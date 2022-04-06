import KYFGLib
from KYFGLib import *


############################# Callback Function ##################################

# Example of user class containing stream information
class StreamInfoStruct:
    def __init__(self):
        self.width = 640
        self.height = 480
        self.callbackCount = 0
        return

# Example of user Stream_callback_func function implementation
# Parameters brief:
#       buffHandle - API handle to received data. Type: STREAM_HANDLE
#       userContext - Retrieved when the callback is issued. Helps to determine the origin of stream in host application.
def Stream_callback_func(buffHandle, userContext): 

    if (buffHandle == 0 ):
        Stream_callback_func.copyingDataFlag = 0
        return
    streamInfo = cast(userContext, py_object).value
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

################################ Defines ###################################################

MAX_BOARDS = 4
MAX_CAMS = 4

handle = [0 for i in range(MAX_BOARDS)]

detectedCameras = []

grabberIndex = 1

camHandleArray = [[0 for x in range(0)] for y in range(MAX_BOARDS)]

buffHandle = STREAM_HANDLE()

cameraStreamHandle = 0

frameDataSize = 0
frameDataAligment = 0

streamBufferHandle = [0 for i in range(16)]
streamAllignedBuffer = [0 for i in range(16)]

DEVICE_QUEUED_BUFFERS_SUPPORTED = "FW_Dma_Capable_QueuedBuffers_Imp"
################################## Control Functions ####################################
def printErr(err, msg = ""):
    print(msg)
    print("Error description: {0}".format(err))


def connectToGrabber(grabberIndex):
    global handle
    (connected_fghandle,) = KYFG_Open(grabberIndex)
    connected = connected_fghandle.get()
    handle[grabberIndex] = connected

    (status, tested_dev_info) = KYFGLib.KY_DeviceInfo(grabberIndex)
    print ("Good connection to grabber " + str(grabberIndex) + ": " + tested_dev_info.szDeviceDisplayName + ", handle= " + str(format(connected, '02x')))
    
    (KYFG_GetGrabberValueInt_status, dmadQueuedBufferCapable) = KYFG_GetGrabberValueInt(handle[grabberIndex],DEVICE_QUEUED_BUFFERS_SUPPORTED)
    
    #print("StreamCreateAndAlloc_status: " + str(format(KYFG_GetGrabberValueInt_status, '02x')))
    #print("dmadQueuedBufferCapable: " + str(format(dmadQueuedBufferCapable, '02x')))
    
    if ( dmadQueuedBufferCapable != 1 ):
        print("grabber #" + str(grabberIndex) + " is not queued buffers capable\n")
    
    return 0


def startCamera (grabberIndex, cameraIndex):
    # put all buffers to input queue
    (KYFG_BufferQueueAll_status,) = KYFG_BufferQueueAll(cameraStreamHandle, KY_ACQ_QUEUE_TYPE.KY_ACQ_QUEUE_UNQUEUED, KY_ACQ_QUEUE_TYPE.KY_ACQ_QUEUE_INPUT)
    print("KYFG_BufferQueueAll_status: " + str(format(KYFG_BufferQueueAll_status, '02x')))
    (KYFG_CameraStart_status,) = KYFG_CameraStart(camHandleArray[grabberIndex][cameraIndex], cameraStreamHandle, 0)
    print("KYFG_CameraStart_status: " + str(format(KYFG_CameraStart_status, '02x')))
    return 0

########################### Script ################################################


try:
    print("Welcome To KYFGLib Queued Buffers API Python Sample Script\n")

    initParams = KYFGLib_InitParameters()
    KYFGLib_Initialize(initParams)

    (KY_GetSoftwareVersion_status, soft_ver) = KY_GetSoftwareVersion()
    print("KYFGLib version: " + str(soft_ver.Major) + "." + str(soft_ver.Minor) + "." + str(soft_ver.SubMinor))
    if (soft_ver.Beta > 0):
        print("(Beta " + str(soft_ver.Beta) + ")")
    if (soft_ver.RC > 0):
        print("(RC " + str(soft_ver.RC) + ")")

    # Scan grabbers
    (status, fgAmount) = KYFGLib.KY_DeviceScan()
    if (status != FGSTATUS_OK):
        print("KY_DeviceScan() status: " + str(format(status, '02x')))

    # Print available grabbers params
    for x in range(fgAmount):
        (status, dev_info) = KYFGLib.KY_DeviceInfo(x)
        if (status != FGSTATUS_OK):
            print("Cant retrieve device #" + str(x) + " info")
            continue
        print("Device " + str(x) + ": " + dev_info.szDeviceDisplayName)

    # Create an instance of 'StreamInfoStruct' struct and pass it later to KYFG_StreamBufferCallbackRegister function as userContext
    streamInfoStruct = StreamInfoStruct()
    
    c = 'x'
    while (c != 'e'):
        if (c != ''):
            print(
                "\nEnter choice: ([0-4]-select grabber) (o-open frabber) (c-connect to camera)(s-start)(t-stop)(e-exit)(i-info)(x-getXML)")
        c = input("")
        if (len(c) != 1):
            print("Please enter one char")
            continue

        if (c >= '0' and c < str(MAXBOARDS)):
            grabberIndex = int(c)
            print("Selected grabber: " + str(c))
            print("\nGetting info about the grabber: ")
            (status, dev_info) = KY_DeviceInfo(grabberIndex)
            if (status != FGSTATUS_OK):
                print("Cant retrieve device #" + str(grabberIndex) + " info")
                continue
            print("DeviceDisplayName: " + dev_info.szDeviceDisplayName)
            print("Bus: " + str(dev_info.nBus))
            print("Slot: " + str(dev_info.nSlot))
            print("Function: " + str(dev_info.nFunction))
            print("DevicePID: " + str(dev_info.DevicePID))
            print("isVirtual: " + str(dev_info.isVirtual))

        elif (c == 'o'):
            connection = -1
            try:
                connection = connectToGrabber(grabberIndex)
            except KYException as err:
                print('\n')
                printErr(err, "Could not connect to grabber {0}".format(grabberIndex))

        elif (c == 's'):
            print('\r', end='')
            sys.stdout.flush()
            startCamera(grabberIndex, 0)

        elif (c == 't'):
            print('\r', end='')
            sys.stdout.flush()
            (CameraStop_status,) = KYFG_CameraStop(camHandleArray[grabberIndex][0])
            # print("CameraStop_status: " + str(format(CameraStop_status, '02x')))


        elif (c == 'c'):
            # scan for connected cameras
            (CameraScan_status, camHandleArray[grabberIndex]) = KYFG_UpdateCameraList(handle[grabberIndex])
            print("Found " + str(len(camHandleArray[grabberIndex])) + " cameras");
            if(len(camHandleArray[grabberIndex]) == 0):
                print("Could not connect to a camera")
                continue
            # open a connection to chosen camera
            (KYFG_CameraOpen2_status,) = KYFG_CameraOpen2(camHandleArray[grabberIndex][0], None)
            # print("KYFG_CameraOpen2_status: " + str(format(KYFG_CameraOpen2_status, '02x')))
            if (KYFG_CameraOpen2_status == FGSTATUS_OK):
                print("Camera 0 was connected successfully")
            else:
                print("Something went wrong while opening camera")

            # Example of setting camera values
            (SetCameraValueInt_status_width,) = KYFG_SetCameraValueInt(camHandleArray[grabberIndex][0], "Width", 640)
            # print("SetCameraValueInt_status_width: " + str(format(SetCameraValueInt_status_width, '02x')))
            (SetCameraValueInt_status_height,) = KYFG_SetCameraValueInt(camHandleArray[grabberIndex][0], "Height", 480)
            # print("SetCameraValueInt_status_height: " + str(format(SetCameraValueInt_status_height, '02x')))
            #(SetCameraValueEnum_ByValueName_status,) = KYFG_SetCameraValueEnum_ByValueName(camHandleArray[grabberIndex][0], "PixelFormat", "Mono8")
            # print("SetCameraValueEnum_ByValueName_status: " + str(format(SetCameraValueEnum_ByValueName_status, '02x')))

            # create stream and assign appropriate runtime acquisition callback function
            (KYFG_StreamCreate_status, cameraStreamHandle) = KYFG_StreamCreate(camHandleArray[grabberIndex][0], 0)
            # print("KYFG_StreamCreate_status: " + str(format(KYFG_StreamCreate_status, '02x')))

            # Example of getting camera values
            (KYFG_GetValue_status, width) = KYFG_GetCameraValueInt(camHandleArray[grabberIndex][0], "Width")
            (KYFG_GetValue_status, height) = KYFG_GetCameraValueInt(camHandleArray[grabberIndex][0], "Height")

            streamInfoStruct.width = width
            streamInfoStruct.height = height

            # Register user 'Stream_callback_func' function and 'streamInfoStruct' as 'userContext'
            # 'streamInfoStruct' will be retrieved when the callback is issued
            (KYFG_StreamBufferCallbackRegister_status,) = KYFG_StreamBufferCallbackRegister(cameraStreamHandle,
                                                                                            Stream_callback_func, py_object(streamInfoStruct))
            # print("KYFG_StreamBufferCallbackRegister_status: " + str(format(KYFG_StreamBufferCallbackRegister_status, '02x')))

            # Retrieve information about required frame buffer size and alignment
            (KYFG_StreamGetInfo_status, payload_size, frameDataSize, pInfoType) = \
                KYFG_StreamGetInfo(cameraStreamHandle, KY_STREAM_INFO_CMD.KY_STREAM_INFO_PAYLOAD_SIZE)

            (KYFG_StreamGetInfo_status, buf_allignment, frameDataAligment, pInfoType) = \
                KYFG_StreamGetInfo(cameraStreamHandle, KY_STREAM_INFO_CMD.KY_STREAM_INFO_BUF_ALIGNMENT)

            # allocate memory for desired number of frame buffers
            for iFrame in range(len(streamBufferHandle)):
                streamAllignedBuffer[iFrame] = aligned_array(buf_allignment, c_ubyte, payload_size)
                # print("Address of alligned array: " + hex(addressof(streamAllignedBuffer[iFrame])))
                (status, streamBufferHandle[iFrame]) = KYFG_BufferAnnounce(cameraStreamHandle,
                                                                           streamAllignedBuffer[iFrame], None)
        elif (c == 'i'):
            (Status, camInfo) = KYFG_CameraInfo2(camHandleArray[grabberIndex][0])
            print("master_link: ", str(camInfo.master_link))
            print("link_mask: ", str(camInfo.link_mask))
            print("link_speed: ", str(camInfo.link_speed))
            print("stream_id: ", str(camInfo.stream_id))
            print("deviceVersion: ", str(camInfo.deviceVersion))
            print("deviceVendorName: ", str(camInfo.deviceVendorName))
            print("deviceManufacturerInfo: ", str(camInfo.deviceManufacturerInfo))
            print("deviceModelName: ", str(camInfo.deviceModelName))
            print("deviceID: ", str(camInfo.deviceID))
            print("deviceUserID: ", str(camInfo.deviceUserID))
            print("outputCamera: ", str(camInfo.outputCamera))
            print("virtualCamera: ", str(camInfo.virtualCamera))

        elif (c == 'x'):
            (KYFG_CameraGetXML_status, isZipped, buffer) = KYFG_CameraGetXML(camHandleArray[grabberIndex][0])
            print("Is Zipped: " + str(isZipped))
            # print("KYFG_CameraGetXML_status: " + str(format(KYFG_CameraGetXML_status, '02x')))
            if (isZipped == False):
                print("Writing buffer to xml file...")
                newFile = open("camera_xml.xml", "w")
                newFile.write(''.join(buffer))
                newFile.close()
            else:
                print("Writing buffer to zip file...")
                newFile = open("camera_xml.zip", "wb")
                newFile.write(bytes(buffer))
                newFile.close()
        else:
            print("Please enter a correct character")

    input("\nPress enter to exit");

    if (len(camHandleArray[grabberIndex]) > 0):
        (KYFG_CameraClose_status,) = KYFG_CameraClose(camHandleArray[grabberIndex][0])
    if (handle[grabberIndex] != 0):
        (KYFG_Close_status,) = KYFG_Close(handle[grabberIndex])


except KYException as KYe:
    print("KYException occurred: ")
    raise












