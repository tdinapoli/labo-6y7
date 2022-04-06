/************************************************************************ 
*   File: KYFGLib_Example.c
*   Sample Frame Grabber API application
*
*   KAYA Instruments Ltd.
*************************************************************************/

#include "stdafx.h"

#include "KYFGLib.h"


#if !defined(_countof)
#define _countof(_Array) (sizeof(_Array) / sizeof(_Array[0]))
#endif

#ifdef _MSC_VER
#define PRISIZET "Iu" //https://msdn.microsoft.com/en-us/library/tcxf1dw6%28v=vs.110%29.aspx
#else
#define PRISIZET "zu"
#endif

#ifdef __GNUC__ // _aligned_malloc() implementation for gcc
void* _aligned_malloc(size_t size, size_t alignment)
{
    size_t pageAlign = size % 4096;
    if (pageAlign)
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
int get_printable_char();
int get_printable_char()
{
    int c;
    fflush(stdin);
    do
        c = getchar();
    while (isspace(c));
    return c;
}

#define MINIMAL_CALLBACK // Comment out to obtain and print more information about each frame
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

    // as a minimum, application may want to get pointer to current frame memory and/or its numerical ID
    KYFG_BufferGetInfo(streamBufferHandle,
                       KY_STREAM_BUFFER_INFO_BASE,
                       &pFrameMemory,
                       NULL,
                       NULL);
    KYFG_BufferGetInfo(streamBufferHandle,
                       KY_STREAM_BUFFER_INFO_ID,
                       &frameId,
                       NULL,
                       NULL);

    printf(//"\n" // Uncomment to print on new line each time
           "\rGood callback stream's buffer handle:%" PRISTREAM_BUFFER_HANDLE ", ID:%02" PRIu32, streamBufferHandle, frameId);

    // additionaly the following information can be obtained:
    #ifndef MINIMAL_CALLBACK
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

    printf(", timeStamp: %" PRIu64 ", instantFps: %f        ", timeStamp, instantFps);

    #endif //#ifndef MINIMAL_CALLBACK
}

#define MAXBOARDS 4
FGHANDLE handle[MAXBOARDS];

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

    if ((handle[grabberIndex] = KYFG_Open(grabberIndex)) != -1) // connect to selected device
    {
        printf("Good connection to grabber #%d, handle=%X\n", grabberIndex, handle[grabberIndex] );
        return 0;
    }
    else
    {
        printf("Could not connect to grabber #%d\n", grabberIndex);
        get_printable_char();
        return -1;
    }
}

int infosize = 0;
void closeGrabber()
{
    int grabberIndex = 0;
    for (grabberIndex = 0; grabberIndex < infosize; grabberIndex++)
    {
        if (INVALID_FGHANDLE != handle[grabberIndex])
        {
            if (FGSTATUS_OK != KYFG_Close(handle[grabberIndex])) // Close the selected device and unregisters all associated routines
            {
                printf("wasn't able to close grabber #%d\n", grabberIndex);
            }
        }
        else
        {
            printf("grabber #%d wasn't open\n", grabberIndex);
        }
    }
}

int main()
{
    int grabberIndex = 0, deviceIndex; 
    int cameraIndex = 0;
    STREAM_HANDLE streamHandle = INVALID_STREAMHANDLE;
    CAMHANDLE camHandleArray[MAXBOARDS][KY_MAX_CAMERAS];        // there are maximum KY_MAX_CAMERAS cameras
    int detectedCameras[MAXBOARDS];
    char c = 0;
    int bLoopInProgress = 0;
    KYFGLib_InitParameters kyInit;

    // Comment out the folowing #define to see how acquisition buffers can be allocated by user
    #define FGLIB_ALLOCATED_BUFFERS
    #ifndef FGLIB_ALLOCATED_BUFFERS
    STREAM_BUFFER_HANDLE streamBufferHandle[16] = { 0 };
    size_t frameDataSize, frameDataAligment;
    int i;
    #endif

    memset(&kyInit, 0, sizeof(kyInit));
    kyInit.version = 1;

    if (FGSTATUS_OK != KYFGLib_Initialize(&kyInit))
    {
        printf("Library initialization failed \n ");
        return 1;
    }

    for(deviceIndex = 0; deviceIndex < MAXBOARDS; deviceIndex++)
    {
        handle[deviceIndex] = INVALID_FGHANDLE;
    }


    KY_DeviceScan(&infosize); // Retrieve the number of virtual and hardware devices connected to PC
    printf("Number of devices found: %d\n", infosize);

    for(deviceIndex = 0; deviceIndex < infosize; deviceIndex++)
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
        if (!bLoopInProgress)
        {
            if (c != '\n')
            {
                printf("\nEnter choice: ([0-%" PRISIZET "]-select and open grabber)(c-connect to camera)(s-start)(t-stop)(e-exit)\n", _countof(handle) - 1);
            }
            fflush(stdin);
            while ((c = (char)getchar()) == -1);
        }

        if( (c >= '0') && (c < ('0' + _countof(handle)) ) )
        {
            grabberIndex = c - '0';
            printf("Selected grabber #%d\n", grabberIndex);
            connectToGrabber(grabberIndex);
            if (bLoopInProgress)
            {
                c = 'c';
            }
        }
        else if( c == 'c')
        {
            // scan for connected cameras
            int detectionCount = _countof(camHandleArray);
            if(FGSTATUS_OK != KYFG_UpdateCameraList(handle[grabberIndex], camHandleArray[grabberIndex], &detectionCount))
            {
                continue;
            }
            if(detectionCount < 1)
            {
                continue; // no cameras were detected
            }
            detectedCameras[grabberIndex] = detectionCount;
            printf("Found %d cameras.\n", detectedCameras[grabberIndex]);

            // open a connection to chosen camera
            if(FGSTATUS_OK == KYFG_CameraOpen2(camHandleArray[grabberIndex][cameraIndex], 0))
            {
                printf("Camera 0 was connected successfully\n");
            }
            else
            {
                printf("Camera isn't connected\n");
                continue;
            }

            if (bLoopInProgress)
            {
                KYFG_CameraClose(camHandleArray[grabberIndex][cameraIndex]);
                closeGrabber();
                c = '0' + (char)grabberIndex;
                continue;
            }

//            int cameraSelector = KYFG_GetGrabberValueInt(handle[grabberIndex], "CameraSelector");
//            printf("CameraSelector: %d.\n", cameraSelector);

            KYFG_SetCameraValueInt(camHandleArray[grabberIndex][cameraIndex], "Width", 640); // set camera width 
            KYFG_SetCameraValueInt(camHandleArray[grabberIndex][cameraIndex], "Height", 480); // set camera height
            KYFG_SetCameraValueEnum_ByValueName(camHandleArray[grabberIndex][cameraIndex], "PixelFormat", "Mono8"); // set camera pixel format

            KYFG_SetGrabberValueInt(handle[grabberIndex], "CameraSelector", 1 - cameraIndex);
            KYFG_SetGrabberValueInt(camHandleArray[grabberIndex][cameraIndex], "Width", 640);

            #ifdef FGLIB_ALLOCATED_BUFFERS
            #pragma message("Building with KYFGLib allocated buffers")
            // let KYFGLib allocate acquisition buffers 
            if(FGSTATUS_OK != KYFG_StreamCreateAndAlloc(camHandleArray[grabberIndex][cameraIndex], &streamHandle , 16, 0))
            {
                printf("Failed to allocate buffer.\n");
            }

            KYFG_StreamBufferCallbackRegister(streamHandle, Stream_callback_func, NULL);

            #else // Advanced example - custom allocation of acquisition buffers:
            
            #pragma message("Building with user allocated buffers")

            // Create stream
            KYFG_StreamCreate(camHandleArray[grabberIndex][cameraIndex], &streamHandle, 0);

            // Retrieve information about required frame buffer size and alignment 
            KYFG_StreamGetInfo(streamHandle,
                               KY_STREAM_INFO_PAYLOAD_SIZE,
                               &frameDataSize,
                               NULL, NULL);
            KYFG_StreamGetInfo(streamHandle,
                               KY_STREAM_INFO_BUF_ALIGNMENT,
                               &frameDataAligment,
                               NULL, NULL);

            // allocate required amount of frames and announce them to the KYFGLib
            for (i = 0; i < _countof(streamBufferHandle); i++)
            {
                void * pBuffer = _aligned_malloc(frameDataSize, frameDataAligment);
                KYFG_BufferAnnounce(streamHandle,
                                    pBuffer,
                                    frameDataSize,
                                    NULL,
                                    &streamBufferHandle[i]);
            }

            // Link all frames into a cyclic buffer
            KYFG_StreamLinkFramesContinuously(streamHandle);

            #endif // Advanced example - custom allocation of acquisition buffers:


        }
        else if(c == 't')
        {
            KYFG_CameraStop(camHandleArray[grabberIndex][cameraIndex]);
        }
        else if (c == 's')
        {
            if(streamHandle == 0)
            {
            printf("Stream handle is not valid.\n");
            }
            else
            {
                KYFG_CameraStart(camHandleArray[grabberIndex][cameraIndex], streamHandle, 0);
            }
        }
        else if (c == 'l')
        {
            bLoopInProgress = 1;
            c = 'c';
        }
    }
    printf("\nExiting...\n");

    closeGrabber();

    printf("Press any key to exit");
    getchar();
    return 0;
}

