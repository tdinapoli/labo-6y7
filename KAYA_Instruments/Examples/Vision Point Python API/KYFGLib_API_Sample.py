import KYFGLib
from KYFGLib import *

############################ Callback Detection ############################

def Device_event_callback_func(userContext, event):
    if (isinstance(event, KYDEVICE_EVENT_CAMERA_CONNECTION_LOST) == True):
        print("KYDEVICE_EVENT_CAMERA_CONNECTION_LOST_ID event recognized")
        print("event_id: " + str(event.deviceEvent.eventId))
        print("cam_handle: " + format(event.camHandle.get(), '02x'))   
        print("device_link: " + str(event.iDeviceLink))
        print("camera_link: " + str(event.iCameraLink))
    elif (isinstance(event, KYDEVICE_EVENT_CAMERA_START) == True):
        print("KYDEVICE_EVENT_CAMERA_START event recognized")
        print("event_id: " + str(event.deviceEvent.eventId))
        print("camHandle: " + format(event.camHandle.get(), '02x'))
    elif (isinstance(event, KYDEVICE_EVENT_SYSTEM_TEMPERATURE) == True):
        print("KYDEVICE_EVENT_SYSTEM_TEMPERATURE event recognized")
        print("event_id: " + str(event.deviceEvent.eventId))
        print("temperatureThresholdId: " + str(event.temperatureThresholdId))
    elif (isinstance(event, KYDEVICE_EVENT_CXP2_HEARTBEAT) == True):
        print("KYDEVICE_EVENT_CXP2_HEARTBEAT event recognized")
        print("event_id: " + str(event.deviceEvent.eventId))
        print("camHandle: " + format(event.camHandle.get(), '02x'))
    elif (isinstance(event, KYDEVICE_EVENT_CXP2_EVENT) == True):
        print("KYDEVICE_EVENT_CXP2_EVENT event recognized")
        print("event_id: " + str(event.deviceEvent.eventId))
        print("camHandle: " + format(event.camHandle.get(), '02x'))
    elif (isinstance(event, KYDEVICE_EVENT_GENCP_EVENT) == True):
        print("KYDEVICE_EVENT_GENCP_EVENT event recognized")
        print("event_id: " + str(event.deviceEvent.eventId))
    elif (isinstance(event, KYDEVICE_EVENT_GIGE_EVENTDATA) == True):
        print("KYDEVICE_EVENT_GIGE_EVENTDATA event recognized")
        print("event_id: " + str(event.deviceEvent.eventId))
    else:
        print("Unknown event recognized")


############################# Callback Function ##################################

def Stream_callback_func(buffHandle, userContext): 
    if (buffHandle == 0 ):
        Stream_callback_func.copyingDataFlag = 0
        return

    streamInfo = cast(userContext, py_object).value
    #print('buffer ' + str(format(buffHandle, '02x')) + ': height=' + str(streamInfo.height) + ', width=' + str(
    #    streamInfo.width) + ', callback count=' + str(streamInfo.callbackCount))
    streamInfo.callbackCount = streamInfo.callbackCount + 1

    (KYFG_BufferGetInfo_status, pInfoBase, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
         buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_BASE) # PTR
    (KYFG_BufferGetInfo_status, pInfoPTR, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
        buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_USER_PTR)  # PTR
    (KYFG_BufferGetInfo_status, pInfoTimestamp, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
        buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_TIMESTAMP)  # UINT64
    (KYFG_BufferGetInfo_status, pInfoFPS, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
        buffHandle, KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_INSTANTFPS)  # FLOAT64
    (KYFG_BufferGetInfo_status, pInfoID, pInfoSize, pInfoType) = KYFG_BufferGetInfo(
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

Stream_callback_func.data = 0
Stream_callback_func.copyingDataFlag = 0

# Example of user class containing stream information
class StreamInfoStruct:
    def __init__(self):
        self.width = 640
        self.height = 480
        self.callbackCount = 0
        return

################################ Defines ###################################################

MAX_BOARDS = 4

handle = [0 for i in range(MAX_BOARDS)]

detectedCameras = []

grabberIndex = 1

camHandleArray = [[0 for x in range(0)] for y in range(MAX_BOARDS)]

buffHandle = STREAM_HANDLE()

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
    print("Good connection to grabber " + str(grabberIndex) + ": " + tested_dev_info.szDeviceDisplayName + ", handle= " + str(format(connected, '02x')))
    return 0


########################### Script ################################################
try:
    print("Welcome To KYFGLib API Python Sample Script\n")

    initParams = KYFGLib_InitParameters()
    # initParams. =
    KYFGLib_Initialize(initParams)

    (KY_GetSoftwareVersion_status, soft_ver) = KY_GetSoftwareVersion()
    print("KYFGLib version: " + str(soft_ver.Major) + "." + str(soft_ver.Minor) + "." + str(soft_ver.SubMinor))
    if (soft_ver.Beta > 0):
        print("(Beta " + str(soft_ver.Beta) + ")")
    if (soft_ver.RC > 0):
        print("(RC " + str(soft_ver.RC) + ")")

    # Scan for availible grabbers
    (KYFG_Scan_status, fgAmount) = KY_DeviceScan()
    if (KYFG_Scan_status != FGSTATUS_OK):
        print("KY_DeviceScan() status: " + str(format(KYFG_Scan_status, '02x')))

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
                "\nEnter choice: ([0-4]-select grabber) (o-open grabber) (c-connect to camera)(s-start)(t-stop)(e-exit)(i-camera info)(x-getXML)")
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

        elif (c == 'c'):
            # scan for connected cameras
            (CameraScan_status, camHandleArray[grabberIndex]) = KYFG_UpdateCameraList(handle[grabberIndex])
            cams_num = len(camHandleArray[grabberIndex])
            print("Found " + str(cams_num) + " cameras\n");
            # If no cameras found -->  continue
            if (cams_num < 1):
                print("Please, connect at least one camera to continue")
                continue
                # open a connection to camera 0
            (KYFG_CameraOpen2_status,) = KYFG_CameraOpen2(camHandleArray[grabberIndex][0], None)
            # print("KYFG_CameraOpen2_status: " + str(format(KYFG_CameraOpen2_status, '02x')))
            if (KYFG_CameraOpen2_status == FGSTATUS_OK):
                print("Camera 0 was connected successfully")
            else:
                print("Something got wrong while camera connecting")


            # Set ROI Width
            '''
            (SetCameraValue_status_width,) = KYFG_SetCameraValue(camHandleArray[grabberIndex][0], "Width", 640)
            print("\nWidth SetCameraValue_status_width: " + str(format(SetCameraValue_status_width, '02x')))
            (GetCameraValueInt_status, width) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "Width")
            print("Returned width: " + str(width))
            '''

            # Set ROI Height
            '''
            (SetCameraValue_status_height,) = KYFG_SetCameraValue(camHandleArray[grabberIndex][0], "Height", 480)
            print("\nSetCameraValueInt_status_height: " + str(format(SetCameraValue_status_height, '02x')))
            (GetCameraValueInt_status, height) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "Height")
            print("Returned height: " + str(height))
            '''

            # Avaliable on cams with enabled PixelFormat parameter
            '''
            (SetCameraValue_status,) = KYFG_SetCameraValue(camHandleArray[grabberIndex][0], "PixelFormat", "Mono8")
            print("\nPixelFormat status1: " + str(format(SetCameraValue_status, '02x')))
            (SetCameraValue_status,) = KYFG_SetCameraValue(camHandleArray[grabberIndex][0], "PixelFormat", 17301505)
            print("PixelFormat status2: " + str(format(SetCameraValue_status, '02x')))
            (GetCameraValue_status, pixel_format_str, pixel_format_int) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "PixelFormat")
            print("Returned PixelFormat: " + pixel_format_str + " : " + str(pixel_format_int))
            '''

            # Avaliable on cams with enabled BF_AutoLevelAdjust parameter
            '''
            (SetCameraValue_status,) = KYFG_SetCameraValue(camHandleArray[grabberIndex][0], "BF_AutoLevelAdjust", True);
            print("\nBF_AutoLevelAdjust SetCameraValue_status: " + str(format(SetCameraValue_status, '02x')))
            (GetCameraValue_status,auto_level) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "BF_AutoLevelAdjust");
            print("Returned BF_AutoLevelAdjust value: " + str(auto_level))
            '''

            # Avaliable on cams with enabled ExposureTime parameter
            '''
            (SetCameraValue_status,) = KYFG_SetCameraValue(camHandleArray[grabberIndex][0], "ExposureTime", 25.84);
            print("\nExposureTime SetCameraValue_status: " + str(format(SetCameraValue_status, '02x')))
            (SetCameraValue_status, exposure_time) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "ExposureTime");
            print("Returned Exposure Time: " + str(exposure_time))
            '''

            # Avaliable on cams with enabled DeviceUserID parameter
            '''
            (SetCameraValue_status,) = KYFG_SetCameraValue(camHandleArray[grabberIndex][0], "DeviceUserID", "Tester Name");
            print("\nDeviceUserID SetCameraValue_status: " + str(format(SetCameraValue_status, '02x')))
            (SetCameraValue_status, user_id) = KYFG_GetCameraValueStringCopy(camHandleArray[grabberIndex][0], "DeviceUserID");
            print("Returned DeviceUserID: " + user_id)
            '''

            # Avaliable on cams with enabled DeviceUserID parameter - Working on KAYA INSTRUMENTS 19HS
            '''
            (GetCameraValue_status, ex) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "UserMemoryPageSave");
            print("Has UserMemoryPageSave been executed: " + str(ex) 
            (SetCameraValue_status,) = KYFG_SetCameraValue(camHandleArray[grabberIndex][0], "UserMemoryPageAll", bytes([2,3,4,5,6,7]));
            print("Setting  UserMemoryPageAll register status: " + str(format(SetCameraValue_status, '02x')))  
            (SetCameraValue_status,) = KYFG_SetCameraValue(camHandleArray[grabberIndex][0], "UserMemoryPageSave", 0);
            print("Saving UserMemoryPageAll status: " + str(format(SetCameraValue_status, '02x')))
            (GetCameraValue_status, buffer) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "UserMemoryPageAll");
            print("Returned  UserMemoryPageAll register status: " + str(buffer))  
            (GetCameraValue_status, ex) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "UserMemoryPageSave");
            print("Has UserMemoryPageSave been executed: " + str(ex))
            '''

            (StreamCreateAndAlloc_status, buffHandle) = KYFG_StreamCreateAndAlloc(camHandleArray[grabberIndex][0], 16, 0)
            # print("StreamCreateAndAlloc_status: " + str(format(StreamCreateAndAlloc_status, '02x')))

            (CallbackRegister_status) = KYFG_StreamBufferCallbackRegister(buffHandle, Stream_callback_func, py_object(streamInfoStruct))

        elif (c == 's'):
            (CameraStart_status,) = KYFG_CameraStart(camHandleArray[grabberIndex][0], buffHandle, 0)
            # print("CameraStart_status: " + str(format(CameraStart_status, '02x')))

        elif (c == 'o'):
            connection = -1
            try:
                connection = connectToGrabber(grabberIndex)
            except KYException as err:
                print('\n')
                printErr(err, "Could not connect to grabber {0}".format(grabberIndex))
            if (connection == 0):
                (KYDeviceEventCallBackRegister_status,) = KYDeviceEventCallBackRegister(handle[grabberIndex],
                                                                                        Device_event_callback_func, 0)

        elif (c == 't'):
            print('\r', end='')
            sys.stdout.flush()
            (CameraStop_status,) = KYFG_CameraStop(camHandleArray[grabberIndex][0])


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

    input("\nPress enter to exit")

    if (len(camHandleArray[grabberIndex]) > 0):
        (KYFG_CameraClose_status,) = KYFG_CameraClose(camHandleArray[grabberIndex][0])
    if (handle[grabberIndex] != 0):
        (CallbackRegister_status,) = KYFG_StreamBufferCallbackUnregister(handle[grabberIndex], Stream_callback_func)
        (KYFG_Close_status,) = KYFG_Close(handle[grabberIndex])


except KYException as KYe:
    print("KYException occurred: ")
    raise
