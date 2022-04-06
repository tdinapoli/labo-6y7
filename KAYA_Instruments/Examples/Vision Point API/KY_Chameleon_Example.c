/************************************************************************ 
*	File: KY_Simulation_Example.c
*	Sample Chameleon Camera simulator API application
*
*	KAYA Instruments Ltd.
*************************************************************************/

#include "stdafx.h"

#include "KYFGLib.h"

#if !defined(_countof)
#define _countof(_Array) (sizeof(_Array) / sizeof(_Array[0]))
#endif


#ifdef UNUSED
#elif defined(__GNUC__)
# define UNUSED(x) UNUSED_ ## x __attribute__((unused))
#elif defined(__LCLINT__)
# define UNUSED(x) /*@unused@*/ x
#endif

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


static void* rawBuffers[8];
static KYBOOL bufferIsReplaced[8];
static const int FRAMES_COUNT = sizeof(rawBuffers)/sizeof(rawBuffers[0]);
static CAMHANDLE cameraHandle = INVALID_CAMHANDLE;
static STREAM_HANDLE cameraStreamHandle = INVALID_STREAMHANDLE;
static unsigned int	frames_sent = 0;// Total number of frames sent


void LoadRawFile(char* rawFilePath, int frameIndex)
{
    FILE* file;
    size_t frame_size = 0;
    size_t read_size = 0;

    if ((file = fopen(rawFilePath, "rb")) == NULL)
    {
        printf("Couldn't open file %s\n\r", rawFilePath);
        return;
    }
    fseek(file, 0, SEEK_END); // seek end of binary file
    frame_size = ftell(file); // give current position
    rewind(file);             // get back to the beginning of the file

    rawBuffers[frameIndex] = malloc(frame_size);
    if (NULL == rawBuffers[frameIndex])
    {
        printf("Couldn't allocate memory to read file %s\n\r", rawFilePath);
        return;
    }
    read_size = fread(rawBuffers[frameIndex], 1, frame_size, file);
    if (read_size != frame_size)
    {
        printf("Failed to read %zd bytes from file %s\n\r", frame_size, rawFilePath);
    }

    fclose(file);
}

void PrepareRawBuffers()
{
    int i;
    char fileName[260];
    for (i = 0; i < FRAMES_COUNT; i++)
    {
        sprintf(fileName, "../../Data/%d.raw", i);
        LoadRawFile(fileName, i);
        bufferIsReplaced[i] = KYFALSE;
    }
}


void StartGeneration()
{
    frames_sent = 0; // Reset frames counter when starting new session

    printf("Creating stream...\n");
    if (FGSTATUS_OK == KYFG_StreamCreateAndAlloc(cameraHandle,
                                                 &cameraStreamHandle,
                                                 FRAMES_COUNT,
                                                 0))// streamIndex currently must be 0
    {
        printf("Stream was created successfuly\n");
    }
    else
    {
        printf("Stream creation has failed\n");
        printf("Press to exit");
        get_printable_char();
        return;
    }

    printf("Loading File...\n");
    if (FGSTATUS_OK == KYFG_LoadFileData(cameraStreamHandle, "../../Data/example_rgb_8bit.bmp", "bmp", FRAMES_COUNT)) // load an image(s) file to the simulator
    {
        printf("File was loaded successfuly\n");
    }
    else
    {
        printf("File load has failed\n");
        printf("Press to exit");
        get_printable_char();
        return;
    }

    KYFG_CameraStart(cameraHandle, cameraStreamHandle, 0);	// Starts the simulation
}

void KYDeviceEventCallBackImpl(void* userContext, KYDEVICE_EVENT* pEvent)
{
    userContext; // suppress warning
  switch(pEvent->eventId)
  {
      case KYDEVICE_EVENT_CAMERA_START_REQUEST:
      {
        CAMHANDLE eventCameraHandle = ((KYDEVICE_EVENT_CAMERA_START*)pEvent)->camHandle;
        if (eventCameraHandle == cameraHandle)
        {
            printf("\nDetected remote request to start generation\n");
            StartGeneration();
        }
      }
      break;
  }
}

void CameraCallbackImpl (void* userContext, STREAM_HANDLE streamHandle)
{
    userContext;
    uint32_t    currentIndex;   // Indicates the Nth frame that was currently send.
    void    *ptr;               // Pointer to current frame the data
    int64_t size;               // Size of each frame in bytes

    if (!streamHandle)
    {
        // callback with streamHandle == 0 indicates that stream generation has stopped
        // any data retrieved using this handle (frame index, buffer pointer, etc.) won't be valid
        printf("\nStream generation stopped\n");
        return;
    }

    currentIndex = KYFG_StreamGetFrameIndex(streamHandle);

    frames_sent++;
    printf("\rCallback call N %d, frame N %u                      ", frames_sent, currentIndex);

    ptr = KYFG_StreamGetPtr(streamHandle, currentIndex);
    size = KYFG_StreamGetSize(streamHandle);
    // after frame has been generated replace its memory with a different raw content:
    if (frames_sent > 10 // start "on-the-fly" buffer replacement after x frames were sent - just as an example...
        &&
        bufferIsReplaced[currentIndex] == KYFALSE)
    {
        memcpy(ptr, rawBuffers[currentIndex], (size_t)size);
        bufferIsReplaced[currentIndex] = KYTRUE;
    }
}

int main()
{
    FGHANDLE deviceHandle = 0;
    CAMHANDLE cameraHandles[KY_MAX_CAMERAS];
    int detectedCameras;
    FGSTATUS status;
    int infosize = 0;
    int infoIndex = -1;
    int deviceIndex;
    char c = 0;

    PrepareRawBuffers();

    KY_DeviceScan(&infosize);	// Retrieve the number of virtual and hardware devices connected to PC
    printf("Number of devices found: %d\n", infosize);

    for (deviceIndex = 0; deviceIndex < infosize; deviceIndex++)
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

    if (infosize > 0)
    {
        do
        {
            printf("\nEnter which device to connect (0-%d): ", infosize - 1);
            infoIndex = get_printable_char();
            infoIndex = infoIndex - '0'; // translate user entered char to int number

        }
        while (!(infoIndex >= 0 && infoIndex <= infosize - 1));

        // Try to connect to selected device that must br simulator
        KY_DEVICE_INFO deviceInfo;
        memset(&deviceInfo, 0, sizeof(KY_DEVICE_INFO));
        deviceInfo.version = KY_MAX_DEVICE_INFO_VERSION;
        if (FGSTATUS_OK != KY_DeviceInfo(infoIndex, &deviceInfo))
        {
            printf("wasn't able to retrive information from device #%d\n", deviceIndex);
            return -1;
        }
        if (0 == (KY_DEVICE_STREAM_GENERATOR & deviceInfo.m_Flags))
        {
            printf("sorry, select device #%d is not a Chameleon Simulator\n", infoIndex);
            printf("Press any key to exit");
            getchar();
            return -1;
        }

        if ((deviceHandle = KYFG_OpenEx(infoIndex, 0)) != INVALID_FGHANDLE)	// open the selected device
        {
            printf("Good connection, deviceHandle == 0x%X\n", deviceHandle);
        }
        else
        {
            printf("Not connected\n");
            get_printable_char();
            return -1;
        }
    }
    else
    {
        printf("Exiting\n");
        get_printable_char();
        return -1;
    }

    detectedCameras = _countof(cameraHandles);
    status = KYFG_UpdateCameraList(deviceHandle, cameraHandles, &detectedCameras);
    if (FGSTATUS_OK != status)
    {
        printf("Camera scan failed\n");
        get_printable_char();
        return -1;
    }

    // Currently only one camera is implemented by Chameleon Simulator
    if (detectedCameras < 1)
    {
        printf("No camera detected\n");
        get_printable_char();
        return 0;
    }
    // Also, in this example we are working with only first camera
    cameraHandle = cameraHandles[0];
    status = KYFG_CameraOpen2(cameraHandle, 0); // if 'xml_file_path' is 0 then only internal XML will be used providing minimal set of mandatory camera parameters
    if ( FGSTATUS_OK != status)
    {
        printf("Failed to open camera, status 0x%X\n", status);
        get_printable_char();
        return -1;
    }

    // Register callback function for the camera
    status = KYFG_CameraCallbackRegister(cameraHandle, CameraCallbackImpl, 0);
    if ( FGSTATUS_OK != status)
    {
        printf("Failed to register camera callback, status 0x%X\n", status);
        get_printable_char();
        return -1;
    }

    // Register callback function for device
    status = KYDeviceEventCallBackRegister(deviceHandle, KYDeviceEventCallBackImpl, 0);
    if ( FGSTATUS_OK != status)
    {
        printf("Failed to register device callback, status 0x%X\n", status);
        get_printable_char();
        return -1;
    }

    // Optional step - re-load the selected XML file 
    /*
    if(KYFG_LoadCameraConfiguration(cameraHandle, "../Data/KAYA_Chameleon.xml", 0) != FGSTATUS_OK) // KAYA additional file values - not implemented yet, second parameter must be 0
    {
        printf("Load of camera configuration file failed\n");
        printf("Press to exit");
        get_printable_char();
        return 0;
    }
    */

    // Setting the camera parameters
    KYFG_SetCameraValueInt(cameraHandle, "Width", 640);
    KYFG_SetCameraValueInt(cameraHandle, "Height", 480);
    KYFG_SetCameraValueEnum_ByValueName(cameraHandle, "PixelFormat", "RGB8");
    KYFG_SetCameraValueFloat(cameraHandle, "AcquisitionFrameRate", 60.0);

    while (c != 'e')
    {
        printf("\nEnter choice: (s-start)(t-stop)(e-exit)\n");
        while ((c = (char)get_printable_char()) == -1);

        if (c == 't')
        {
            KYFG_CameraStop(cameraHandle); // Stops the simulation
        }
        else if (c == 's')
        {
            StartGeneration();
        }
    }
    printf("\nExiting...\n");

    if (KYFG_Close(deviceHandle) != FGSTATUS_OK)	// Close the selected device and releases all associated resources - cameraHandle, cameraStreamHandle; also unregisteres callbacks
    {
        printf("wasn't able to close correctly\n");
    }

    printf("Press any key to exit");
    getchar();
    return 0;
}

