import KYFGLib as ky
from time import sleep
import ctypes as c



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

def Stream_callback_func(buffHandle, userContext): 
    if (buffHandle == 0 ):
        Stream_callback_func.copyingDataFlag = 0
        return

    streamInfo = cast(userContext, ky.py_object).value
    #print('buffer ' + str(format(buffHandle, '02x')) + ': height=' + str(streamInfo.height) + ', width=' + str(
    #    streamInfo.width) + ', callback count=' + str(streamInfo.callbackCount))
    streamInfo.callbackCount = streamInfo.callbackCount + 1

    (KYFG_BufferGetInfo_status, pInfoBase, pInfoSize, pInfoType) = ky.KYFG_BufferGetInfo(
         buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_BASE) # PTR
    (KYFG_BufferGetInfo_status, pInfoPTR, pInfoSize, pInfoType) = ky.KYFG_BufferGetInfo(
        buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_USER_PTR)  # PTR
    (KYFG_BufferGetInfo_status, pInfoTimestamp, pInfoSize, pInfoType) = ky.KYFG_BufferGetInfo(
        buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_TIMESTAMP)  # UINT64
    (KYFG_BufferGetInfo_status, pInfoFPS, pInfoSize, pInfoType) = ky.KYFG_BufferGetInfo(
        buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_INSTANTFPS)  # FLOAT64
    (KYFG_BufferGetInfo_status, pInfoID, pInfoSize, pInfoType) = ky.KYFG_BufferGetInfo(
        buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_ID)  # UINT32
    # print("KYFG_BufferGetInfo_status: " + str(format(KYFG_BufferGetInfo_status, '02x')))
    print(
        "Buffer Info: Base " + str(pInfoBase) + ", Size " + str(pInfoSize) + ", Timestamp " + str(pInfoTimestamp) + ", FPS " + str(pInfoFPS)
        + ", ID " + str(pInfoID), end='\r')
    
    if ( Stream_callback_func.copyingDataFlag == 0):
        Stream_callback_func.copyingDataFlag = 1
    
    sys.stdout.flush()
    Stream_callback_func.copyingDataFlag = 0
    return

#################################################### Defines #######################
MAX_BOARDS = 4

handle = [0 for i in range(MAX_BOARDS)]

detectedCameras = []

grabberIndex = 0

camHandleArray = [[0 for x in range(0)] for y in range(MAX_BOARDS)]

buffHandle = ky.STREAM_HANDLE()
##################################################### Defines #######################


#inicializa los parámetros (no sabemos de que ni para que sirven)
initParams = ky.KYFGLib_InitParameters()
# initParams. =
ky.KYFGLib_Initialize(initParams)

#escanea los grabbers (opcional)
# Scan for availible grabbers
(KYFG_Scan_status, fgAmount) = ky.KY_DeviceScan()
print(fgAmount, KYFG_Scan_status)
(status, dev_info) = ky.KY_DeviceInfo(grabberIndex)
print("DeviceDisplayName: " + dev_info.szDeviceDisplayName)
print("Bus: " + str(dev_info.nBus))
print("Slot: " + str(dev_info.nSlot))
print("Function: " + str(dev_info.nFunction))
print("DevicePID: " + str(dev_info.DevicePID))
print("isVirtual: " + str(dev_info.isVirtual))
print("Version: " + str(dev_info.version))
print("Device Generation:" + str(dev_info.DeviceGeneration))


streamInfoStruct = StreamInfoStruct()

#Se conecta al grabber (necesario)
connection = -1
try:
    connection = connectToGrabber(grabberIndex)
except ky.KYException as err:
    print('error')

if (connection == 0):
    (KYDeviceEventCallBackRegister_status,) = KYDeviceEventCallBackRegister(handle[grabberIndex],
                                                                            Device_event_callback_func, 0)


#Se conecta a la cámara
(CameraScan_status, camHandleArray[grabberIndex]) = ky.KYFG_UpdateCameraList(handle[grabberIndex])
cams_num = len(camHandleArray[grabberIndex])
if (cams_num < 1):
    print("no se encontraron camaras")
(KYFG_CameraOpen2_status,) = ky.KYFG_CameraOpen2(camHandleArray[grabberIndex][0], None)
if (KYFG_CameraOpen2_status == ky.FGSTATUS_OK):
    print("camara conectada correctamente")

#Empieza a grabar

(StreamCreateAndAlloc_status, buffHandle) = ky.KYFG_StreamCreateAndAlloc(camHandleArray[grabberIndex][0], 16, 0)
(CallbackRegister_status) = ky.KYFG_StreamBufferCallbackRegister(buffHandle, Stream_callback_func, ky.py_object(streamInfoStruct))
cantidad_frames = 10
(CameraStart_status,) = ky.KYFG_CameraStart(camHandleArray[grabberIndex][0], buffHandle, cantidad_frames)

#buscamos el pointer donde estan los datos y el buffer size
pointer = ky.KYFG_StreamGetPtr(buffHandle, 0)
buffSize = ky.KYFG_StreamGetInfo(buffHandle, 7)
print(buffSize)

#leemos el pointer, probamos entero de 64 bits
data = (buffSize).from_address(pointer)
print(data)

#Guardo una imagen

