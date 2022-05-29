import time

import KYFGLib
from KYFGLib import *
import numpy as np
import ctypes
from matplotlib import pyplot as plt
from PIL import Image


totalFrames = 0
buffSize = 0
buffIndex = 0
buffData: ctypes.c_void_p
np_frames= []

############################ Callback Link Loss Detection ########################

def Device_event_callback_func(userContext, event):
    if (isinstance(event, KYDEVICE_EVENT_CAMERA_CONNECTION_LOST) == True):
        print("KYDEVICE_EVENT_CAMERA_CONNECTION_LOST_ID event recognized")
        print("event_id: " + str(event.deviceEvent.eventId))
        print("cam_handle: " + format(event.camHandle.get(), '02x'))   
        print("device_link: " + str(event.iDeviceLink))
        print("camera_link: " + str(event.iCameraLink))
    elif (isinstance(event, KYDEVICE_EVENT_CAMERA_START) == True):
        print("KYDEVICE_EVENT_CAMERA_START_REQUEST event recognized")
    else:
        print("Unknown event recognized")


############################# Callback Function ##################################

def Stream_callback_func(buffHandle, userContext): 

    global buffData
    global buffSize
    global np_frames

    if (buffHandle == 0 ):
        Stream_callback_func.copyingDataFlag = 0
        return

    (buffSize,) = KYFG_StreamGetSize(buffHandle)
    (status, buffIndex)= KYFG_StreamGetFrameIndex(buffHandle)
    (buffData,) = KYFG_StreamGetPtr(buffHandle, buffIndex)

    if (userContext != 0):
        streamInfo = cast(userContext, py_object).value
        streamInfo.callbackCount = streamInfo.callbackCount + 1
    
    if ( Stream_callback_func.copyingDataFlag == 0):
        Stream_callback_func.copyingDataFlag = 1
    
    #print("\nFrames per stream: " + str(streamInfo.framesPerStream) + ", total callbacks: " + str(streamInfo.callbackCount))
    #print('Good callback buffer handle: ' + str(format(buffHandle, '06x')) + ", current index: " + str(buffIndex) + ", total callbacks: " + str(streamInfo.callbackCount) + "         ", end='\r')
    sys.stdout.flush()

    #np_data = numpy_from_data(buffData, buffSize)
    Stream_callback_func.copyingDataFlag = 0
    np_frames.append(numpy_from_data(buffData, buffSize, streamInfo.datatype).reshape(streamInfo.height, streamInfo.width))
    return


# Example of user class containing stream information
class StreamInfoStruct:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.datatype = 0
        self.callbackCount = 0
        self.framesPerStream = 0
        return

################################ Defines ################################################

MAX_BOARDS = 4

handle = [0 for i in range(MAX_BOARDS)]

detectedCameras = []

grabberIndex = 1

camHandleArray = [[0 for x in range(0)] for y in range(MAX_BOARDS)]

buffHandle = STREAM_HANDLE()

streamInfoStruct = StreamInfoStruct()

Stream_callback_func.data = 0

Stream_callback_func.copyingDataFlag = 0

################################## Control Functions ####################################

def printErr(err, msg = ""):
    print(msg)
    print("Error description: {0}".format(err))


def numpy_from_data(buffData, buffSize, datatype):
    data_pointer= ctypes.cast(buffData, ctypes.c_char_p)
    buffer_from_memory = ctypes.pythonapi.PyMemoryView_FromMemory
    buffer_from_memory.restype = ctypes.py_object
    # buffer_from_memory.restype=ctypes.c_uint16
    buffer = buffer_from_memory(data_pointer, buffSize)
    return np.frombuffer(buffer, datatype)


def connectToGrabber(grabberIndex):
    global handle
    (connected_fghandle,) = KYFG_Open(grabberIndex)
    connected = connected_fghandle.get()
    handle[grabberIndex] = connected
    print ("Good connection to grabber " + str(grabberIndex) + ", handle= " + str(format(connected, '02x')))
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

    c = 'x'
    while (c != 'e'):
        if (c != ''):
            print(
                "\nEnter choice: ([0-4]-select grabber) (o-open grabber) (c-connect to camera)(s-start)(t-stop)(e-exit)(i-camera info)(x-getXML)(f-show images)")
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

            (StreamCreateAndAlloc_status, buffHandle) = KYFG_StreamCreateAndAlloc(camHandleArray[grabberIndex][0], 16, 0)
            # print("StreamCreateAndAlloc_status: " + str(format(StreamCreateAndAlloc_status, '02x')))


        elif (c == 's'):
            (status, height) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "Height")
            (status, width) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "Width")

            streamInfoStruct.width = width
            streamInfoStruct.height = height

            (status, camera_pixel_format_int, camera_pixel_format) = KYFG_GetCameraValue(camHandleArray[grabberIndex][0], "PixelFormat")

            if camera_pixel_format[-1] == "8":
                streamInfoStruct.datatype = np.uint8
            else:
                streamInfoStruct.datatype = np.uint16

            (status, framesPerStream) = KYFG_GetGrabberValue(camHandleArray[grabberIndex][0], "FramesPerStream")

            (CameraStart_status,) = KYFG_CameraStart(camHandleArray[grabberIndex][0], buffHandle, 0)
            # print("CameraStart_status: " + str(format(CameraStart_status, '02x')))

            # Use the number of allocated frames per stream, in order to bound the number of saved and displayed images.
            (status, framesPerStream) = KYFG_GetGrabberValue(handle[grabberIndex], "FramesPerStream")
            streamInfoStruct.framesPerStream = framesPerStream

        elif (c == 'o'):
            connection = -1
            try:
                connection = connectToGrabber(grabberIndex)
            except KYException as err:
                print('\n')
                printErr(err, "Could not connect to grabber {0}".format(grabberIndex))
            if (connection == 0):
                (CallbackRegister_status,) = KYFG_CallbackRegister(handle[grabberIndex], Stream_callback_func, py_object(streamInfoStruct))
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

        elif (c == 'f'):
            image_number = 0
            all_images = len(np_frames)
            plt.ion()  # activates pyplot interactive mode
            for i in np_frames:
                img = Image.fromarray(i, mode='L')  # convert NumPy image array to the PIL image
                #img.show()  # shows image in a standard windows application using PIL
                plt.imshow(img, cmap='gray')
                plt.pause(0.1)  # required to operate with pyplot GUI in interactive mode
                plt.show()
                image_number += 1
                print(f"Image {image_number} of {all_images}")
                time.sleep(1)
            plt.pause(1)
            plt.close('all')
            print("All images were shown!")


    input("\nPress enter to exit")

    if (len(camHandleArray[grabberIndex]) > 0):
        (KYFG_CameraClose_status,) = KYFG_CameraClose(camHandleArray[grabberIndex][0])
    if (handle[grabberIndex] != 0):
        (CallbackRegister_status,) = KYFG_CallbackUnregister(handle[grabberIndex], Stream_callback_func)
        (KYFG_Close_status,) = KYFG_Close(handle[grabberIndex])


except KYException as KYe:
    print("KYException occurred: ")
    raise
