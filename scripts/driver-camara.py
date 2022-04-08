import KYFGLib as ky
from time import sleep
import ctypes as c
import sys



def connectToGrabber(grabberIndex):
    global handle
    (connected_fghandle,) = ky.KYFG_Open(grabberIndex)
    connected = connected_fghandle.get()
    handle[grabberIndex] = connected

class StreamInfoStruct:
    def __init__(self):
        self.width = 640
        self.height = 480
        self.callbackCount = 0
        return

def startCamera (grabberIndex, cameraIndex, n_frames):
    # put all buffers to input queue
    _, = ky.KYFG_BufferQueueAll(cameraStreamHandle, ky.KY_ACQ_QUEUE_TYPE.KY_ACQ_QUEUE_UNQUEUED, ky.KY_ACQ_QUEUE_TYPE.KY_ACQ_QUEUE_INPUT)
    
    _, = ky.KYFG_CameraStart(camHandleArray[grabberIndex][cameraIndex], cameraStreamHandle, n_frames)
    return 0

def Stream_callback_func_nuestra(buffHandle, userContext): 
    if (buffHandle == 0 ):
        Stream_callback_func.copyingDataFlag = 0
        return
    streamInfo = cast(userContext, ky.py_object).value
    
    
    width = ky.KYFG_GetCameraValue(buffHandle, "Width")
    height = ky.KYFG_GetGrabberValue(buffHandle, "Heiht")
    totalFrames = ky.KYFG_BufferValue(buffHandle, "RXFrameCounter")
    buffSize = ky.KYFG_BufferGetSize(buffSize)
    buffIndex = ky.KYFG_BufferGerFrameIndex(buffIndex)
    buffData = ky.KYFG_StreamGetPtr(buffHandle, 0)
    
    print("widht", width, "height",height, "tot frame", totalFrames, "buffSize", buffSize, "buffIndex", buffIndex, "buffData", buffData) 
    streamInfo.callbackCount = streamInfo.callbackCount + 1

    
    if ( Stream_callback_func.copyingDataFlag == 0):
        Stream_callback_func.copyingDataFlag = 1
    
    sys.stdout.flush()
    Stream_callback_func.copyingDataFlag = 0
    return

def Stream_callback_func(buffHandle, userContext): 
    print("STREAM CALLBACK FUNC")

    if (buffHandle == 0 ):
        Stream_callback_func.copyingDataFlag = 0
        return
    streamInfo = cast(userContext, ky.py_object).value
    #print('buffer ' + str(format(buffHandle, '02x')) + ': height=' + str(streamInfo.height) + ', width=' + str(
    #    streamInfo.width) + ', callback count=' + str(streamInfo.callbackCount))
    streamInfo.callbackCount = streamInfo.callbackCount + 1

    # Example of retrieving buffer information
    (KYFG_BufferGetInfo_status, pInfoBase, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
                                                                buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_BASE) # PTR
    #print('Good callback streams buffer handle: ' + str(format(int(buffHandle), '02x')) + ", Buffer Info: " + str(pInfoBase), end='\r')

    (KYFG_BufferGetInfo_status, pInfoSize, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
                                                                buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_SIZE) # SIZET
    (KYFG_BufferGetInfo_status, pInfoPTR, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
                                                                buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_USER_PTR) # PTR
    (KYFG_BufferGetInfo_status, pInfoTimestamp, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
                                                                buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_TIMESTAMP) # UINT64
    (KYFG_BufferGetInfo_status, pInfoFPS, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
                                                                buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_INSTANTFPS) # FLOAT64
    (KYFG_BufferGetInfo_status, pInfoID, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
                                                                buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_ID) # UINT32
    # print("KYFG_BufferGetInfo_status: " + str(format(KYFG_BufferGetInfo_status, '02x')))
    print("Buffer Info: Base " + str(pInfoBase) + ", Size " + str(pInfoSize) + ", Timestamp "+ str(pInfoTimestamp) + ", FPS " + str(pInfoFPS)
          + ", ID " + str(pInfoID), end='\r')

    sys.stdout.flush()
    (KYFG_BufferToQueue_status,) = KYFG_BufferToQueue(buffHandle ,KY_ACQ_QUEUE_TYPE.KY_ACQ_QUEUE_INPUT)
    #print("KYFG_BufferToQueue_status: " + str(format(KYFG_BufferToQueue_status, '02x'))) 
    Stream_callback_func.copyingDataFlag = 0
    return
Stream_callback_func.data = 0
Stream_callback_func.copyingDataFlag = 0

#################################################### Defines #######################
MAX_BOARDS = 4
MAX_CAMS = 4

handle = [0 for i in range(MAX_BOARDS)]

detectedCameras = []

grabberIndex = 0

camHandleArray = [[0 for x in range(0)] for y in range(MAX_BOARDS)]

buffHandle = ky.STREAM_HANDLE()

cameraStreamHandle = 0

frameDataSize = 0
frameDataAligment = 0

streamBufferHandle = [0 for i in range(16)]
streamAllignedBuffer = [0 for i in range(16)]

DEVICE_QUEUED_BUFFERS_SUPPORTED = "FW_Dma_Capable_QueuedBuffers_Imp"
##################################################### Defines #######################


#inicializa los parámetros (no sabemos de que ni para que sirven)
initParams = ky.KYFGLib_InitParameters()
ky.KYFGLib_Initialize(initParams)

#escanea los grabbers (opcional)
_, fgAmount = ky.KY_DeviceScan()
print(fgAmount)
_, dev_info = ky.KY_DeviceInfo(grabberIndex)
print("DeviceDisplayName: " + dev_info.szDeviceDisplayName)
print("Bus: " + str(dev_info.nBus))
print("Slot: " + str(dev_info.nSlot))
print("Function: " + str(dev_info.nFunction))
print("DevicePID: " + str(dev_info.DevicePID))
print("isVirtual: " + str(dev_info.isVirtual))
print("Version: " + str(dev_info.version))
print("Device Generation:" + str(dev_info.DeviceGeneration))

#Crea instancia de stream Info struct
streamInfoStruct = StreamInfoStruct()

#Se conecta al grabber (necesario)
connection = -1
try:
    connection = connectToGrabber(grabberIndex)
except ky.KYException as err:
    print('error')

if (connection == 0):
    (KYDeviceEventCallBackRegister_status,) = KYDeviceEventCallBackRegister(handle[grabberIndex], Device_event_callback_func, 0)


#Se conecta a la cámara
_, camHandleArray[grabberIndex] = ky.KYFG_UpdateCameraList(handle[grabberIndex])
cams_num = len(camHandleArray[grabberIndex])
if (cams_num < 1):
    print("no se encontraron camaras")
(KYFG_CameraOpen2_status,) = ky.KYFG_CameraOpen2(camHandleArray[grabberIndex][0], None)
if (KYFG_CameraOpen2_status == ky.FGSTATUS_OK):
    print("camara conectada correctamente")

_, = ky.KYFG_SetCameraValueInt(camHandleArray[grabberIndex][0], "Width", 640)
_, = ky.KYFG_SetCameraValueInt(camHandleArray[grabberIndex][0], "Height", 480)
_, cameraStreamHandle = ky.KYFG_StreamCreate(camHandleArray[grabberIndex][0], 0)
_, width = ky.KYFG_GetCameraValueInt(camHandleArray[grabberIndex][0], "Width")
_, height = ky.KYFG_GetCameraValueInt(camHandleArray[grabberIndex][0], "Height")
streamInfoStruct.width = width
streamInfoStruct.height = height

_, = ky.KYFG_StreamBufferCallbackRegister(cameraStreamHandle, Stream_callback_func, ky.py_object(streamInfoStruct))


_, payload_size, frameDataSize, pInfoType = ky.KYFG_StreamGetInfo(cameraStreamHandle, ky.KY_STREAM_INFO_CMD.KY_STREAM_INFO_PAYLOAD_SIZE)

_, buf_allignment, frameDataAligment, pInfoType = ky.KYFG_StreamGetInfo(cameraStreamHandle, ky.KY_STREAM_INFO_CMD.KY_STREAM_INFO_BUF_ALIGNMENT)

# allocate memory for desired number of frame buffers
for iFrame in range(len(streamBufferHandle)):
    streamAllignedBuffer[iFrame] = ky.aligned_array(buf_allignment, ky.c_ubyte, payload_size)
    _, streamBufferHandle[iFrame] = ky.KYFG_BufferAnnounce(cameraStreamHandle, streamAllignedBuffer[iFrame], None)

#Empieza a grabar
n_frames = 16
sys.stdout.flush()
startCamera(grabberIndex, 0, n_frames)
print(streamBufferHandle[0].get())

###(StreamCreateAndAlloc_status, buffHandle) = ky.KYFG_StreamCreateAndAlloc(camHandleArray[grabberIndex][0], 16, 0)
##(CallbackRegister_status) = ky.KYFG_StreamBufferCallbackRegister(buffHandle, Stream_callback_func, ky.py_object(streamInfoStruct))
##cantidad_frames = 10
##(CameraStart_status,) = ky.KYFG_CameraStart(camHandleArray[grabberIndex][0], buffHandle, cantidad_frames)
##
