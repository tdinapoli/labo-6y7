#ifndef KYFG_LIB_H_
#define KYFG_LIB_H_

#include "KYFGLib_defines.h"
#include "KYFGLibVersion.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief   Initializes KYFGLib library providing various parameters.
 * @details An optional call before KYFGScan(). 
 *          For details please refer to 'KYFGLib_InitParameters' structure description
 * @param   [in] pKYFGLib_InitParameters  - library initialization parameters 
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFGLib_Initialize(KYFGLib_InitParameters* pKYFGLib_InitParameters);

// <--- Connection functions --->

/**
 * @brief   Scan for available devices
 * @param   [out] pDetectedDevices - pointer to 'int' that will be set to number of available devices
 * @return  FGSTATUS - Error code of function execution status
 * @par Example
 * @include KY_DeviceScan.c
 */
KY_API FGSTATUS KY_DeviceScan(int *pDetectedDevices);


/**
 * @brief   Scan for available devices
 * @param   [out] pids_info - pointer to <pid> array of scanned devices
 *                             null - will retrieve only the number of found devices (when this is used, two function calls needed in order to open the device)
 * @param   [in] count - number of devices assigned to pids_info array (assume pids_info array is valid)
 * @return  int - number of found devices, maximum MAX_INFO
 */
KY_DEPRECATED(KAYA_API int KYFG_Scan(uint32_t *pids_info, int count), "Function 'KYFG_Scan()' is deprecated, please use function 'KY_DeviceScan()'.");


/**
 * @brief   Fills KY_DEVICE_INFO struct with relevant info
 * @param   [in] index - index of Frame Grabber device
 * @param   [out] pInfo - pointer to struct with device information
 * @return  FGSTATUS - Error code of function execution status
 */
KY_API FGSTATUS KY_DeviceInfo(int index, KY_DEVICE_INFO* pInfo);


/**
 * @brief   Connect to specific Frame Grabber without loading a project
 * @param   [in] index - device index from scan result
 * @return  FGHANDLE - a handle to the opened device
 */
KAYA_API FGHANDLE     KYFG_Open(int index);


/**
 * @brief   Connect to specific Frame Grabber and optionally load a project
 * @param   [in] index - device index from scan result
 * @param   [in] projectFile - full path of a project file with saved values, can be null
 * @return  FGHANDLE - a handle to the opened device
 */
KAYA_API FGHANDLE    KYFG_OpenEx(int index, const char* projectFile);

KY_API const char* KY_DeviceDisplayName(int index);

/**
 * @brief   Close the specified device
 * @param   [in] handle - a handle to the opened device
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS    KYFG_Close(FGHANDLE handle);

#pragma pack(push, 1)
typedef struct _KY_SOFTWARE_VERSION
{
    uint16_t struct_version; // Must be set to 0 or 1 before calling KY_GetSoftwareVersion() function
    uint16_t Major;
    uint16_t Minor;
    uint16_t SubMinor;

    // since version 1 of this structure:
    uint16_t Beta; // Non-zero value indicates a "Beta build"
    uint16_t RC;   // Non-zero value indicates a "Release Candidate build"
}KY_SOFTWARE_VERSION;
#pragma pack(pop)

/**
 * @brief   Retrieve current KAYA software version
 * @param   [in, out] pVersion - pointer to struct with versions information
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS     KY_GetSoftwareVersion(KY_SOFTWARE_VERSION* pVersion);


#define KYFG_AUX_MESSAGE_ID_IO_CONTROLLER 11

#pragma pack(push, 1)
typedef struct _KYFG_IO_AUX_DATA
{
    uint64_t masked_data;
    uint64_t timestamp;
}KYFG_IO_AUX_DATA;
#pragma pack(pop)

#define KYFG_IO_CONTROLLER_MASKED_IO(masked_data) ((masked_data) & 0xFFFFFFFFFF)
#define KYFG_IO_CONTROLLER_MASKED_ENCODERS(masked_data) (((masked_data) >> 40) & 0xF)
#define KYFG_IO_CONTROLLER_MASKED_TIMERS(masked_data) (((masked_data) >> 44) & 0xFF)
#define KYFG_IO_CONTROLLER_MASKED_CAMERA_TRIGGERS(masked_data) (((masked_data) >> 52) & 0xFF)
#define KYFG_IO_CONTROLLER_MASKED_TRIGGERS(masked_data) (((masked_data) >> 60) & 0xF)


#pragma pack(push, 1)
typedef struct _KYFG_FRAME_AUX_DATA
{
    uint32_t sequence_number;
    uint64_t timestamp;
    uint32_t reserved;
}KYFG_FRAME_AUX_DATA;
#pragma pack(pop)


#define AUX_DATA_MAX_SIZE (4*sizeof(uint32_t))
#pragma pack(push, 1)
typedef struct _KYFG_AUX_DATA
{
    uint32_t messageID;
    KYBOOL   reserved;

    size_t   dataSize;
    union
    {
        uint8_t              data[AUX_DATA_MAX_SIZE];
        KYFG_IO_AUX_DATA     io_data;                    // messageID == KYFG_AUX_MESSAGE_ID_IO_CONTROLLER
        KYFG_FRAME_AUX_DATA  frame_data;
    } u_data;
}KYFG_AUX_DATA;
#pragma pack(pop)

typedef void (KYFG_CALLCONV *FGAuxDataCallback)(KYFG_AUX_DATA* pData, void* context);

/**
 * @brief   Register run-time callback for receiving auxiliary data
 * @param   [in] handle - handle to connected Frame Grabber
 * @param   [in] userFunc - pointer to the callback function
 * @param   [in] userContext - pointer to the data to be sent back with callback
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS    KYFG_AuxDataCallbackRegister(FGHANDLE handle, FGAuxDataCallback userFunc, void* userContext);


/**
 * @brief   Unregister run-time auxiliary data callback
 * @param   [in] handle - handle to the connected device 
 * @param   [in] userFunc - pointer to the callback function to unregister, if NULL is passed, all registered callbacks will be unregistered
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS    KYFG_AuxDataCallbackUnregister(FGHANDLE handle, FGAuxDataCallback userFunc);

typedef void(KYFG_CALLCONV *FGCallback)(BUFFHANDLE buffHandle, void* userContext);

/**
 * @brief   Register run-time callback for the Frame Grabber and all connected cameras
 * @details This API function is deprecated. New software should use functions 'KYFG_CameraCallbackRegister()' or 'KYFG_StreamBufferCallbackRegister()'
 * @param   [in] handle - handle to the connected Frame Grabber
 * @param   [in] userFunc - pointer to the callback function
 * @param   [in] userContext - pointer to the data, to be sent back with callback
 * @return  FGSTATUS - Error code of function execution status
 */
KY_DEPRECATED(KAYA_API FGSTATUS    KYFG_CallbackRegister(FGHANDLE handle, FGCallback userFunc, void* userContext), "Function 'KYFG_CallbackRegister' is deprecated, please use function 'KYFG_CameraCallbackRegister()' or 'KYFG_StreamBufferCallbackRegister()'.");
/**
 * @brief   Unregister run-time callback for the Frame Grabber and all connected cameras
 * @details This API function is deprecated. New software should use functions 'KYFG_CameraCallbackUnregister()' or 'KYFG_StreamBufferCallbackUnregister()'
 * @param   [in] handle - handle to the connected Frame Grabber
 * @param   [in] userFunc - pointer to the callback function
 * @return  FGSTATUS - Error code of function execution status
 */
KY_DEPRECATED(KAYA_API FGSTATUS    KYFG_CallbackUnregister(FGHANDLE handle, FGCallback userFunc), "Function 'KYFG_CallbackUnregister' is deprecated, please use function 'KYFG_CameraCallbackUnregister()' or 'KYFG_StreamBufferCallbackUnregister()'.");


// Callback prototype and registration of runtime callback function for specific camera
typedef void(KYFG_CALLCONV *CameraCallback)(void* userContext, STREAM_HANDLE streamHandle);
KAYA_API FGSTATUS    KYFG_CameraCallbackRegister(CAMHANDLE camHandle, CameraCallback userFunc, void* userContext);
KAYA_API FGSTATUS    KYFG_CameraCallbackUnregister(CAMHANDLE camHandle, CameraCallback userFunc);

// Callback prototype and registration of stream callback function for general events and all connected cameras
typedef void(KYFG_CALLCONV *StreamBufferCallback)(STREAM_BUFFER_HANDLE streamBufferHandle, void* userContext);


/**
 * @brief   Register user's run-time callback for video stream
 * @param   [in] streamHandle - handle to a stream
 * @param   [in] userFunc -    pointer to the callback function
 * @param   [in] userContext - user defined pointer to be sent back as callback function argument
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS    KYFG_StreamBufferCallbackRegister(STREAM_HANDLE streamHandle, StreamBufferCallback userFunc, void* userContext);

/**
 * @brief   Unregister run-time callback for video stream
 * @param   [in] streamHandle - handle to a stream
 * @param   [in] userFunc -    pointer to the callback function
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS    KYFG_StreamBufferCallbackUnregister(STREAM_HANDLE streamHandle, StreamBufferCallback userFunc);

/**
 * Generic device callbacks:
 * KYDEVICE_EVENT_CAMERA_START_REQUEST - Device detected a remote request to start transmission on a camera.
 *                                         Currently used only for KAYA Chameleon Simulator when remote Frame Grabber sends request for acquisition start. 
 * KYDEVICE_EVENT_CAMERA_CONNECTION_LOST_ID - Detection of connection loss on a previously detected camera.
 *                                         Currently implemented for CoaXPress and CLHS Frame Grabbers only.  
 *                                         For 10Gige Frame Grabbers this event will not be received from callback event.
 * KYDEVICE_EVENT_SYSTEM_TEMPERATURE_ID - This event is sent when device temperature reached a threshold.
 * KYDEVICE_EVENT_CXP2_HEARTBEAT_ID      - CXP 2.0 Heartbeat packet received from connected camera.
 * KYDEVICE_EVENT_CXP2_EVENT_ID          - CXP 2.0 Event packet received from connected camera.
 * KYDEVICE_EVENT_GENCP_EVENT_ID           GenCP Event message id for CLHS
 * KYDEVICE_EVENT_GIGE_EVENTDATA_ID        EVENTDATA Event message id for 10GigE
 */
typedef enum _KYDEVICE_EVENT_ID
{
    KYDEVICE_EVENT_CAMERA_START_REQUEST = 0,
    KYDEVICE_EVENT_CAMERA_CONNECTION_LOST_ID = 1,
    KYDEVICE_EVENT_SYSTEM_TEMPERATURE_ID = 2,
    KYDEVICE_EVENT_CXP2_HEARTBEAT_ID = 3,
    KYDEVICE_EVENT_CXP2_EVENT_ID = 4,
    KYDEVICE_EVENT_GENCP_EVENT_ID = 5,
    KYDEVICE_EVENT_GIGE_EVENTDATA_ID = 6,
}KYDEVICE_EVENT_ID;

#pragma pack(push, 1)
typedef struct _KYDEVICE_EVENT
{
    KYDEVICE_EVENT_ID eventId;
}KYDEVICE_EVENT;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct _KYDEVICE_EVENT_CAMERA_START
{
    // KYDEVICE_EVENT_CAMERA_START derived from KYDEVICE_EVENT:
    KYDEVICE_EVENT deviceEvent;

    // Specific KYDEVICE_EVENT_CAMERA_START members:
    CAMHANDLE camHandle;
}KYDEVICE_EVENT_CAMERA_START;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct _KYDEVICE_EVENT_CAMERA_CONNECTION_LOST
{
    // KYDEVICE_EVENT_CAMERA_CONNECTION_LOST derived from KYDEVICE_EVENT:
    KYDEVICE_EVENT deviceEvent;

    // Specific KYDEVICE_EVENT_CAMERA_CONNECTION_LOST members:
    CAMHANDLE camHandle;
    size_t    iDeviceLink;
    size_t    iCameraLink;
}KYDEVICE_EVENT_CAMERA_CONNECTION_LOST;
#pragma pack(pop)

typedef enum _KYDEVICE_EVENT_SYSTEM_TEMPERATURE_THRESHOLD_ID
{
    KYDEVICE_EVENT_SYSTEM_TEMPERATURE_NORMAL = 0,
    KYDEVICE_EVENT_SYSTEM_TEMPERATURE_WARNING = 1,
    KYDEVICE_EVENT_SYSTEM_TEMPERATURE_CRITICAL = 2,
}KYDEVICE_EVENT_SYSTEM_TEMPERATURE_THRESHOLDS_ID;

#pragma pack(push, 1)
typedef struct _KYDEVICE_EVENT_SYSTEM_TEMPERATURE
{
    // KYDEVICE_EVENT_SYSTEM_TEMPERATURE derived from KYDEVICE_EVENT:
    KYDEVICE_EVENT deviceEvent;

    KYDEVICE_EVENT_SYSTEM_TEMPERATURE_THRESHOLDS_ID temperatureThresholdId;

}KYDEVICE_EVENT_SYSTEM_TEMPERATURE;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct _KYDEVICE_EVENT_CXP2_HEARTBEAT
{
    // KYDEVICE_EVENT_CXP2_HEARTBEAT derived from KYDEVICE_EVENT:
    KYDEVICE_EVENT deviceEvent;

    // Specific KYDEVICE_EVENT_CXP2_HEARTBEAT members:
    CAMHANDLE camHandle;
    KY_CXP2_HEARTBEAT heartBeat;
}KYDEVICE_EVENT_CXP2_HEARTBEAT;
#pragma pack(pop)

#pragma pack(push, 1)
typedef struct _KYDEVICE_EVENT_CXP2_EVENT
{
    // KYDEVICE_EVENT_CXP2_EVENT derived from KYDEVICE_EVENT:
    KYDEVICE_EVENT deviceEvent;

    // Specific KYDEVICE_EVENT_CXP2_EVENT members:
    CAMHANDLE camHandle;
    KY_CXP2_EVENT cxp2Event;
}KYDEVICE_EVENT_CXP2_EVENT;
#pragma pack(pop)

#pragma pack(push, 1)
// used for KYDEVICE_EVENT_GENCP_EVENT_ID
#define KY_GENCP_EVENT_MAX_DATA_SIZE 1024

typedef struct _KYDEVICE_EVENT_GENCP_EVENT
{
    // KYDEVICE_EVENT_GENCP_EVENT derived from KYDEVICE_EVENT:
    KYDEVICE_EVENT deviceEvent;

    // Specific KYDEVICE_EVENT_GENCP_EVENT members:
    int srcDevicePort;
    struct KY_GENCP_EVENT
    {
        uint16_t eventSize;    // Size of event data object in bytes including event_size, event_id, timestamp and optional data.
        uint16_t eventId;      // The event_id is a number identifying an event source.
        uint64_t timestamp;     // 64 bit timestamp value in ns as defined in the timestamp bootstrap register.
        uint8_t data[KY_GENCP_EVENT_MAX_DATA_SIZE];  // data payload with valid size of 'dataSize'
    }gencpEvent;
    
}KYDEVICE_EVENT_GENCP_EVENT;
#pragma pack(pop)

#pragma pack(push, 1)

// used for KYDEVICE_EVENT_GIGE_EVENTDATA_ID
#define KY_GIGE_EVENTDATA_EVENT_MAX_DATA_SIZE 512

typedef struct _KYDEVICE_EVENT_GIGE_EVENTDATA
{
    // KYDEVICE_EVENT_GIGE_EVENTDATA derived from KYDEVICE_EVENT:
    KYDEVICE_EVENT deviceEvent;

    // Specific KYDEVICE_EVENT_GIGE_EVENTDATA members:
    int srcDevicePort;
    struct KY_GIGE_EVENTDATA_EVENT 
    {
        uint16_t eventSize;      // Size of event data object in bytes including event_size, event_id, timestamp and optional data.
        uint16_t eventId;        // The event_id is a number identifying an event source.
        uint16_t streamChannel;
        uint16_t blockId;
        uint64_t timestamp;       // 64 bit timestamp value in ns as defined in the timestamp bootstrap register.
        uint8_t data[KY_GIGE_EVENTDATA_EVENT_MAX_DATA_SIZE];  // data payload with valid size of 'dataSize'
    }gigeEvent;
}KYDEVICE_EVENT_GIGE_EVENTDATA;
#pragma pack(pop)

typedef void(KYFG_CALLCONV *KYDeviceEventCallBack)(void* userContext, KYDEVICE_EVENT* pEvent);
KAYA_API FGSTATUS KYDeviceEventCallBackRegister(FGHANDLE handle, KYDeviceEventCallBack userFunc, void* userContext);
KAYA_API FGSTATUS KYDeviceEventCallBackUnregister(FGHANDLE handle, KYDeviceEventCallBack userFunc);

/**
 * @brief   Creates new stream object bound to given open camera
 * @details Collects information from the camera such as value of "Width", "Height", "PixelFormat" and Frame Grabber configuration parameters
 *          such as "SegmentsPerBuffer" in order to initialize internal data structure(s) required to manage a video stream
 *          Stream created with this function requires user to provide and manage buffers using KYFG_BufferToQueue() and/or KYFG_BufferQueueAll() API calls
 * @pre     Camera specified by 'camHandle' must be open
 * @param   [in] camHandle - handle of an open camera
 * @param   [out] pStreamHandle - pointer to STREAM_HANDLE variable that will be filled with handle of newly created stream
 * @param   [in] streamIndex - reserved for future use, must be 0
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_StreamCreate(CAMHANDLE camHandle, STREAM_HANDLE *pStreamHandle, int streamIndex); //streamIndex currently must be 0

/**
 * @brief   Link all announced frame buffers into a stream to form continuous cyclic buffer
 * @param   [in] streamHandle - handle of a previously created stream
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_StreamLinkFramesContinuously(STREAM_HANDLE streamHandle);

/**
 * @brief   Creates internal stream object bound to given open camera with automatic video buffer allocation and management.
 * @details Collects information from given open camera such as value of "Width", "Height" and "PixelFormat" and Frame Grabber configuration parameters
 *          such as "SegmentsPerBuffer" to initialize internal data structure(s) required to manage a video stream.
 *          Stream created with this function automatically manages buffers and doesn't accept KYFG_BufferToQueue() and KYFG_BufferQueueAll() API calls
 * @pre     Camera specified by 'camHandle' must be open.
 * @param   [in] camHandle - handle of an open camera.
 * @param   [out] pStreamHandle - pointer to STREAM_HANDLE variable that will be filled with handle of newly created stream.
 * @param   [in] frames - number of allocated video frames required.
 * @param   [in] streamIndex - reserved for future use, must be 0
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_StreamCreateAndAlloc(CAMHANDLE camHandle, STREAM_HANDLE *pStreamHandle, uint32_t frames, int streamIndex);

KY_DEPRECATED2(KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_BufferAlloc(CAMHANDLE camHandle, BUFFHANDLE *pBuffHandle, uint32_t frames) KY_FORCE_INLINE_GCC, "Function 'KYFG_BufferAlloc' is deprecated, please use function 'KYFG_StreamCreateAndAlloc()'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_BufferAlloc(CAMHANDLE camHandle, BUFFHANDLE *pBuffHandle, uint32_t frames)
{
    return KYFG_StreamCreateAndAlloc(camHandle, pBuffHandle, frames, 0);
}

/**
 * @brief create a single buffer, representing a single frame. The buffer will be associated  with the pre-defined stream
 */
KAYA_API FGSTATUS KYFG_BufferAllocAndAnnounce(STREAM_HANDLE streamHandle, size_t nBufferSize, void * pPrivate, STREAM_BUFFER_HANDLE * pBufferHandle);

/**
 * @brief submit a user buffer, representing a single frame, for a pre-defined stream
 */
KAYA_API FGSTATUS KYFG_BufferAnnounce(STREAM_HANDLE streamHandle, void * pBuffer, size_t nBufferSize, void * pPrivate, STREAM_BUFFER_HANDLE * pBufferHandle);


typedef enum _KY_STREAM_INFO_CMD
{
    KY_STREAM_INFO_PAYLOAD_SIZE                     =  7,   /* SIZET    Size of the expected data in bytes */
    KY_STREAM_INFO_BUF_ALIGNMENT                    = 13,   /* SIZET    Buffer memory alignment in bytes */
    KY_STREAM_INFO_PAYLOAD_SIZE_INCREMENT_FACTOR    = 1000, /* SIZET    Payload size should be divisible by increment factor */
    // TODO: the following is KYFGLib addition, check for standard name existance
    KY_STREAM_INFO_BUF_COUNT                        = 2000, /* SIZET    Number of buffers in the stream */
    KY_STREAM_INFO_INSTANTFPS                       = 2001, /* FLOAT64  Last calculated FPS. Valid after at least two frames have been acquired*/
}KY_STREAM_INFO_CMD;

typedef enum _KY_ACQ_QUEUE_TYPE
{
    KY_ACQ_QUEUE_INPUT,                 // buffers in INPUT queue are ready to be filled with data 
    KY_ACQ_QUEUE_OUTPUT,                // buffers in OUTPUT queue have been filled with data and awaiting user processing
    KY_ACQ_QUEUE_UNQUEUED,              // buffers in UNQUEUED set have been announced but are inactive for acquisition mechanism. By default all buffers are placed in UNQUEUED set
    KY_ACQ_QUEUE_AUTO,                  // buffers in AUTO queue are managed automatically, in a cyclic matter, without the need for user to re-queue them 
}KY_ACQ_QUEUE_TYPE;

/**
 * @brief retrieve information on requested pre-defined stream
 */
KAYA_API FGSTATUS KYFG_StreamGetInfo(STREAM_HANDLE streamHandle, KY_STREAM_INFO_CMD cmdStreamInfo, void *pInfoBuffer, size_t *pInfoSize, KY_DATA_TYPE *pInfoType);


typedef enum _KY_STREAM_BUFFER_INFO_CMD
{
    KY_STREAM_BUFFER_INFO_BASE                            = 0,  /* PTR        Base address of the buffer memory */
    KY_STREAM_BUFFER_INFO_SIZE                            = 1,  /* SIZET      Size of the buffer in bytes */
    KY_STREAM_BUFFER_INFO_USER_PTR                        = 2,  /* PTR        Private data pointer to the stream buffer */
    KY_STREAM_BUFFER_INFO_TIMESTAMP                       = 3,  /* UINT64     Timestamp the buffer was acquired in nanoseconds*/
    KY_STREAM_BUFFER_INFO_INSTANTFPS                      = 4,  /* FLOAT64    Instant FPS calculated from current and previous timestamp */
    KY_STREAM_BUFFER_INFO_ID                              = 1000, /* UINT32      Unique ID of the buffer in the stream */
}KY_STREAM_BUFFER_INFO_CMD;
/**
 * @brief retrieve information about stream buffer
 */
KAYA_API FGSTATUS KYFG_BufferGetInfo(STREAM_BUFFER_HANDLE streamBufferHandle, KY_STREAM_BUFFER_INFO_CMD cmdStreamBufferInfo, void *pInfoBuffer, size_t *pInfoSize, KY_DATA_TYPE *pInfoType);

/**
 * @brief move all announced frames buffers to specified queue
 */
KAYA_API FGSTATUS KYFG_BufferToQueue(STREAM_BUFFER_HANDLE streamBufferHandle, KY_ACQ_QUEUE_TYPE dstQueue);

/**
 * @brief move all announced frames buffers from one queue to another
 */
KAYA_API FGSTATUS KYFG_BufferQueueAll(STREAM_HANDLE streamHandle, KY_ACQ_QUEUE_TYPE srcQueue, KY_ACQ_QUEUE_TYPE dstQueue);

enum SUBMIT_BUFF_FLAGS
{
    SUBMIT_BUFF_REGULAR_BUFFER = 0x00,
    SUBMIT_BUFF_PHYSICAL_ADDRESS = 0x01,                // provided buffer addresses are physical addresses
};
KAYA_API FGSTATUS    KYFG_BufferSubmit(CAMHANDLE camHandle, STREAM_HANDLE *streamHandle, void** bufferPtrArray, unsigned int frames, unsigned int frameSize, unsigned int flags);


// Deletes the stream and frees all associated  resources 
KAYA_API FGSTATUS    KYFG_StreamDelete(STREAM_HANDLE streamHandle);

KY_DEPRECATED2(KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_BufferDelete(BUFFHANDLE buffHandle) KY_FORCE_INLINE_GCC, "Function 'KYFG_BufferDelete' is deprecated, please use function 'KYFG_StreamDelete'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_BufferDelete(BUFFHANDLE buffHandle)
{
    return KYFG_StreamDelete(buffHandle);
}

/**
 * @brief   Retrieves the pointer to a specified frame
 * @param   [in] streamHandle - handle to the allocated buffer
 * @param   [in] frame - the number of frame to retrieve its pointer [1..<num_of_frames>]
 * @return  pointer to a specified frame
 */
KAYA_API void*    KYFG_StreamGetPtr(STREAM_HANDLE streamHandle, uint32_t frame);
KY_DEPRECATED2(KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API void* KYFG_BufferGetPtr(BUFFHANDLE buffHandle, uint32_t frame) KY_FORCE_INLINE_GCC, "Function 'KYFG_BufferGetPtr' is deprecated, please use function 'KYFG_StreamGetPtr'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API void* KYFG_BufferGetPtr(BUFFHANDLE buffHandle, uint32_t frame)
{
    return KYFG_StreamGetPtr(buffHandle, frame);
}

// Retrieves the buffer's frame size (in bytes)
KAYA_API int64_t    KYFG_StreamGetSize(STREAM_HANDLE streamHandle);
KY_DEPRECATED2(KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API int64_t KYFG_BufferGetSize(BUFFHANDLE buffHandle) KY_FORCE_INLINE_GCC, "Function 'KYFG_BufferGetSize' is deprecated, please use function 'KYFG_StreamGetSize'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API int64_t KYFG_BufferGetSize(BUFFHANDLE buffHandle)
{
    return KYFG_StreamGetSize(buffHandle);
}

// Retrieves the last index of acquired frame from chosen buffer
KAYA_API int KYFG_StreamGetFrameIndex(STREAM_HANDLE streamHandle);
KY_DEPRECATED2(KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API int KYFG_BufferGetFrameIndex(BUFFHANDLE buffHandle) KY_FORCE_INLINE_GCC, "Function 'KYFG_BufferGetFrameIndex' is deprecated, please use function 'KYFG_StreamGetFrameIndex'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API int KYFG_BufferGetFrameIndex(BUFFHANDLE buffHandle)
{
    return KYFG_StreamGetFrameIndex(buffHandle);
}

/**
 * @brief   Retrieves the pointer to an auxiliary  data of a specified frame
 * @param   [in] streamHandle - handle to the allocated stream
 * @param   [in] frame - the number of frame to retrieve its pointer [1..<num_of_frames>]
 * @param   [out] pAuxData - pointer of an auxiliary  data to be filled
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_StreamGetAux(STREAM_HANDLE streamHandle, int frame, KYFG_AUX_DATA* pAuxData);

KY_DEPRECATED2(KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_BufferGetAux(BUFFHANDLE buffHandle, int frame, KYFG_AUX_DATA* pAuxData) KY_FORCE_INLINE_GCC, "Function 'KYFG_BufferGetAux' is deprecated, please use function 'KYFG_StreamGetAux'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_BufferGetAux(BUFFHANDLE buffHandle, int frame, KYFG_AUX_DATA* pAuxData)
{
    return KYFG_StreamGetAux(buffHandle, frame, pAuxData);
}

// <-- Low level registers access -->
// Read/Write to chosen port of the device
KAYA_API FGSTATUS KYFG_ReadPortReg(FGHANDLE handle, int port, uint64_t address, uint32_t* pData);
KAYA_API FGSTATUS KYFG_WritePortReg(FGHANDLE handle, int port, uint64_t address, uint32_t data);
/**
 * @brief   Read block of data to chosen port of the device.
 * @param   [in] handle - handle to the connected device
 * @param   [in] port - device port through which data will be sent
 * @param   [in] address - destination address on the remote device
 * @param   [out] data - data buffer, its length  is specified by size parameter
 * @param   [in,out] size - block size to process. Size will return the number of the proccessed bytes
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_ReadPortBlock(FGHANDLE handle, int port, uint64_t address, void* pBuffer, uint32_t* pSize);
/**
 * @brief   Write block of data to chosen port of the device.
 * @param   [in] handle - handle to the connected device
 * @param   [in] port - device port through which data will be sent
 * @param   [in] address - destination address on the remote device
 * @param   [in] data - data buffer, its length  is specified by size parameter
 * @param   [in,out] size - block size to process. Size will return the number of the proccessed bytes
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_WritePortBlock(FGHANDLE handle, int port, uint64_t address, const void* pBuffer, uint32_t* pSize);

typedef enum _PORT_STATUS
{
    PORT_DISCONNECTED         = 0x00,   // the port is disconnected, no link has been established
    PORT_SYNCHRONIZED         = 0x01,   // port link is synchronized and awaiting connection
    PORT_CONNECTING           = 0x10,     // a connection is trying to be established on port
    PORT_CONNECTED            = 0x11       // port is connected and assigned to camera 
}PORT_STATUS;

KAYA_API FGSTATUS KYFG_GetPortStatus(FGHANDLE handle, int port, PORT_STATUS* portStatus);

// Direct Read/Write to an address of connected device
KAYA_API FGSTATUS KYFG_DeviceDirectHardwareRead(FGHANDLE handle, uint64_t address, void* pBuffer, uint32_t bytes);
KAYA_API FGSTATUS KYFG_DeviceDirectHardwareWrite(FGHANDLE handle, uint64_t address, const void* pBuffer, uint32_t bytes);

// Direct Read/Write to registers of a connected device
KAYA_API FGSTATUS KYFG_GrabberReadReg(FGHANDLE handle, uint64_t address, void* pBuffer, uint32_t* pSize);
KAYA_API FGSTATUS KYFG_GrabberWriteReg(FGHANDLE handle, uint64_t address, const void* pBuffer, uint32_t* pSize);

// Read/Write to registers of a connected Camera (no XML file has to be present)
KAYA_API FGSTATUS KYFG_CameraReadReg(CAMHANDLE camHandle, uint64_t address, void* pBuffer, uint32_t* pSize);
KAYA_API FGSTATUS KYFG_CameraWriteReg(CAMHANDLE camHandle, uint64_t address, const void* pBuffer, uint32_t* pSize);

/**
 * @brief   Send Event Message as specified by GenCP for CLHS, or EVENTDATA message for 10GigE
 * @details Event message from remote device can be received using "KYDeviceEventCallBackRegister" event id "KYDEVICE_EVENT_GENCP_EVENT_ID" for CLHS, and "KYDEVICE_EVENT_GIGE_EVENTDATA_ID" for 10GigE
 * @param   [in] handle - handle to the connected device
 * @param   [in] port - device port through which data will be sent
 * @param   [in] eventId - id of the event message
 * @param   [in] pBuffer - event data payload, its length is specified by size parameter
 * @param   [in] bufferSize - event data size to process
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_DevicePortSendEventMessage(FGHANDLE handle, int port, uint32_t eventId, const void* pBuffer, uint32_t bufferSize);

/**
 * @brief   Send Event Message as specified by GenCP for CLHS, or EVENTDATA message for 10GigE
 * @details Event message from remote device can be received using "KYDeviceEventCallBackRegister" event id "KYDEVICE_EVENT_GENCP_EVENT_ID" for CLHS, and "KYDEVICE_EVENT_GIGE_EVENTDATA_ID" for 10GigE
 * @param   [in] camHandle - Camera handle
 * @param   [in] eventId - id of the event message
 * @param   [in] pBuffer - event data payload, its length is specified by size parameter
 * @param   [in] bufferSize - event data size to process
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_CameraSendEventMessage(CAMHANDLE camHandle, uint32_t eventId, const void* pBuffer, uint32_t bufferSize);


// <-- Camera connection -->
// Scans for the cameras connected to the Frame Grabber
KY_DEPRECATED(KAYA_API FGSTATUS KYFG_CameraScan(FGHANDLE handle, CAMHANDLE *camHandleArray, int *detectedCameras), "Function 'KYFG_CameraScan' is deprecated, please use function 'KYFG_UpdateCameraList'. Project should be loaded using function 'KYFG_OpenEx'.");

/**
 * @brief   Updates the list of cameras connected to the device. Open camera handles are not affected by this function and retained at the same places of array where they were returned by previous call except for camera(s) that were closed between calls.
 * @param   [in] handle - handle to the connected device
 * @param   [out] pCamHandleArray - pointer to an array of CAMHANDLE elements
 * @param   [in,out] pArraySize - pointer to integer. Must be set to number of elements allocated in the 'pCamHandleArray'. After successful function return indicates number of elements that were filled
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_UpdateCameraList(FGHANDLE handle, CAMHANDLE *pCamHandleArray, int *pArraySize);

typedef struct _KYFGLib_CameraScanParameters
{
    uint32_t version; // Version of this structure definition, must be 1

    // since version 1:
    CAMHANDLE *pCamHandleArray;  // array of CAMHANDLE allocated by caller
    int       nCameraCount;     // on entry number CAMHANDLEs allocated in 'pCamHandleArray', on exit number of detected cameras
    KYBOOL    bRetainOpenCameras;// KYTRUE if scan should skip currently active links and detect only new connections.
                                 // Open camera handles will not be affected by KYFG_CameraScanEx() call and will be retained at the same places of array where they were returned by previous call,
                                 // with exception for camera(s) that were closed between calls.
                                 // KYFALSE if all cuurently open camera handles should be reset and full re-scan should be performed.
}KYFGLib_CameraScanParameters;

/**
 * @brief   Updates the list of cameras connected to the device.
 * @param   [in] handle - handle to the connected device.
 * @param   [in, out] pScanParams - pointer to KYFGLib_CameraScanParameters instance.
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_CameraScanEx(FGHANDLE handle, KYFGLib_CameraScanParameters* pScanParams);

// Connects to a specific camera. If an xml_file_path is present then the XML is loaded from file and not from camera.
KY_DEPRECATED(KAYA_API FGSTATUS KYFG_CameraOpen(CAMHANDLE camHandle, const char *xml_file_path, const char* project_file_path), "Function 'KYFG_CameraOpen' with parameter 'project_file_path' is deprecated, please use function 'KYFG_CameraOpen2'. Project should be loaded using function 'KYFG_OpenEx'.");
KAYA_API FGSTATUS KYFG_CameraOpen2(CAMHANDLE camHandle, const char *xml_file_path);

// Closes connection to specific camera
KAYA_API FGSTATUS KYFG_CameraClose(CAMHANDLE camHandle);
// Retrieves information about a connected camera
KY_DEPRECATED(KAYA_API FGSTATUS KYFG_CameraInfo(CAMHANDLE camHandle, KYFGCAMERA_INFO *info), "Function 'KYFG_CameraInfo' is deprecated, please use function 'KYFG_CameraInfo2'.");
KAYA_API FGSTATUS KYFG_CameraInfo2(CAMHANDLE camHandle, KYFGCAMERA_INFO2 *info); 

/**
 * @brief   Enables video data flow for specified stream. If "TransferControlMode" Frame Grabbers parameter is set to "Automatic" (default) then also executes "AcquisitionStart" on the specified camera.
 * @details If "TransferControlMode" Frame Grabber parameter is set to "UserControlled" this function ommits last step of executing "AcquisitionStart" command on the camera
 *          and it is user responsibility to activate/deactivate camera stream issuing standard "AcquisitionStart" and "AcquisitionStop" camera commands.
 * @param   [in] camHandle - handle of an open camera.
 * @param   [in] streamHandle - handle to the allocated stream.
 * @param   [in] frames - number of frames to receive in software callback. It might not reflect the actual number of frames received in hardware!
 *                        set 0 to not limit number of recieved frames (recommended configuration value)
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_CameraStart(CAMHANDLE camHandle, STREAM_HANDLE streamHandle, uint32_t frames);
KY_DEPRECATED2(KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_CameraStartAcquire(CAMHANDLE camHandle, STREAM_HANDLE streamHandle, uint32_t frames) KY_FORCE_INLINE_GCC, "Function 'KYFG_CameraStartAcquire' is deprecated, please use function 'KYFG_CameraStart'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_CameraStartAcquire(CAMHANDLE camHandle, STREAM_HANDLE streamHandle, uint32_t frames)
{
    return KYFG_CameraStart(camHandle, streamHandle, frames);
}

/**
 * @brief   If "TransferControlMode" Frame Grabber parameter is set to "Automatic" (default) executes "AcquisitionStop" on the specified camera. Then disables video data flow for specified stream. 
 * @details If "TransferControlMode" Frame Grabber parameter is set to "UserControlled" this function ommits first step of executing "AcquisitionStopt" command on the camera.
 *          and it is user responsibility to activate/deactivate camera stream issuing standard "AcquisitionStart" and "AcquisitionStop" camera commands.
 * @param   [in] camHandle - handle of an open camera.
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_CameraStop(CAMHANDLE camHandle);
KY_DEPRECATED2(KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_CameraStopAcquire(CAMHANDLE camHandle) KY_FORCE_INLINE_GCC, "Function 'KYFG_CameraStopAcquire' is deprecated, please use function 'KYFG_CameraStop'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_CameraStopAcquire(CAMHANDLE camHandle)
{
    return KYFG_CameraStop(camHandle);
}

/**
 * @brief   Retreives the xml from camera to user allocated buffer.
 * @param   [in] camHandle - Camera handle
 * @param   [out] buffer - The extracted xml file from specified camera
 * @param   [in,out] bufferSize - The buffer size needed for extracted xml file
 * @param   [out] isZipFile - Flag indicates if the extracted xml file is of type xml(.xml) or a zip(.zip) file containing a camera xml file
 * @return  FGSTATUS - Error code of function execution status
 */
KAYA_API FGSTATUS KYFG_CameraGetXML(CAMHANDLE camHandle, char *buffer, KYBOOL* isZipFile, uint64_t *bufferSize);

/**
 * @brief   Retreives the xml from specified camera to library allocated buffer.
 * @details It is responcibility of the user to de-allocate xml buffer.
 * @param   [in] camHandle - Camera handle
 * @param   [out] buffer - The extracted xml file from specified camera
 * @param   [out] bufferSize - The buffer size needed for extracted xml file
 * @param   [out] isZipFile - Flag indicates if the extracted xml file is of type xml(.xml) or a zip(.zip) file containing a camera xml file
 * @return  FGSTATUS - Error code of function execution status
 */
KY_DEPRECATED(KAYA_API FGSTATUS KYFG_GetXML(CAMHANDLE camHandle, char** buffer, uint64_t *bufferSize, KYBOOL *isZipFile), "Function 'KYFG_GetXML' is deprecated, please use function 'KYFG_CameraGetXML'.");



// <-- Genicam functions (requires connection of GeniCam SDK) -->
// Set device value using Gen<i>Cam
KAYA_API FGSTATUS   KYFG_SetGrabberValue(FGHANDLE handle, const char *paramName, const void *paramValue);

KAYA_API FGSTATUS KYFG_SetGrabberValueInt(FGHANDLE handle, const char *paramName, int64_t value);

KAYA_API FGSTATUS   KYFG_SetGrabberValueFloat(FGHANDLE handle, const char *paramName, double value);

KAYA_API FGSTATUS   KYFG_SetGrabberValueBool(FGHANDLE handle, const char *paramName, KYBOOL value);

KAYA_API FGSTATUS   KYFG_SetGrabberValueEnum(FGHANDLE handle, const char *paramName, int64_t value);

KAYA_API FGSTATUS   KYFG_SetGrabberValueString(FGHANDLE handle, const char *paramName, const char* value);

KY_DEPRECATED2( KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS KYFG_ExecuteGrabberCommand(FGHANDLE handle, const char *paramName) KY_FORCE_INLINE_GCC, "Function 'KYFG_ExecuteGrabberCommand' is deprecated, please use function 'KYFG_GrabberExecuteCommand(FGHANDLE handle, const char *paramName)'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS   KYFG_ExecuteGrabberCommand(FGHANDLE handle, const char *paramName)
{
    int64_t dummyValue = 1;
    return KYFG_SetGrabberValue(handle, paramName, &dummyValue);
}
KAYA_API FGSTATUS   KYFG_GrabberExecuteCommand(FGHANDLE handle, const char *paramName);
KAYA_API FGSTATUS    KYFG_SetGrabberValueEnum_ByValueName(FGHANDLE handle, const char *paramName, const char *paramValueName);

// Set specific camera value using Gen<i>Cam 
KAYA_API FGSTATUS KYFG_SetCameraValue(CAMHANDLE camHandle, const char *paramName, void *paramValue);

KAYA_API FGSTATUS KYFG_SetCameraValueInt(CAMHANDLE camHandle, const char *paramName, int64_t value);

KAYA_API FGSTATUS KYFG_SetCameraValueFloat(CAMHANDLE camHandle, const char *paramName, double value);

KAYA_API FGSTATUS KYFG_SetCameraValueBool(CAMHANDLE camHandle, const char *paramName, KYBOOL value);

KAYA_API FGSTATUS KYFG_SetCameraValueEnum(CAMHANDLE camHandle, const char *paramName, int64_t value);


KAYA_API FGSTATUS KYFG_SetCameraValueString(CAMHANDLE camHandle, const char *paramName, const char* value);


KY_DEPRECATED2(KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS   KYFG_ExecuteCommand(CAMHANDLE camHandle, const char *paramName) KY_FORCE_INLINE_GCC, "Function 'KYFG_ExecuteCommand' is deprecated, please use function 'KYFG_GrabberExecuteCommand or KYFG_CameraExecuteCommand'.");
KY_INLINE KY_FORCE_INLINE_MSVC KAYA_API FGSTATUS   KYFG_ExecuteCommand(CAMHANDLE camHandle, const char *paramName)
{
    int64_t dummyValue = 1;
    return KYFG_SetCameraValue(camHandle, paramName, &dummyValue);
}
KAYA_API FGSTATUS   KYFG_CameraExecuteCommand(CAMHANDLE camHandle, const char *paramName);
// Sets Enumeration camera value by field name rather then its numeric value
KAYA_API FGSTATUS    KYFG_SetCameraValueEnum_ByValueName(CAMHANDLE camHandle, const char *paramName, const char *paramValueName);

#ifdef __cplusplus
static const int64_t INVALID_INT_PARAMETER_VALUE = INT64_MAX;
static const double INVALID_FLOAT_PARAMETER_VALUE = LDBL_MAX;
#else
#define INVALID_INT_PARAMETER_VALUE INT64_MAX
#define INVALID_FLOAT_PARAMETER_VALUE LDBL_MAX
#endif

// Get Frame Grabber value using Gen<i>Cam
KAYA_API FGSTATUS   KYFG_GetGrabberValue(FGHANDLE handle, const char *paramName, void *paramValue);

KAYA_API FGSTATUS   KYFG_GetGrabberValueIntMaxMin(FGHANDLE handle, const char *paramName, int64_t* pIntMax, int64_t* pIntMin);
KAYA_API FGSTATUS   KYFG_GetGrabberValueFloatMaxMin(FGHANDLE handle, const char *paramName, double* pDoubleMax, double* pDoubleMin);

KAYA_API int64_t KYFG_GetGrabberValueInt(FGHANDLE handle, const char *paramName);

KAYA_API int64_t KYFG_GetGrabberValueEnum(FGHANDLE handle, const char *paramName);

KAYA_API double KYFG_GetGrabberValueFloat(FGHANDLE handle, const char *paramName);

KAYA_API KYBOOL KYFG_GetGrabberValueBool(FGHANDLE handle, const char *paramName);


// Get Frame Grabber Parameter type
KAYA_API KY_CAM_PROPERTY_TYPE KYFG_GetGrabberValueType(FGHANDLE handle, const char *paramName);

// This function allocates memory for the string. The caller is responsible for releasing this memory
KY_DEPRECATED(KAYA_API FGSTATUS KYFG_GetGrabberValueString(FGHANDLE handle, const char *paramName, char** ptr), "Function 'KYFG_GetGrabberValueString' is deprecated, please use function 'KYFG_GetGrabberValueStringCopy' to retrieve string conent");

KAYA_API FGSTATUS KYFG_GetGrabberValueStringCopy(FGHANDLE handle, const char *paramName, char *stringPtr, uint32_t *stringSize);

KAYA_API FGSTATUS KYFG_GetGrabberValueRegister(FGHANDLE handle, const char *paramName, uint8_t *bufferPtr, uint32_t *bufferSize);

// Get camera Parameter type
KAYA_API KY_CAM_PROPERTY_TYPE KYFG_GetCameraValueType(CAMHANDLE camHandle, const char *paramName);

// This function allocates memory for the string. The caller is responsible for releasing this memory
KY_DEPRECATED(KAYA_API FGSTATUS KYFG_GetCameraValueString(CAMHANDLE camHandle, const char *paramName, char** ptr), "Function 'KYFG_GetCameraValueString' is deprecated, please use function 'KYFG_GetCameraValueStringCopy' to retrieve string conent");

KAYA_API FGSTATUS KYFG_GetCameraValueStringCopy(CAMHANDLE camHandle, const char *paramName, char *stringPtr, uint32_t *stringSize);


// Get specific camera value using Gen<i>Cam
KAYA_API FGSTATUS KYFG_GetCameraValue(CAMHANDLE camHandle, const char *paramName, void *paramValue);

KAYA_API FGSTATUS   KYFG_GetCameraValueIntMaxMin(CAMHANDLE handle, const char *paramName, int64_t* pIntMax, int64_t* pIntMin);
KAYA_API FGSTATUS   KYFG_GetCameraValueFloatMaxMin(CAMHANDLE handle, const char *paramName, double* pDoubleMax, double* pDoubleMin);

KAYA_API int64_t KYFG_GetCameraValueInt(CAMHANDLE camHandle, const char *paramName);

KAYA_API int64_t KYFG_GetCameraValueEnum(CAMHANDLE camHandle, const char *paramName);

KAYA_API double KYFG_GetCameraValueFloat(CAMHANDLE camHandle, const char *paramName);


KAYA_API KYBOOL KYFG_GetCameraValueBool(CAMHANDLE camHandle, const char *paramName);

KAYA_API FGSTATUS KYFG_GetCameraValueRegister(CAMHANDLE camHandle, const char *paramName, uint8_t *bufferPtr, uint32_t *bufferSize);

// Camera configuration
KAYA_API FGSTATUS KYFG_LoadCameraConfiguration(CAMHANDLE camHandle, const char *xmlFilePath, const char* valuesFilePath);
// TODO: Implement sugar for:
// KYCS_API CSSTATUS KYCS_LoadCameraConfiguration(CSHANDLE handle, char *defFile, char* valuesFile);

#ifdef __cplusplus
static const int KY_AUTHKEY_SIZE = 32;
#else
#define KY_AUTHKEY_SIZE 32
#endif
typedef struct _KY_AuthKey 
{ 
    unsigned char secret[KY_AUTHKEY_SIZE]; 
} KY_AuthKey;
KAYA_API FGSTATUS KYFG_CALLCONV KY_AuthProgramKey(FGHANDLE handle, KY_AuthKey* pKey, int lock);
KAYA_API FGSTATUS KYFG_CALLCONV KY_AuthVerify(FGHANDLE handle, KY_AuthKey* pKey);

KAYA_API FGSTATUS KYFG_LoadFileData(STREAM_HANDLE streamHandle, const char* path, const char* type, int frames);
KAYA_API FGSTATUS KYFG_LoadPatternData(STREAM_HANDLE streamHandle, PATTERN_TYPE type, uint16_t *FixedPatternColor);

/////////////////////////////////////////////////////////////////////////////
//
// Chameleon interface provided for backward compatibility:
//
/////////////////////////////////////////////////////////////////////////////

typedef FGSTATUS CSSTATUS;
typedef FGHANDLE CSHANDLE;

KAYA_API CSSTATUS KYCS_ReadBootstrapRegs(FGHANDLE handle, uint32_t address, void* data, uint32_t size);
KAYA_API CSSTATUS KYCS_WriteBootstrapRegs(FGHANDLE handle, uint32_t address, const void* data, uint32_t size);


//
// Image header access
//

// Maximum size that can be specified for KYCS_InjectImageHeader() and KYCS_GetImageHeader().
static const unsigned int IMAGE_HEADER_SIZE = 32; 

/**
 * @brief   Retrieves current image generation header
 * @param   [in] handle - handle to the camera simulator device
 * @param   [out] header - user supplied buffer where header should be stored
 * @param   [in] size - size of user supplied buffer. Maximum IMAGE_HEADER_SIZE can be specified, otherwise CSSTATUS_IMAGE_HEADER_INJECTION_SIZE_TOO_BIG will be returned by function
 * @return  CSSTATUS - Error code of function execution status
 */
KAYA_API CSSTATUS    KYCS_GetImageHeader(CSHANDLE handle, unsigned char* header , unsigned int size);

/**
 * @brief   Allow to overwrite one field of the standard stream image during a configurable number of image generation cycles.
 * @param   [in] handle - handle to camera the simulator device
 * @param   [in] header - user supplied buffer with header 
 * @param   [in] size - size of user supplied buffer. Maximum IMAGE_HEADER_SIZE can be specified, otherwise CSSTATUS_IMAGE_HEADER_INJECTION_SIZE_TOO_BIG will be returned by function
 * @param   [in] cycles - number of image generation cycles. Any value less than 1 is treated as -1 and stops further injections
 * @return  CSSTATUS - Error code of function execution status
 */
KAYA_API CSSTATUS    KYCS_InjectImageHeader(CSHANDLE handle, unsigned char* header , unsigned int size, int cycles);

//
// CRC Injection
//

/**
 * @brief   Allow to set a wrong CRC in one stream packet of one image generation, during a configurable number of image generation cycles.
 * @param   [in] handle - handle to the camera simulator device
 * @param   [in] cycles - number of image generation cycles. Any value less than 1 is treated as -1 and stops further injections
 * @return  CSSTATUS - Error code of function execution status
 */
KAYA_API CSSTATUS    KYCS_InjectVideoCRCErrors(CSHANDLE handle, int cycles);

/**
 * @brief   Allow to set a wrong CRC in the next return Control/Command packets, during a configurable number of cycles.
 * @param   [in] handle - handle to the camera simulator device
 * @param   [in] cycles - number of image generation cycles. Any value less than 1 is treated as -1 and stops further injections
 * @return  CSSTATUS - Error code of function execution status
 */
KAYA_API CSSTATUS    KYCS_InjectControlCRCErrors(CSHANDLE handle, int cycles);

//
// IO Control
//
KAYA_API CSSTATUS    KYCS_SetTriggerSource(CSHANDLE handle, KY_IO source);
KAYA_API CSSTATUS    KYCS_ConfigureIO(CSHANDLE handle, KY_IO source, KY_IO sink, KYBOOL Invert);
KAYA_API CSSTATUS    KYCS_SetOutputEnable(CSHANDLE handle, KY_IO sink);


KAYA_API CSSTATUS    KYCS_GenerateCxpEvent(CSHANDLE handle, KY_CXPEVENT_PACK* pEvent);

#ifdef __cplusplus
} // extern "C" {
#endif

#endif  // #ifndef KYFG_LIB_H_
