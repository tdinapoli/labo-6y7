/************************************************************************ 
*   File: KYFGLib_Example.cpp
*   Sample Frame Grabber API application
*
*   KAYA Instruments Ltd.
*************************************************************************/

#include "stdafx.h"

#include "KYFGLib.h"


#if !defined(_countof)
#define _countof(_Array) (sizeof(_Array) / sizeof(_Array[0]))
#endif

#define MAXBOARDS 4
FGHANDLE handle[MAXBOARDS];
unsigned int currentGrabberIndex;
int printCxp2Events = 0;
int printHeartbeats = 0;

#ifdef __GNUC__ // _aligned_malloc() implementation for gcc
void* _aligned_malloc(size_t size, size_t alignment)
{
    size_t pageAlign = size % 4096;
    if(pageAlign)
    {
        size += 4096 - pageAlign;
    }

#if(GCC_VERSION <= 40407)
    void * memptr = 0;
    posix_memalign(&memptr, alignment, size);
    return memptr;
#else
    return aligned_alloc(alignment, size);
#endif
}
#endif // #ifdef __GNUC__

// Helper function to get single printable char as user input
int get_printable_char()
{
    int c;
    fflush(stdin);
    do
        c = getchar();
    while (isspace(c));
    return c;
}

//#define FGLIB_ALLOCATED_BUFFERS // Uncomment this #definition to use buffers allocated by KYFGLib
#define MINIMAL_CALLBACK

void Stream_callback_func(STREAM_BUFFER_HANDLE streamBufferHandle, void* userContext)
{
    unsigned char* pFrameMemory = 0;
    uint32_t frameId = 0;
#ifndef MINIMAL_CALLBACK
    size_t bufferSize = 0;
    void* pUserContext;
    uint64_t timeStamp;
    double instantFps;
#endif
    userContext; // suppress warning

    if (!streamBufferHandle)
    {
        // this callback indicates that acquisition has stopped
        return;
    }
            
    // as a minimum, application needs to get pointer to current frame memory
    KYFG_BufferGetInfo(streamBufferHandle, 
                        KY_STREAM_BUFFER_INFO_BASE, 
                        &pFrameMemory, 
                        NULL, 
                        NULL);

    // additionaly the following information can be obtained:
#ifndef MINIMAL_CALLBACK
    KYFG_BufferGetInfo(streamBufferHandle, 
                        KY_STREAM_BUFFER_INFO_ID, 
                        &frameId, 
                        NULL, 
                        NULL);

    KYFG_BufferGetInfo(streamBufferHandle, 
                        KY_STREAM_BUFFER_INFO_SIZE, 
                        &bufferSize, 
                        NULL, 
                        NULL);

    KYFG_BufferGetInfo(streamBufferHandle, 
                        KY_STREAM_BUFFER_INFO_USER_PTR, 
                        &pUserContext, 
                        NULL, 
                        NULL);

    KYFG_BufferGetInfo(streamBufferHandle, 
                        KY_STREAM_BUFFER_INFO_TIMESTAMP, 
                        &timeStamp, 
                        NULL, 
                        NULL);

    KYFG_BufferGetInfo(streamBufferHandle, 
                        KY_STREAM_BUFFER_INFO_INSTANTFPS, 
                        &instantFps, 
                        NULL, 
                        NULL);

#endif
    printf(//"\n" // Uncomment to print on new line each time
            "\rGood callback stream's buffer handle:%" PRISTREAM_BUFFER_HANDLE ", ID:%d", streamBufferHandle, frameId);

    // return stream buffer to input queue
    KYFG_BufferToQueue(streamBufferHandle, KY_ACQ_QUEUE_INPUT);
}

void ProcessHeartbeatEvent(KYDEVICE_EVENT_CXP2_HEARTBEAT* pEventHeartbeat)
{
    if (!printHeartbeats)
    {
        return;
    }
    printf("Received KYDEVICE_EVENT_CXP2_HEARTBEAT: cameraTime=%" PRIu64 "\n", pEventHeartbeat->heartBeat.cameraTime);
}

void ProcessCxp2Event(KYDEVICE_EVENT_CXP2_EVENT* pEventCXP2Event)
{
    if (!printCxp2Events)
    {
        return;
    }
    printf("Received KYDEVICE_EVENT_CXP2_EVENT: tag=0x%" PRIu8 "\n", pEventCXP2Event->cxp2Event.tag);
}

void KYDeviceEventCallBackImpl(void* userContext, KYDEVICE_EVENT* pEvent)
{
    userContext; // suppress warning
    switch (pEvent->eventId)
    {
        // Please note that the following events will be recieved only if camera is working in CXP 2 mode. For details please reffer CXP 2 standards
        case KYDEVICE_EVENT_CXP2_HEARTBEAT_ID:
            ProcessHeartbeatEvent((KYDEVICE_EVENT_CXP2_HEARTBEAT*)pEvent);
            break;
        case KYDEVICE_EVENT_CXP2_EVENT_ID:
            ProcessCxp2Event((KYDEVICE_EVENT_CXP2_EVENT*)pEvent);
            break;
    }
}

int connectToGrabber(unsigned int grabberIndex)
{
    KY_DEVICE_INFO deviceInfo;
    memset(&deviceInfo, 0, sizeof(KY_DEVICE_INFO));
    deviceInfo.version = KY_MAX_DEVICE_INFO_VERSION;
    if (FGSTATUS_OK != KY_DeviceInfo(grabberIndex, &deviceInfo))
    {
        printf("wasn't able to retrive information from device #%d\n", grabberIndex);
        return -1;
    }
    if (0 == (KY_DEVICE_STREAM_GRABBER & deviceInfo.m_Flags))
    {
        printf("sorry, select device #%d is not a grabber\n", grabberIndex);
        return -1;
    }

    int64_t dmadQueuedBufferCapable;

    if ((handle[grabberIndex] = KYFG_Open(grabberIndex)) != -1)     // connect to selected device
    {
        printf("Good connection to grabber #%d, handle=%X\n", grabberIndex, handle[grabberIndex] );
    }
    else
    {
        printf("Could not connect to grabber #%d\n", grabberIndex);
        get_printable_char();
        return -1;
    }

    dmadQueuedBufferCapable = KYFG_GetGrabberValueInt(handle[grabberIndex], DEVICE_QUEUED_BUFFERS_SUPPORTED);
    if (1 != dmadQueuedBufferCapable)
    {
        printf("grabber #%d does not support queued buffers\n", grabberIndex);
        get_printable_char();
        return -1;
    }

    currentGrabberIndex = grabberIndex;

    // OPTIONALY register grabber's event callback function
    if (FGSTATUS_OK != KYDeviceEventCallBackRegister(handle[grabberIndex], KYDeviceEventCallBackImpl, 0))
    {
        printf("Warning: KYDeviceEventCallBackRegister() failed \n ");
    }
    else
    {
        printf("KYDeviceEventCallBackImpl() registered, enter 'v' to turn event prints on and off\n ");
    }

    return 0;
}

CAMHANDLE camHandleArray[MAXBOARDS][KY_MAX_CAMERAS];        // there are maximum KY_MAX_CAMERAS cameras
STREAM_HANDLE cameraStreamHandle = INVALID_STREAMHANDLE;
size_t frameDataSize, frameDataAligment;
STREAM_BUFFER_HANDLE streamBufferHandle[16] = {0};
int iFrame;
double instantFps;

int startCamera(unsigned int grabberIndex, unsigned int cameraIndex)
{
    // put all buffers to input queue
    KYFG_BufferQueueAll(cameraStreamHandle, KY_ACQ_QUEUE_UNQUEUED, KY_ACQ_QUEUE_INPUT);    

    // start acquisition
    KYFG_CameraStart(camHandleArray[grabberIndex][cameraIndex], cameraStreamHandle, 0);

    return 0;
}


int main()
{
    int infosize = 0, deviceIndex;
    int grabberIndex = 0, cameraIndex = 0;
    int detectedCameras[MAXBOARDS];
    char c = 0;
    KYFGLib_InitParameters kyInit;

    kyInit.version = 2;
    kyInit.concurrency_mode = 0;
    kyInit.logging_mode = 0;
    kyInit.noVideoStreamProcess = KYFALSE;
    if (FGSTATUS_OK != KYFGLib_Initialize(&kyInit))
    {
        printf("Library initialization failed \n ");
        return 1;
    }

    for(deviceIndex = 0; deviceIndex < MAXBOARDS; deviceIndex++)
    {
        handle[deviceIndex] = INVALID_FGHANDLE;
    }


    KY_DeviceScan(&infosize);	// First scan for device to retrieve the number of virtual and hardware devices connected to PC
    printf("Number of scan results: %d\n", infosize);
    for(deviceIndex=0; deviceIndex<infosize; deviceIndex++)
    {
        KY_DEVICE_INFO deviceInfo;
        memset(&deviceInfo, 0, sizeof(KY_DEVICE_INFO));
        deviceInfo.version = KY_MAX_DEVICE_INFO_VERSION;
        if (FGSTATUS_OK != KY_DeviceInfo(deviceIndex, &deviceInfo))
        {
            printf("wasn't able to retrive information from device #%d\n", deviceIndex);
            continue;
        }
        printf("[%d] %s on PCI slot {%d:%d:%d}: Protocol 0x%X, Generation %d\n", deviceIndex,
               deviceInfo.szDeviceDisplayName,
               deviceInfo.nBus, deviceInfo.nSlot, deviceInfo.nFunction,
               deviceInfo.m_Protocol, deviceInfo.DeviceGeneration);
    }

    c = 'x';
    while (c != 'e')
    {
        if (c != '\n')
        {
            printf("\nEnter choice: ([0-4]-select grabber)(o-open frabber)(c-connect to camera)(s-start)(t-stop)(e-exit)(v - print CXP2 events)(h-print CXP2 heartbeats)\n");
        }
        fflush(stdin);
        while ((c = (char)getchar()) == -1);

        if( c >= '0' && c <= ('0' + _countof(handle) - 1) )
        {
            grabberIndex = c - '0';
            printf("Selected grabber #%d\n", grabberIndex);
        }
        else if( c == 'c')
        {
            // scan for connected cameras
            int detectionCount = _countof(camHandleArray);
            if (FGSTATUS_OK != KYFG_UpdateCameraList(handle[grabberIndex], camHandleArray[grabberIndex], &detectionCount))
            {
                continue;   // no cameras were detected
            }
            detectedCameras[grabberIndex] = detectionCount;
            // open a connection to chosen camera
            if(FGSTATUS_OK == KYFG_CameraOpen2(camHandleArray[grabberIndex][cameraIndex], NULL))
            {
                printf("Camera 0 was connected successfully\n");
            }
            else
            {
                printf("Camera isn't connected\n");
                continue;
            }
            
            //… // update camera/grabber buffer dimensions parameters before stream creation
            KYFG_SetCameraValueInt(camHandleArray[grabberIndex][cameraIndex], "Width", 640);                        // set camera width 
            KYFG_SetCameraValueInt(camHandleArray[grabberIndex][cameraIndex], "Height", 480);                       // set camera height
            KYFG_SetCameraValueEnum_ByValueName(camHandleArray[grabberIndex][cameraIndex], "PixelFormat", "Mono8"); // set camera pixel format

            // create stream and assign appropriate runtime acquisition callback function
            KYFG_StreamCreate(camHandleArray[grabberIndex][cameraIndex], &cameraStreamHandle, 0);
            KYFG_StreamBufferCallbackRegister(cameraStreamHandle, Stream_callback_func, NULL);
       
            // Retrieve information about required frame buffer size and alignment 
            KYFG_StreamGetInfo(cameraStreamHandle, 
                                KY_STREAM_INFO_PAYLOAD_SIZE, 
                                &frameDataSize, 
                                NULL, NULL);

            KYFG_StreamGetInfo(cameraStreamHandle,
                                KY_STREAM_INFO_BUF_ALIGNMENT, 
                                &frameDataAligment, 
                                NULL, NULL);

            // allocate memory for desired number of frame buffers
            for (iFrame = 0; iFrame < _countof(streamBufferHandle); iFrame++)
            {
#ifdef FGLIB_ALLOCATED_BUFFERS
#pragma message("Building with KYFGLib allocated buffers")
                KYFG_BufferAllocAndAnnounce(cameraStreamHandle,
                    frameDataSize,
                    NULL,
                    &streamBufferHandle[iFrame]);
#else
#pragma message("Building with user allocated buffers")
                void * pBuffer = _aligned_malloc(frameDataSize, frameDataAligment);
                KYFG_BufferAnnounce(cameraStreamHandle,
                                    pBuffer, 
                                    frameDataSize, 
                                    NULL, 
                                    &streamBufferHandle[iFrame]);
#endif 

            }//for (iFrame = 0; iFrame < _countof(streamBufferHandle); iFrame++)
        }
        else if(c == 'o')
        {
            connectToGrabber(grabberIndex);
        }
        else if(c == 't')
        {
            // Optional: collect some statistic before stopping
            int64_t RXFrameCounter = KYFG_GetGrabberValueInt(camHandleArray[grabberIndex][cameraIndex], "RXFrameCounter");
            int64_t DropFrameCounter = KYFG_GetGrabberValueInt(camHandleArray[grabberIndex][cameraIndex], "DropFrameCounter");
            int64_t RXPacketCounter = KYFG_GetGrabberValueInt(camHandleArray[grabberIndex][cameraIndex], "RXPacketCounter");
            int64_t DropPacketCounter = KYFG_GetGrabberValueInt(camHandleArray[grabberIndex][cameraIndex], "DropPacketCounter");
            KYFG_StreamGetInfo(cameraStreamHandle,
                               KY_STREAM_INFO_INSTANTFPS,
                               &instantFps,
                               NULL, NULL);

            printf("\npre-stop statistic:\n");
            printf("RXFrameCounter: %" PRId64 "\n", RXFrameCounter);
            printf("DropFrameCounter: %" PRId64 "\n", DropFrameCounter);
            printf("RXPacketCounter: %" PRId64 "\n", RXPacketCounter);
            printf("DropPacketCounter: %" PRId64 "\n", DropPacketCounter);
            printf("instantFps: %f\n", instantFps);

            //////////////////////////////////////////
            KYFG_CameraStop(camHandleArray[grabberIndex][cameraIndex]);
        }
        else if (c == 's')
        {
            startCamera(grabberIndex, cameraIndex);
        }
        else if (c == 'v')
        {
            printCxp2Events = 1 - printCxp2Events; // toggle 'printCxp2Events' between 0 and 1
        }
        else if (c == 'h')
        {
            printHeartbeats = 1 - printHeartbeats; // toggle 'printHeartbeats' between 0 and 1
        }

    }
    printf("\nExiting...\n");

    for (grabberIndex = 0; grabberIndex < infosize; grabberIndex++)
    {
        if(INVALID_FGHANDLE != handle[grabberIndex])
        {
            if(FGSTATUS_OK!= KYFG_Close(handle[grabberIndex]))  // Close the selected device and unregisters all associated routines
            {
                printf("wasn't able to close grabber #%d\n", grabberIndex);
            }
        }
        else
        {
            printf("grabber #%d wasn't open\n", grabberIndex);
        }
    }

    printf("Press any key to exit");
    getchar();
    return 0;
}
