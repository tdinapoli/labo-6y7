from __future__ import print_function
import ctypes
import enum
import sys
import time
import threading
from ctypes import *
from enum import Enum
import sys
import inspect
import platform
import os
import warnings


###################################### Types Section #####################################
AUX_DATA_MAX_SIZE = 16
KY_MAX_CAMERAS = 16
MAX_CAMERA_INFO_STRING_SIZE = 64

class FGHANDLE:
    def __init__(self, val: 'Default:' = 0):
        self.val = val
    def __str__(self):
        return str(self.val)
    def __int__(self):
        return self.val
    def set(self, val):
        self.val = val
    def get(self):
        return self.val

class STREAM_HANDLE(FGHANDLE):
    def __init__(self, val: 'Default:' = 0):
        FGHANDLE.__init__(self,val)
    def __str__(self):
        return str(self.val)
    def __int__(self):
        return self.val
    def set(self, val):
        self.val = val
    def get(self):
        return self.val

class CAMHANDLE:
    def __init__(self, val: 'Default:' = 0):
        self.val = val
    def __str__(self):
        return str(self.val)
    def __int__(self):
        return self.val
    def set(self, val):
        self.val = val
    def get(self):
        return self.val


class KYException(Exception):
    pass


class STREAM_BUFFER_HANDLE:
    def __init__(self, val: 'Default:' = 0):
        self.val = val
    def __int__(self):
        return self.val
    def get(self):
        return self.val
    def set(self, val):
        self.val = val

#----------------------------- KY_DEVICE_PROTOCOL -----------------------------#
class KY_DEVICE_PROTOCOL(Enum):
    KY_DEVICE_PROTOCOL_CoaXPress = 0x0
    KY_DEVICE_PROTOCOL_CLHS = 0x1
    KY_DEVICE_PROTOCOL_GigE = 0x2
    KY_DEVICE_PROTOCOL_Mixed = 0xFF
    KY_DEVICE_PROTOCOL_Unknown = 0xFFFF
    
#----------------------------- PORT_STATUS -----------------------------#
class PORT_STATUS(Enum):
    PORT_DISCONNECTED = 0x00   # the port is disconnected, no link has been established
    PORT_SYNCHRONIZED = 0x01   # port link is synchronized and awaiting connection
    PORT_CONNECTING = 0x10     # a connection is trying to be established on port
    PORT_CONNECTED = 0x11      # port is connected and assigned to camera

#----------------------------- SUBMIT_BUFF_FLAGS -----------------------------#
class SUBMIT_BUFF_FLAGS(Enum):
    SUBMIT_BUFF_REGULAR_BUFFER = 0x00
    SUBMIT_BUFF_PHYSICAL_ADDRESS = 0x01   # provided buffer addresses are physical addresses

#----------------------------- KY_DEVICE_INFO -----------------------------#

class KY_DEVICE_INFO:
    def __init__(self):
        self.version = 0
        self.szDeviceDisplayName = ""
        self.nBus = 0
        self.nSlot = 0
        self.nFunction = 0
        self.DevicePID = 0
        self.isVirtual = 0
        self.m_Flag = 0
        self.m_Protocol = 0
        self.DeviceGeneration = 0

DEV_NAME_STR = c_char * 256
class KY_DEVICE_INFO_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("version", c_uint32),
        ("szDeviceDisplayName", DEV_NAME_STR),
        ("nBus", c_int),
        ("nSlot", c_int),
        ("nFunction", c_int),
        ("DevicePID", c_uint32),
        ("isVirtual", c_byte),
        ("m_Flags", c_byte),
        ("m_Protocol", c_uint),
        ("DeviceGeneration", c_uint32)]
    def __init__(self):
        self.version = 4

#--------------------   KYFGLib_InitParameters -----------------------#
# The original struct defined in KYFGLib_defines.h
class KYFGLib_InitParameters:
    def __init__(self):
        self.version = 2
        # since version 1
        self.concurrency_mode = 0
        self.logging_mode = 0
        # since version 2
        self.noVideoStreamProcess = False

class KYFGLib_InitParameters_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("version", c_uint),
        # since version 1
        ("concurrency_mode", c_uint),
        ("logging_mode", c_uint),
        # since version 2
        ("noVideoStreamProcess", c_bool) ]
    def __init__(self):
        self.version = 2
        # since version 1
        self.concurrency_mode = 0
        self.logging_mode = 0
        # since version 2
        self.noVideoStreamProcess = ctypes.c_bool(False)

#----------------------------- KY_SOFTWARE_VERSION -----------------------------------------#
class KY_SOFTWARE_VERSION:
    def __init__(self):
        self.struct_version = 1  # Must be set to 0 or 1 before calling KY_GetSoftwareVersion() function
        self.Major = 0
        self.Minor = 0
        self.SubMinor = 0
        # since version 1
        self.Beta = 0 # Non-zero value indicates a "Beta build"
        self.RC = 0   # Non-zero value indicates a "Release Candidate build"

class KY_SOFTWARE_VERSION_C_STYLE(Structure):
    _fields_ = [
        ("struct_version", c_uint16),
        ("Major", c_uint16),
        ("Minor", c_uint16),
        ("SubMinor", c_uint16),
        # since version 1
        ("Beta", c_uint16), # Non-zero value indicates a "Beta build"
        ("RC", c_uint16) ]  # Non-zero value indicates a "Release Candidate build"

#----------------------   KYFGLib_CameraScanParameters ----------------------------#
class KYFGLib_CameraScanParameters:
    def __init__(self):
        self.version = 1
        # since version 1
        self.pCamHandleArray = []
        self.nCameraCount = KY_MAX_CAMERAS
        self.bRetainOpenCameras = False

class KYFGLib_CameraScanParameters_C_STYLE(Structure):
    _fields_ = [
        ("version", c_uint32),
        # since version 1
        ("pCamHandleArray", POINTER(c_uint32)),
        ("nCameraCount", c_int),
        ("bRetainOpenCameras", c_bool) ]
    def __init__(self):
        self.version = 1
        pCamHandleArray_p = (c_uint32 * KY_MAX_CAMERAS)(0)
        self.pCamHandleArray = cast(pCamHandleArray_p, POINTER(c_uint32)) #Array of API camera handles of detected cameras
        self.nCameraCount = KY_MAX_CAMERAS
        self.bRetainOpenCameras = c_bool(False)

#----------------------   KYFGCAMERA_INFO ----------------------------#
class KYFGCAMERA_INFO:
    def __init__(self):
        self.master_link = 0
        self.link_mask = 0
        self.link_speed = 0
        self.stream_id = 0
        self.deviceVersion = ""
        self.deviceVendorName = ""
        self.deviceManufacturerInfo = ""
        self.deviceModelName = ""
        self.deviceID = ""
        self.deviceUserID = ""
        self.outputCamera = False
        self.virtualCamera = False
        
CAMERA_INFO_ARRAY = c_char * (MAX_CAMERA_INFO_STRING_SIZE + 1)
class KYFGCAMERA_INFO_C_STYLE(Structure):
    _fields_ = [
        ("master_link", c_ubyte),
        ("link_mask", c_ubyte),
        ("link_speed", c_int),
        ("stream_id", c_uint),
        ("deviceVersion", CAMERA_INFO_ARRAY),
        ("deviceVendorName", CAMERA_INFO_ARRAY),
        ("deviceManufacturerInfo", CAMERA_INFO_ARRAY),
        ("deviceModelName", CAMERA_INFO_ARRAY),
        ("deviceID", CAMERA_INFO_ARRAY),
        ("deviceUserID", CAMERA_INFO_ARRAY),
        ("outputCamera", c_bool),
        ("virtualCamera", c_bool) ]        
        
#----------------------   KYFGCAMERA_INFO2 ----------------------------#
class KYFGCAMERA_INFO2:
    def __init__(self):
        self.version = 0
        self.master_link = 0
        self.link_mask = 0
        self.link_speed = 0
        self.stream_id = 0
        self.deviceVersion = ""
        self.deviceVendorName = ""
        self.deviceManufacturerInfo = ""
        self.deviceModelName = ""
        self.deviceID = ""
        self.deviceUserID = ""
        self.outputCamera = False
        self.virtualCamera = False

CAMERA_INFO2_ARRAY = c_char * (MAX_CAMERA_INFO_STRING_SIZE + 1)
class KYFGCAMERA_INFO2_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("version", c_int),
        ("master_link", c_ubyte),
        ("link_mask", c_ubyte),
        ("link_speed", c_int),
        ("stream_id", c_uint),
        ("deviceVersion", CAMERA_INFO2_ARRAY),
        ("deviceVendorName", CAMERA_INFO2_ARRAY),
        ("deviceManufacturerInfo", CAMERA_INFO2_ARRAY),
        ("deviceModelName", CAMERA_INFO2_ARRAY),
        ("deviceID", CAMERA_INFO2_ARRAY),
        ("deviceUserID", CAMERA_INFO2_ARRAY),
        ("outputCamera", c_bool),
        ("virtualCamera", c_bool) ]


#--------------------   KYFG_AUX_DATA & Dirived ---------------------------#
class KYFG_AUX_DATA:
    messageID = 0
    aux_header_reserved = False
    dataSize = 0

class KYFG_RAW_AUX(KYFG_AUX_DATA):
    data = [0 for i in range(AUX_DATA_MAX_SIZE)]

class KYFG_IO_AUX_DATA(KYFG_AUX_DATA):
    masked_data = 0
    timestamp = 0

class KYFG_FRAME_AUX_DATA(KYFG_AUX_DATA):
    sequence_number = 0
    timestamp = 0
    aux_frame_reserved = 0


#--------------------   KYFG_AUX_DATA_C_STYLE & Dirived ---------------------------#
class KYFG_AUX_DATA_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("messageID", c_uint),
        ("aux_header_reserved", c_ubyte),
        ("dataSize", c_uint64) ]

DATA_ARRAY_TYPE = c_ubyte * AUX_DATA_MAX_SIZE
class KYFG_RAW_AUX_C_STYLE(KYFG_AUX_DATA_C_STYLE):
    _pack_ = 1
    _fields_ = [
        ("data", DATA_ARRAY_TYPE) ]

class KYFG_IO_AUX_DATA_C_STYLE(KYFG_AUX_DATA_C_STYLE):
    _pack_ = 1
    _fields_ = [
        ("masked_data", c_uint64),
        ("timestamp", c_uint64) ]

class KYFG_FRAME_AUX_DATA_C_STYLE(KYFG_AUX_DATA_C_STYLE):
    _pack_ = 1
    _fields_ = [
        ("sequence_number", c_uint),
        ("timestamp", c_uint64),
        ("aux_frame_reserved", c_uint) ]


#--------------------------------------- KY_CAM_PROPERTY_TYPE --------------------------#
class KY_CAM_PROPERTY_TYPE:
    PROPERTY_TYPE_UNKNOWN    = -1
    PROPERTY_TYPE_INT        = 0x00
    PROPERTY_TYPE_BOOL        = 0x01
    PROPERTY_TYPE_STRING    = 0x02
    PROPERTY_TYPE_FLOAT        = 0x03
    PROPERTY_TYPE_ENUM        = 0x04
    PROPERTY_TYPE_COMMAND    = 0x05
    PROPERTY_TYPE_REGISTER    = 0x06

#----------------------------- KY_STREAM_BUFFER_INFO_CMD -----------------------------------------#
class KY_STREAM_BUFFER_INFO_CMD:
    KY_STREAM_BUFFER_INFO_BASE          = 0      # PTR        Base address of the buffer memory.
    KY_STREAM_BUFFER_INFO_SIZE          = 1      # SIZET      Size of the buffer in bytes. */
    KY_STREAM_BUFFER_INFO_USER_PTR      = 2      # PTR        Private data pointer for the stream buffer. */
    KY_STREAM_BUFFER_INFO_TIMESTAMP     = 3      # UINT64     Timestamp the buffer was acquired. */
    KY_STREAM_BUFFER_INFO_INSTANTFPS    = 4      # FLOAT64    Instant FPS calculated from current and previous timestamp */
    KY_STREAM_BUFFER_INFO_ID            = 1000   # UINT32      Unique id of buffer in the stream */


#----------------------------- KY_ACQ_QUEUE_TYPE -----------------------------------------#
class KY_ACQ_QUEUE_TYPE:
    KY_ACQ_QUEUE_INPUT      =   0   # buffers in INPUT queue are ready to be filled with data
    KY_ACQ_QUEUE_OUTPUT     =   1   # buffers in OUTPUT queue have been filled and awaiting user processing
    KY_ACQ_QUEUE_UNQUEUED   =   2   # buffers in UNQUEUED set have been anounced but are inactive for acquisition mechanisem. By default all buffers are placed in UNQUEUED set
    KY_ACQ_QUEUE_AUTO       =   3


#----------------------------- KY_AuthKey -----------------------------------------#
KY_AUTHKEY_SIZE = 32

class KY_AuthKey:
    secret = [0 for i in range(KY_AUTHKEY_SIZE)]

class KY_AuthKey_C_STYLE:
    secret = (c_ubyte * KY_AUTHKEY_SIZE)()

#----------------------------- KY_DATA_TYPE -----------------------------------------#
class KY_DATA_TYPE:
    KY_DATATYPE_UNKNOWN     = 0       # Unknown data type
    KY_DATATYPE_STRING      = 1       # NULL-terminated C string (ASCII encoded).
    KY_DATATYPE_STRINGLIST  = 2       # Concatenated INFO_DATATYPE_STRING list. End of list is signaled with an additional NULL.
    KY_DATATYPE_INT16       = 3       # Signed 16 bit integer.
    KY_DATATYPE_UINT16      = 4       # Unsigned 16 bit integer
    KY_DATATYPE_INT32       = 5       # Signed 32 bit integer
    KY_DATATYPE_UINT32      = 6       # Unsigned 32 bit integer
    KY_DATATYPE_INT64       = 7       # Signed 64 bit integer
    KY_DATATYPE_UINT64      = 8       # Unsigned 64 bit integer
    KY_DATATYPE_FLOAT64     = 9       # Signed 64 bit floating point number.
    KY_DATATYPE_PTR         = 10      # Pointer type (void*). Size is platform dependent (32 bit on 32 bit platforms).
    KY_DATATYPE_BOOL8       = 11      # Boolean value occupying 8 bit. 0 for false and anything for true.
    KY_DATATYPE_SIZET       = 12      # Platform dependent unsigned integer (32 bit on 32 bit platforms).
    KY_DATATYPE_BUFFER      = 13      # Like a INFO_DATATYPE_STRING but with arbitrary data and no NULL termination.


#----------------------------- KY_STREAM_INFO_CMD -----------------------------------------#
class KY_STREAM_INFO_CMD:
    KY_STREAM_INFO_PAYLOAD_SIZE                         =  7   # Size of the expected data in bytes. */
    KY_STREAM_INFO_BUF_ALIGNMENT                        = 13   # Buffer memory alignment in bytes. */
    KY_STREAM_INFO_PAYLOAD_SIZE_INCREMENT_FACTOR        = 1000 # Payload size should be divisible by increment factor. */
    KY_STREAM_INFO_BUF_COUNT                            = 2000 # Number of buffers in the stream. */
    KY_STREAM_INFO_INSTANTFPS                           = 2001 # Last calculated FPS. Valid after at least two frames have been acquired*/

#----------------------------- Device Event Structures -----------------------------------------#
class KYDEVICE_EVENT_ID:
    KYDEVICE_EVENT_CAMERA_START_REQUEST                         =  0
    KYDEVICE_EVENT_CAMERA_CONNECTION_LOST_ID                    =  1
    KYDEVICE_EVENT_SYSTEM_TEMPERATURE_ID                        =  2
    KYDEVICE_EVENT_CXP2_HEARTBEAT_ID                            =  3
    KYDEVICE_EVENT_CXP2_EVENT_ID                                =  4
    KYDEVICE_EVENT_GENCP_EVENT_ID                               =  5
    KYDEVICE_EVENT_GIGE_EVENTDATA_ID                            =  6

class KYDEVICE_EVENT:
    eventId = 0
class KYDEVICE_EVENT_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("eventId", c_uint) ]

#------------------- KYDEVICE_EVENT_CAMERA_START Structures ---------------------#
class KYDEVICE_EVENT_CAMERA_START:
    deviceEvent: KYDEVICE_EVENT
    camHandle: CAMHANDLE
class KYDEVICE_EVENT_CAMERA_START_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("deviceEvent", c_uint),
        ("camHandle", c_uint) ]

#-------------- KYDEVICE_EVENT_CAMERA_CONNECTION_LOST Structures ----------------#
class KYDEVICE_EVENT_CAMERA_CONNECTION_LOST:
    deviceEvent: KYDEVICE_EVENT
    camHandle: CAMHANDLE
    iDeviceLink: int
    iCameraLink: int
class KYDEVICE_EVENT_CAMERA_CONNECTION_LOST_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("deviceEvent", KYDEVICE_EVENT_C_STYLE),
        ("camHandle", c_uint),
        ("iDeviceLink", c_uint64),
        ("iCameraLink", c_uint64) ]

#--------------- KYDEVICE_EVENT_SYSTEM_TEMPERATURE Structures -----------------#
class KYDEVICE_EVENT_SYSTEM_TEMPERATURE_THRESHOLDS_ID(Enum):
    KYDEVICE_EVENT_SYSTEM_TEMPERATURE_NORMAL        =   0
    KYDEVICE_EVENT_SYSTEM_TEMPERATURE_WARNING       =   1
    KYDEVICE_EVENT_SYSTEM_TEMPERATURE_CRITICAL      =   2

class KYDEVICE_EVENT_SYSTEM_TEMPERATURE:
    deviceEvent: KYDEVICE_EVENT
    temperatureThresholdId: KYDEVICE_EVENT_SYSTEM_TEMPERATURE_THRESHOLDS_ID

class KYDEVICE_EVENT_SYSTEM_TEMPERATURE_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("deviceEvent", KYDEVICE_EVENT_C_STYLE),
        ("temperatureThresholdId", c_int) ]

#---------------------- KY_CXP2_HEARTBEAT Structures ------------------------#
class KY_CXP2_HEARTBEAT:
    masterHostConnectionID: int
    cameraTime: int
class KY_CXP2_HEARTBEAT_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("masterHostConnectionID", c_uint32),   # according to CXP 2.0 standard, holds the Host Connection ID of the Host connection
                                                # connected to the Device Master connection
        ("cameraTime", c_uint64)]               # The Device time is expressed in nanoseconds.
                                                # Note that this field is called "Device time" in the CXP standard but in this API the
                                                # notion "device" is used for PCI devices - grabbers and simulators

class KYDEVICE_EVENT_CXP2_HEARTBEAT:
    deviceEvent: KYDEVICE_EVENT
    camHandle: CAMHANDLE
    heartBeat: KY_CXP2_HEARTBEAT
class KYDEVICE_EVENT_CXP2_HEARTBEAT_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("deviceEvent", KYDEVICE_EVENT_C_STYLE),
        ("camHandle", c_uint),
        ("heartBeat", KY_CXP2_HEARTBEAT_C_STYLE) ]

#---------------------- KY_CXP2_EVENT Structures ------------------------#
KY_CXP_EVENT_MAX_DATA_SIZE  = 256 # 1024 / 4  according to CXP 2.0 standard
CXP_EVENT_DATA_WORD = c_uint32 * 256
class KY_CXP2_EVENT:
    masterHostConnectionID: int
    tag: int
    dataSize: int
    dataWords = [0 for i in range(KY_CXP_EVENT_MAX_DATA_SIZE)]
class KY_CXP2_EVENT_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("masterHostConnectionID", c_uint32),   # according to CXP 2.0 standard, holds the Host Connection ID of the Host connection
                                                # connected to the Device Master connection
        ("tag", c_uint8),                       # 8 bit tag. Incremented for each new Event packet.
        ("dataSize", c_uint16),                 # the number of event data words, Maximum size = CXP_EVENT_MAX_DATA_SIZE bytes according to CXP 2.0 standard
        ("dataWords", CXP_EVENT_DATA_WORD) ]    # 'dataSize' words with one or more event messages

class KYDEVICE_EVENT_CXP2_EVENT:
    deviceEvent: KYDEVICE_EVENT
    camHandle: CAMHANDLE
    cxp2Event: KY_CXP2_EVENT
class KYDEVICE_EVENT_CXP2_EVENT_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("deviceEvent", KYDEVICE_EVENT_C_STYLE),
        ("camHandle", c_uint),
        ("cxp2Event", KY_CXP2_EVENT_C_STYLE) ]

#----------------- KYDEVICE_EVENT_GENCP_EVENT Structures ------------------#
KY_GENCP_EVENT_MAX_DATA_SIZE = 1024
GENCP_EVENT_DATA = c_uint8 * 1024
class KY_GENCP_EVENT:
    eventSize: int
    eventId: int
    timestamp: int
    data = [0 for i in range(KY_GENCP_EVENT_MAX_DATA_SIZE)]
class KY_GENCP_EVENT_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("eventSize", c_uint16),        # Size of event data object in bytes including event_size, event_id, timestamp and optional data.
        ("eventId", c_uint16),          # The event_id is a number identifying an event source.
        ("timestamp", c_uint64),        # 64 bit timestamp value in ns as defined in the timestamp bootstrap register.
        ("data", GENCP_EVENT_DATA) ]    # data payload with valid size of 'dataSize'

class KYDEVICE_EVENT_GENCP_EVENT:
    deviceEvent: KYDEVICE_EVENT
    srcDevicePort: int
    gencpEvent: KY_CXP2_EVENT
class KYDEVICE_EVENT_GENCP_EVENT_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("deviceEvent", KYDEVICE_EVENT_C_STYLE),
        ("srcDevicePort", c_int),
        ("gencpEvent", KY_GENCP_EVENT_C_STYLE) ]

#----------------- KYDEVICE_EVENT_GIGE_EVENTDATA Structures ------------------#
KY_GIGE_EVENTDATA_EVENT_MAX_DATA_SIZE = 512
GIGE_EVENT_DATA = c_uint8 * 512
class KY_GIGE_EVENTDATA_EVENT:
    eventSize: int
    eventId: int
    streamChannel: int
    blockId: int
    timestamp: int
    data = [0 for i in range(KY_GIGE_EVENTDATA_EVENT_MAX_DATA_SIZE)]
class KY_GIGE_EVENTDATA_EVENT_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("eventSize", c_uint16),        # Size of event data object in bytes including event_size, event_id, timestamp and optional data.
        ("eventId", c_uint16),          # The event_id is a number identifying an event source.
        ("streamChannel", c_uint16),
        ("blockId", c_uint16),
        ("timestamp", c_uint64),        # 64 bit timestamp value in ns as defined in the timestamp bootstrap register.
        ("data", GIGE_EVENT_DATA) ]     # data payload with valid size of 'dataSize'

class KYDEVICE_EVENT_GIGE_EVENTDATA:
    deviceEvent: KYDEVICE_EVENT
    srcDevicePort: int
    gigeEvent: KY_GIGE_EVENTDATA_EVENT
class KYDEVICE_EVENT_GIGE_EVENTDATA_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("deviceEvent", KYDEVICE_EVENT_C_STYLE),
        ("srcDevicePort", c_int),
        ("gigeEvent", KY_GIGE_EVENTDATA_EVENT_C_STYLE) ]


#--------------------------- CXP 2 GenerateCxpEvent() Structures -------------------------------#
class KY_CXPEVENT_NAMESPACE:
    KY_CXPEVENT_GENICAM                      =  0
    KY_CXPEVENT_COAXPRESS                    =  1
    KY_CXPEVENT_SPECIFIC                     =  2
    KY_CXPEVENT_RESERVED                     =  3

class KY_CXPEVENT_PACK:
    nDataWords: int
    eventDataWord = [0 for i in range(256)]

DATA_WORD = c_uint32 * 256
class KY_CXPEVENT_PACK_C_STYLE(Structure):
    _pack_ = 1
    _fields_ = [
        ("nDataWords", c_uint16),      # Number of data WORDS in 'eventDataWord'
        ("eventDataWord", DATA_WORD)]  # according to CXP standard, there can be maximum 1024 bytes of data

#----------------------------- Ramp pattern type Structure -------------------------------------#
class PATTERN_TYPE:
    PATTERN_XRAMP                     =  0
    PATTERN_XRAMP_COLOR               =  1
    PATTERN_YRAMP                     =  2
    PATTERN_YRAMP_COLOR               =  3
    PATTERN_XYRAMP                    =  4
    PATTERN_XYRAMP_COLOR              =  5
    PATTERN_FIXED                     =  6


###################################### Utilites ###########################################

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def dbg_print(formatted_string):
    #print(formatted_string)
    pass


################################ Global Defines ###########################################
CallBackFunc_ref = 0
CameraCallBackFunc_ref = 0
StreamBufferCallbackFunc_ref = 0
FGAuxDataCallbackFunc_ref = 0
KYDeviceEventCallBack_ref = 0
KYDeviceEventCallBack_INTERNAL_ref = 0

kyExceptionsEnabled = True

#kydll = 4
CallBackFunc_ref = 0
CameraCallBackFunc_ref = 0
MAXBOARDS = 4

################################ STATUS DEFINES ###########################################
ERROR_STATUS = {
    0x2000: 'CSSTATUS_OK',
    0x2001: 'CSSTATUS_UNKNOWN_SIM_HANDLE',
    0x2002: 'CSSTATUS_HW_NOT_FOUND',
    0x2003: 'CSSTATUS_BUSY',
    0x2004: 'CSSTATUS_FILE_NOT_FOUND',
    0x2005: 'CSSTATUS_FILE_READ_ERROR',
    0x2006: 'CSSTATUS_CONFIG_NOT_LOADED',
    0x2007: 'CSSTATUS_INVALID_VALUE',
    0x2008: 'CSSTATUS_MAX_CONNECTIONS',
    0x2009: 'CSSTATUS_COULD_NOT_STOP',
    0x200A: 'CSSTATUS_CANNOT_LOAD_IMAGE_FILE',
    0x200B: 'CSSTATUS_MEMORY_ERROR',
    0x200C: 'CSSTATUS_UNKNOWN_SIM_CONTROL',
    0x200D: 'CSSTATUS_WRONG_PARAMETER_NAME',
    0x200E: 'CSSTATUS_WRONG_PARAMETER_TYPE',
    0x200F: 'CSSTATUS_GENICAM_EXCEPTION',
    0x2010: 'CSSTATUS_OUT_OF_RANGE_ADDRESS',
    0x2011: 'CSSTATUS_PATH_INVALID',
    0x2012: 'CSSTATUS_FILE_TYPE_INVALID',
    0x2013: 'CSSTATUS_UNSUPPORTED_IMAGE',
    0x2014: 'CSSTATUS_UNSUPPORTED_IMAGE_CONVERSION',
    0x2015: 'CSSTATUS_UNSUPPORTED_DEPTH_CONVERSION',
    0x2016: 'CSSTATUS_INVALID_VALUES_FILE',
    0x2017: 'CSSTATUS_FILE_WRITE_ERROR',
    0x2018: 'CSSTATUS_BUFFER_NOT_LOADED',
    0x2019: 'CSSTATUS_TRIGGER_NOT_SET',
    0x201A: 'CSSTATUS_CANNOT_SET_USER_REGISTER_ADDRESS',
    0x201B: 'CSSTATUS_CANNOT_READ_USER_REGISTER',
    0x201C: 'CSSTATUS_CANNOT_WRITE_USER_REGISTER',
    0x201D: 'CSSTATUS_CANNOT_WRITE_REGISTER',
    0x201E: 'CSSTATUS_IMAGE_HEADER_INJECTION_SIZE_TOO_BIG',
    0x201F: 'CSSTATUS_NO_EXTENDED_HW_FEATURES',
    0x2020: 'CSSTATUS_MAX_USER_ADDRESS_EXCEEDED',


    0x3000: 'FGSTATUS_OK',
    0x3001: 'FGSTATUS_UNKNOWN_HANDLE',
    0x3002: 'FGSTATUS_HW_NOT_FOUND',
    0x3003: 'FGSTATUS_BUSY',
    0x3004: 'FGSTATUS_FILE_NOT_FOUND',
    0x3005: 'FGSTATUS_FILE_READ_ERROR',
    0x3006: 'FGSTATUS_CONFIG_NOT_LOADED',
    0x3007: 'FGSTATUS_INVALID_VALUE',
    0x3008: 'FGSTATUS_MAX_CONNECTIONS',
    0x3009: 'FGSTATUS_MEMORY_ERROR',
    0x300A: 'FGSTATUS_WRONG_PARAMETER_NAME',
    0x300B: 'FGSTATUS_WRONG_PARAMETER_TYPE',
    0x300C: 'FGSTATUS_GENICAM_EXCEPTION',
    0x300D: 'FGSTATUS_OUT_OF_RANGE_ADDRESS',
    0x300E: 'FGSTATUS_COULD_NOT_START',
    0x300F: 'FGSTATUS_COULD_NOT_STOP',
    0x3010: 'FGSTATUS_XML_FILE_NOT_LOADED',
    0x3011: 'FGSTATUS_INVALID_VALUES_FILE',
    0x3012: 'FGSTATUS_NO_REQUIRED_PARAMETERS_SECTION',
    0x3013: 'FGSTATUS_WRONG_PARAMETERS_SECTION',
    0x3014: 'FGSTATUS_VALUE_HAS_NO_SELECTOR',
    0x3015: 'FGSTATUS_CALLBACK_NOT_ASSIGNED',
    0x3016: 'FGSTATUS_HANDLE_DOES_NOT_MATCH_CONFIG',
    0x3017: 'FGSTATUS_BUFFER_TOO_SMALL',
    0x3018: 'FGSTATUS_BUFFER_UNSUPPORTED_SIZE',
    0x3019: 'FGSTATUS_GRABBER_FIRMWARE_NOT_SUPPORTED',
    0x301A: 'FGSTATUS_PARAMETER_NOT_WRITABLE',
    0x301B: 'FGSTATUS_CANNOT_START_HW_STREAM',
    0x301C: 'FGSTATUS_WRONG_SCHEMA_VERSION',
    0x301D: 'FGSTATUS_CAMERA_OR_GRABBER_SECTION_NOT_ARRAY',
    0x301E: 'FGSTATUS_ROOT_IS_NOT_OBJECT',
    0x301F: 'FGSTATUS_NO_PARAMETER_TYPE',
    0x3020: 'FGSTATUS_FILE_CREATE_ERROR',
    0x3021: 'FGSTATUS_COULD_NOT_STOP_STREAM',
    0x3022: 'FGSTATUS_BUFFER_MEMORY_OVERLAP',
    0x3023: 'FGSTATUS_UNSUPPORTED_PARAMETER_TYPE',
    0x3100: 'FGSTATUS_EXCEEDED_MAX_CAMERA_CONNECTIONS',
    0x3101: 'FGSTATUS_QUEUED_BUFFERS_NOT_SUPPORTED',
    0x3102: 'FGSTATUS_DESTINATION_QUEUE_NOT_SUPPORTED',
    0x3103: 'FGSTATUS_INVALID_STREAM_INFO_CMD',
    0x3104: 'FGSTATUS_INVALID_STREAM_BUFFER_INFO_CMD',
    0x3105: 'FGSTATUS_STREAM_NOT_CREATED',
    0x3106: 'FGSTATUS_GRABBER_NOT_CONNECTED',
    0x3107: 'FGSTATUS_CAMERA_NOT_CONNECTED',
    0x3200: 'FGSTATUS_CAMERA_NODES_NOT_INITIALIZED',
    0x3300: 'FGSTATUS_UPDATE_WRONG_VID',
    0x3301: 'FGSTATUS_UPDATE_WRONG_BOARD_ID',
    0x3500: 'FGSTATUS_LICENSE_NOT_VALID',
    0x3501: 'FGSTATUS_LICENSE_ALREADY_STARTED_TRIAL',
    0x3FFF: 'FGSTATUS_UNKNOWN_ERROR',

    0x4001: 'INPUT_ARGUMENT_TYPE_ERROR',
    0x4002: 'KYFGLIB_DLL_NOT_FOUND',
    0x4003: 'KYPY_STATUS_INVALID_FGHANDLE',
    0x4004: 'INVALID_INPUT_ARGUMENT'
}


INVALID_FGHANDLE_VAL = 4294967295 # legacy code
INVALID_FGHANDLE  = 4294967295    # INVALID_FGHANDLE as defined in C library

FGSTATUS_WRONG_PARAMETER_NAME = 0x300A
CSSTATUS_OK = 0x2000
FGSTATUS_OK = 0x3000

FGSTATUS_INVALID_VALUE = 0x3007

INPUT_ARGUMENT_TYPE_ERROR = 0x4001
KYFGLIB_DLL_NOT_FOUND = 0x4002
KYPY_STATUS_INVALID_FGHANDLE = 0x4003
INVALID_INPUT_ARGUMENT = 0x4004

FGSTATUS_UNKNOWN_HANDLE = 0x3001

FGSTATUS_LICENSE_NOT_VALID = 0x3500
FGSTATUS_LICENSE_ALREADY_STARTED_TRIAL = 0x3501

INVALID_INT_PARAMETER_VALUE = 9223372036854775807
INVALID_FLOAT_PARAMETER_VALUE = 1.7976931348623158e+308
################################ Routines ###########################################

def disable_exceptions():
    global kyExceptionsEnabled
    kyExceptionsEnabled = False
def enable_exceptions():
    global kyExceptionsEnabled
    kyExceptionsEnabled = True
def exceptions_enabled():
    global kyExceptionsEnabled
    return kyExceptionsEnabled

def return_status(error_code):
    # If Status OK
    if (error_code == CSSTATUS_OK or error_code == FGSTATUS_OK):
        return error_code
    # If there is an errror and Exceptions Enabled
    if (exceptions_enabled() == True):
        raise KYException(ERROR_STATUS[error_code])
    # If there is an errror and Exceptions Disabled
    return error_code


def return_handle(fghandle):
    if (fghandle != INVALID_FGHANDLE):
        return FGHANDLE(fghandle)
    if (exceptions_enabled() == True):
        raise KYException(ERROR_STATUS[FGSTATUS_UNKNOWN_HANDLE])
    # If there is an errror and Exceptions Disabled
    return FGHANDLE(fghandle)

########################################################################################################
########################################################################################################
##################################### Verified Functions ###############################################
########################################################################################################
########################################################################################################
import struct
def is_python_64bit():
    return (struct.calcsize("P") == 8)

def KYFG_Init(KYFGLib_name: 'Default' = "KYFGLib_vc141.dll"):
    global kydll
    if ( isinstance(KYFGLib_name,str) == False ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if platform.system() == "Windows":
        local_env = os.environ
        if sys.version_info.minor > 7:
            os.add_dll_directory(os.environ['KAYA_VISION_POINT_BIN_PATH'])
        if "KAYA_DEVENV_ROOT_DIR" in os.environ:
            vs_platform = "x64" if is_python_64bit() else "Win32"
            local_bin = local_env["KAYA_DEVENV_ROOT_DIR"] + "\\" + local_env["KAYA_VISION_POINT_TESTDIR_NAME"] + "\\" + vs_platform + "\\Common\\Bin"
            local_env['PATH'] = local_bin + ";" + local_env['PATH']
            #print("os.environ['PATH']: {0}".format(os.environ['PATH']))

        kydll = ctypes.CDLL(KYFGLib_name)
    else:
        #import cv2; print(cv2.__version__) #just gives more precise diagnostics if case ctypes.CDLL below results in (opencv-related) undefined symbol error (_ZTIN2cv9Exception)

        KYFGLib_name = "libKYFGLib.so"
        try:
            KAYA_VISION_POINT_LIB_PATH = os.environ['KAYA_VISION_POINT_LIB_PATH']
            #print("KAYA_VISION_POINT_LIB_PATH: " + KAYA_VISION_POINT_LIB_PATH)
        except KeyError as err:
            print("\nCould not retieve value of  location of KAYA_VISION_POINT_LIB_PATH, error: {0}".format(err))
            exit()

        try:
            #kydll = ctypes.CDLL(KAYA_VISION_POINT_LIB_PATH + "/" + KYFGLib_name, mode=ctypes.RTLD_NOW) # results in error: module 'ctypes' has no attribute 'RTLD_NOW',
                                                                                                        # so we'll use os.environ:
            os.environ['LD_BIND_NOW'] = "1" # see https://linux.die.net/man/3/dlopen for environment variable LD_BIND_NOW
            kydll = ctypes.CDLL(KAYA_VISION_POINT_LIB_PATH + "/" + KYFGLib_name)
        except Exception as err:
            print("Could not load KYFGLib, error: {0}".format(err))
            exit(1)


# Next will be executed after beeing imported
if __name__ == 'KYFGLib':
    KYFG_Init()

    

##################################### Connection and Info ############################################### 

   
'''
@brief:
    Retrieves current KAYA softwar and driver information
@params:
@return (Status, SoftwareVersion):
    FGSTATUS - Error code of function execution status
    SoftwareVersion - structure with info about the software. Type: KY_SOFTWARE_VERSION
'''
def  KY_GetSoftwareVersion():
    KY_SOFTWARE_VERSION_C_STYLE_POINTER = POINTER(KY_SOFTWARE_VERSION_C_STYLE)
    kydll.KY_GetSoftwareVersion.argtypes = (KY_SOFTWARE_VERSION_C_STYLE_POINTER,)
    kydll.KY_GetSoftwareVersion.restype = c_uint32

    soft_ver = KY_SOFTWARE_VERSION_C_STYLE()
    soft_ver.struct_version = 1
    KY_GetSoftwareVersion_status = kydll.KY_GetSoftwareVersion(byref(soft_ver))

    if (KY_GetSoftwareVersion_status != FGSTATUS_OK):
        return (return_status(KY_GetSoftwareVersion_status),)

    SoftwareVersion = KY_SOFTWARE_VERSION()
    SoftwareVersion.struct_version = soft_ver.struct_version
    SoftwareVersion.Major = soft_ver.Major
    SoftwareVersion.Minor = soft_ver.Minor
    SoftwareVersion.SubMinor = soft_ver.SubMinor
    SoftwareVersion.Beta = soft_ver.Beta
    SoftwareVersion.RC = soft_ver.RC

    return (return_status(KY_GetSoftwareVersion_status), SoftwareVersion)
   
   
'''
@brief:
    Initializes KYFGLib library providing various parameters.  
@params:
    initParams - initialize parameters
@return (Status,):
    Status - INPUT_ARGUMENT_TYPE_ERROR / FGSTATUS_OK
@note:
    An optional call before KYFGScan().
'''
def KYFGLib_Initialize(initParams):
    if (isinstance(initParams, KYFGLib_InitParameters) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR), 0)
    KYFGLib_InitParameters_C_STYLE_POINTER = POINTER(KYFGLib_InitParameters_C_STYLE)
    kydll.KYFGLib_Initialize.argtypes = (KYFGLib_InitParameters_C_STYLE_POINTER,)
    kydll.KYFGLib_Initialize.restype = c_uint32

    init_params = KYFGLib_InitParameters_C_STYLE()
    init_params.version = c_uint(initParams.version)
    init_params.concurrency_mode = c_uint(initParams.concurrency_mode)
    init_params.logging_mode = c_uint(initParams.logging_mode)
    init_params.noVideoStreamProcess = c_bool(initParams.noVideoStreamProcess)

    KYFGLib_Initialize_status = kydll.KYFGLib_Initialize(byref(init_params))
    if (KYFGLib_Initialize_status != FGSTATUS_OK):
        dbg_print('Error while KYFGLib_Initialize() processing. Status: KYFGLib_Initialize_status\n')
        return (return_status(INVALID_INPUT_ARGUMENT),)
    dbg_print('KYFGLib_Initialize done\n')
    return (return_status(FGSTATUS_OK))


'''
@brief:
    Scan for available devices
@params:
@return (Status, KYFG_Scan_dev_num, pids_info):
    Status - FGSTATUS_OK / INPUT_ARGUMENT_TYPE_ERROR / KYFGLIB_DLL_NOT_FOUND
    KYFG_Scan_dev_num - Number of connected hardware and virtual devices.
    pids_info - List of scanned devices. Type: list
@note:
    DEPRECATED - please use function 'KY_DeviceScan()'
'''
def KYFG_Scan():
    warnings.warn("Function 'KYFG_Scan()' is deprecated, please use function 'KY_DeviceScan()'.", DeprecationWarning)
    global kydll
    if ( isinstance(kydll,ctypes.CDLL) == False ):
        return (return_status(KYFGLIB_DLL_NOT_FOUND),)

    # Retrieve thew number of of devices
    KYFG_Scan_dev_num = kydll.KYFG_Scan(None, 0)

    # Create pythonic and c style arrays to be filled with pids info
    pids_info = []
    temp_arr = (c_uint * KYFG_Scan_dev_num)(0)
    temp_arr_c_uint32_p = pointer(temp_arr)

    # Get the pids info
    KYFG_Scan_dev_num = kydll.KYFG_Scan(temp_arr_c_uint32_p, KYFG_Scan_dev_num)

    # Update the pythonic list
    for i in range(KYFG_Scan_dev_num):
        pids_info.append(temp_arr[i])

    return (return_status(FGSTATUS_OK), KYFG_Scan_dev_num, pids_info)


'''
@brief:
    Scan for available devices
@params:
@return (Status, KYFG_Scan_dev_num):
    Status - FGSTATUS_OK / FGSTATUS_INVALID_VALUE / KYFGLIB_DLL_NOT_FOUND
    KYFG_Scan_dev_num - Number of connected hardware and virtual devices.
'''
def KY_DeviceScan():
    global kydll
    if ( isinstance(kydll,ctypes.CDLL) == False ):
        return (return_status(KYFGLIB_DLL_NOT_FOUND),)
    
    # Retrieve the number of devices
    dev_num = c_uint(0)
    KYFG_Scan_status = kydll.KY_DeviceScan(byref(dev_num))

    return (return_status(KYFG_Scan_status), dev_num.value)


'''
@brief:
    Connect to specific device without loading a project
@params:
    deviceIndex - The index, from scan result array acquired with KYFG_Scan() function, of the device to open. Type: int
@return (FGHANDLE,):
    FGHANDLE - API handle to Frame Grabber device. Type: int
'''
def KYFG_Open(deviceIndex):
    if (isinstance(deviceIndex, int) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_Open.argtypes = (c_int,)
    kydll.KYFG_Open.restype = c_uint32
    connected = kydll.KYFG_Open(deviceIndex)

    if (connected != INVALID_FGHANDLE):
        return (FGHANDLE(connected),)
    if (exceptions_enabled() == True):
        raise KYException(ERROR_STATUS[KYPY_STATUS_INVALID_FGHANDLE])
    # If there is an errror and Exceptions Disabled
    return (FGHANDLE(KYPY_STATUS_INVALID_FGHANDLE),)


'''
@brief:
    Connect to specific device and optionally load a project
@params:
    index - The index, from scan result array acquired with KYFG_Scan() function, of the device to open. Type: int
    projectFile - full path of a project file with saved values, can be null
@return (FGHANDLE,):
    FGHANDLE - API handle to the opened device. Type: int
''' 
def KYFG_OpenEx(index, projectFile):
    kydll.KYFG_OpenEx.argtypes = (c_uint, c_void_p)
    kydll.KYFG_OpenEx.restype = c_uint32
    projectFile_str_buf = create_string_buffer(bytes(projectFile.encode()))
    if (isinstance(index, int) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    elif ( (isinstance(projectFile, str) == True) or (isinstance(projectFile, int) and (projectFile == 0)) ):
        OpenEx_status = kydll.KYFG_OpenEx(index, projectFile_str_buf)
    else:
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)

    if (OpenEx_status != INVALID_FGHANDLE):
        return (FGHANDLE(OpenEx_status),)
    if (exceptions_enabled() == True):
        raise KYException(ERROR_STATUS[KYPY_STATUS_INVALID_FGHANDLE])
    # If there is an errror and Exceptions Disabled
    return (FGHANDLE(KYPY_STATUS_INVALID_FGHANDLE),)

   
'''
@brief:
    Discovered device display name
@params:
    x - Discovered device index
@return (Status, Name):
    Status - INPUT_ARGUMENT_TYPE_ERROR / INVALID_INPUT_ARGUMENT /FGSTATUS_OK
    dev_name - The name of device issued by the specified index.
@note:
    DEPRECATED - please use KY_DeviceInfo(x) instead
'''
def KY_DeviceDisplayName(x):
    warnings.warn("Function 'KY_DeviceDisplayName()' is deprecated, please use function 'KY_DeviceInfo()'.", DeprecationWarning)
    if ( isinstance(x,int) == False ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KY_DeviceDisplayName.argtypes = (c_int,)
    kydll.KY_DeviceDisplayName.restype = c_char_p
    dev_name = kydll.KY_DeviceDisplayName(x)
    if (dev_name is None):
        return (return_status(INVALID_INPUT_ARGUMENT),)
    return (return_status(FGSTATUS_OK), dev_name.decode())


'''
@brief:
    Fills KY_DEVICE_INFO struct with relevant info
@params:
    x - Discovered device index
@return (Status, devInfo):
    Status - INPUT_ARGUMENT_TYPE_ERROR / FGSTATUS_OK
    devInfo - structure with info about the relevant device. Type: KY_DEVICE_INFO
@note:
    Since 'KY_DeviceDisplayName' is now deprecated, the next function used also to retrieve the device name
'''
def KY_DeviceInfo(x):
    if ( isinstance(x,int) == False ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    KY_DEVICE_INFO_C_STYLE_POINTER = POINTER(KY_DEVICE_INFO_C_STYLE)
    dev_info = KY_DEVICE_INFO_C_STYLE()
    dev_info_p = pointer(dev_info)
    kydll.KY_DeviceInfo.argtypes = (c_int, KY_DEVICE_INFO_C_STYLE_POINTER)
    kydll.KY_DeviceInfo.restype = c_uint32
    KY_DeviceInfo_status = kydll.KY_DeviceInfo(x, byref(dev_info))
    if (KY_DeviceInfo_status != FGSTATUS_OK):
        return (return_status(INVALID_INPUT_ARGUMENT),)
    devInfo = KY_DEVICE_INFO()
    devInfo.version = dev_info.version
    devInfo.szDeviceDisplayName = dev_info.szDeviceDisplayName.decode()
    devInfo.nBus = dev_info.nBus
    devInfo.nSlot = dev_info.nSlot
    devInfo.nFunction = dev_info.nFunction
    devInfo.DevicePID = dev_info.DevicePID
    devInfo.isVirtual = dev_info.isVirtual
    devInfo.protocol = KY_DEVICE_PROTOCOL(dev_info.m_Protocol)
    return (return_status(KY_DeviceInfo_status), devInfo)
    
    
'''
@brief:
    Closes the specified device
@params:
    handle - API handle to chosen davice. Type: int or FGHANDLE
@return (FGSTATUS,):
    FGSTATUS - The return status of the function
'''
def KYFG_Close(handle):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_Close.argtypes = (c_uint,)
    kydll.KYFG_Close.restype = c_uint32
    KYFG_Close_status = kydll.KYFG_Close(handle)
    return (return_status(KYFG_Close_status),)
  
  

##################################### Camera Configurations ############################################### 


'''
@brief:
    Scans for the cameras connected to the Frame Grabber
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
@return (Status, camHandleArray_col):
    Status - FGSTATUS
    camHandleArray_col - List of API camera handles of detected cameras. Type: List
@note:
    DEPRECATED - please use KYFG_UpdateCameraList(handle) instead
'''
def KYFG_CameraScan(handle):
    warnings.warn("Function 'KYFG_CameraScan()' is deprecated, please use function 'KYFG_UpdateCameraList()'.", DeprecationWarning)
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)
    detectedCameras_c_int32 = c_int32(0)
    detectedCameras_c_int32_p = pointer(detectedCameras_c_int32)
    temp_arr = (c_uint * KY_MAX_CAMERAS)(0)
    camHandleArray_c_uint32_p = pointer(temp_arr)
    CameraScan_status = kydll.KYFG_CameraScan(handle, camHandleArray_c_uint32_p, detectedCameras_c_int32_p)
    camHandleArray_col = []
    for i in range(detectedCameras_c_int32.value):
        camHandleArray_col.append(temp_arr[i])
    return (return_status(CameraScan_status), camHandleArray_col)


'''
@brief:
    Updates the list of cameras connected to the device. 
    Open camera handles are not affected by this function and retained at the same places of array,
    where they were returned by previous call except for camera(s) that were closed between calls.
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
@return (Status,camHandleArray_col):
    Status - FGSTATUS
    camHandleArray_col - List of API camera handles of detected cameras. Type: List
'''
def KYFG_UpdateCameraList(handle):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)
    detectedCameras_c_int32 = c_int32(KY_MAX_CAMERAS)
    detectedCameras_c_int32_p = pointer(detectedCameras_c_int32)
    temp_arr = (c_uint * KY_MAX_CAMERAS)(0)
    camHandleArray_c_uint32_p = pointer(temp_arr)
    CameraScan_status = kydll.KYFG_UpdateCameraList(handle, camHandleArray_c_uint32_p, detectedCameras_c_int32_p)
    camHandleArray_col = []
    for i in range(detectedCameras_c_int32.value):
        camHandleArray_col.append(temp_arr[i])
    return (return_status(CameraScan_status), camHandleArray_col)

'''
@brief:
    Scans for the cameras connected to the Frame Grabber
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    bRetainOpenCameras - skip currently active links and detect only new connections or reset and full re-scan should be performed.
@return (Status, camScanParameters):
    Status - FGSTATUS
    camScanParameters - Camera scan parameters stucture. Type: KYFGLib_CameraScanParameters
'''
def KYFG_CameraScanEx(handle, bRetainOpenCameras):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)
    KYFGLib_CameraScanParameters_C_STYLE_POINTER = POINTER(KYFGLib_CameraScanParameters_C_STYLE)
    CameraScanParameters = KYFGLib_CameraScanParameters_C_STYLE()
    CameraScanParameters.bRetainOpenCameras = bRetainOpenCameras
    CameraScanParameters_p = pointer(CameraScanParameters)
    kydll.KYFG_CameraScanEx.argtypes = (c_uint, KYFGLib_CameraScanParameters_C_STYLE_POINTER)
    kydll.KYFG_CameraScanEx.restype = c_uint32
    KYFG_CameraScanEx_status = kydll.KYFG_CameraScanEx(handle, CameraScanParameters_p)

    camScanParameters = KYFGLib_CameraScanParameters()
    camScanParameters.version = CameraScanParameters.version
    camScanParameters.nCameraCount = CameraScanParameters.nCameraCount
    camScanParameters.bRetainOpenCameras = CameraScanParameters.bRetainOpenCameras

    for i in range(camScanParameters.nCameraCount):
        camScanParameters.pCamHandleArray.append(CameraScanParameters.pCamHandleArray[i])

    return (return_status(KYFG_CameraScanEx_status), camScanParameters)


'''
@brief:
    Connects to a specific camera. If an xml_file_path is present then the XML is loaded from file and not from camera.
@params:
    camHandle_num - API handle to connected camera. Type: int or CAMHANDLE
    xml_file_path - Path to override XML file. If NULL, the native XML file from the camera will be retrieved. Type: str or 0
@return (FGSTATUS,):
    FGSTATUS - The return status of the function. Can be INPUT_ARGUMENT_TYPE_ERROR
'''
def KYFG_CameraOpen2(camHandle_num, xml_file_path):
    if ( (isinstance(camHandle_num, int) != True) and (isinstance(camHandle_num, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    camHandle_num = int(camHandle_num)
    if ( (xml_file_path is not None) and (isinstance(xml_file_path, str) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_CameraOpen2.argtypes = (c_uint, c_char_p)
    kydll.KYFG_CameraOpen2.restype = c_uint32
    if (xml_file_path is not None):
        xml_file_path_str_buf = create_string_buffer(bytes(xml_file_path.encode()))
    else:
        xml_file_path_str_buf = c_char_p(xml_file_path)
    CameraOpen2_status = kydll.KYFG_CameraOpen2(camHandle_num, xml_file_path_str_buf)
    return (return_status(CameraOpen2_status),)
    

'''
@brief:
    Retrieves information about a connected camera
@params:
    camHandle - API handle to connected camera
@return (FGSTATUS, camInfo):
    FGSTATUS - The return status of the function
    camInfo - chosen camera information. Type: KYFGCAMERA_INFO
@note:
    DEPRECATED - please use KYFG_CameraInfo2(camHandle) instead    
'''
def KYFG_CameraInfo(camHandle):
    warnings.warn("Function 'KYFG_CameraInfo()' is deprecated, please use function 'KYFG_CameraInfo2()'.", DeprecationWarning)
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    camHandle = int(camHandle)
    KYFGCAMERA_INFO_C_STYLE_POINTER = POINTER(KYFGCAMERA_INFO_C_STYLE)
    cam_info = KYFGCAMERA_INFO_C_STYLE()
    cam_info_p = pointer(cam_info)
    kydll.KYFG_CameraInfo.argtypes = (c_uint, KYFGCAMERA_INFO_C_STYLE_POINTER)
    kydll.KYFG_CameraInfo.restype = c_uint32
    KYFG_CameraInfo_status = kydll.KYFG_CameraInfo(camHandle, byref(cam_info))
    camInfo = KYFGCAMERA_INFO()
    camInfo.master_link = cam_info.master_link
    camInfo.link_mask = cam_info.link_mask
    camInfo.link_speed = cam_info.link_speed
    camInfo.stream_id = cam_info.stream_id
    camInfo.deviceVersion = cam_info.deviceVersion.decode()
    camInfo.deviceVendorName = cam_info.deviceVendorName.decode()
    camInfo.deviceManufacturerInfo = cam_info.deviceManufacturerInfo.decode()
    camInfo.deviceModelName = cam_info.deviceModelName.decode()
    camInfo.deviceID = cam_info.deviceID.decode()
    camInfo.deviceUserID = cam_info.deviceUserID.decode()
    camInfo.outputCamera = cam_info.outputCamera
    camInfo.virtualCamera = cam_info.virtualCamera
    return (return_status(KYFG_CameraInfo_status),camInfo)
    
    
'''
@brief:
    Retrieves information about a connected camera
@params:
    camHandle - API handle to connected camera
@return (FGSTATUS, camInfo):
    FGSTATUS - The return status of the function
    camInfo - chosen camera information. Type: KYFGCAMERA_INFO2
'''
def KYFG_CameraInfo2(camHandle):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    camHandle = int(camHandle)
    KYFGCAMERA_INFO2_C_STYLE_POINTER = POINTER(KYFGCAMERA_INFO2_C_STYLE)
    cam_info = KYFGCAMERA_INFO2_C_STYLE()
    cam_info_p = pointer(cam_info)
    kydll.KYFG_CameraInfo2.argtypes = (c_uint, KYFGCAMERA_INFO2_C_STYLE_POINTER)
    kydll.KYFG_CameraInfo2.restype = c_uint32
    KYFG_CameraInfo_status = kydll.KYFG_CameraInfo2(camHandle, byref(cam_info))
    camInfo = KYFGCAMERA_INFO2()
    camInfo.version = cam_info.version
    camInfo.master_link = cam_info.master_link
    camInfo.link_mask = cam_info.link_mask
    camInfo.link_speed = cam_info.link_speed
    camInfo.stream_id = cam_info.stream_id
    camInfo.deviceVersion = cam_info.deviceVersion.decode()
    camInfo.deviceVendorName = cam_info.deviceVendorName.decode()
    camInfo.deviceManufacturerInfo = cam_info.deviceManufacturerInfo.decode()
    camInfo.deviceModelName = cam_info.deviceModelName.decode()
    camInfo.deviceID = cam_info.deviceID.decode()
    camInfo.deviceUserID = cam_info.deviceUserID.decode()
    camInfo.outputCamera = cam_info.outputCamera
    camInfo.virtualCamera = cam_info.virtualCamera
    return (return_status(KYFG_CameraInfo_status),camInfo)    


'''
@brief:
    Retreives the xml from camera to a buffer
@param:
    camHandle - API handle to connected camera
@return (FGSTATUS, isZipped, buffer):
    FGSTATUS - The return status of the function
    isZipFile - indicated if we get xml - 0, zip - 1. Type: bool
    pBuffer - bytearray of xml or zip
@note:
    To get the final file, the pBuffer should be converted to a string, for example this way: --> ''.join(pBuffer)
'''
def KYFG_CameraGetXML(camHandle):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    #c_ubyte_p = POINTER(c_ubyte)
    #c_uint64_p = POINTER(c_uint64)
    #kydll.KYFG_CameraGetXML.argtypes = (c_uint, c_char_p, c_ubyte_p, c_uint64)
    kydll.KYFG_CameraGetXML.restype = c_uint32
    bufferSize_internal = c_uint64(0)
    isZipFile_internal = c_ubyte(0)
    kydll.KYFG_CameraGetXML(camHandle, None, byref(isZipFile_internal), byref(bufferSize_internal))
    #print("Size of internal buffer: " + str(bufferSize_internal.value))
    #print("Internal Is Zipped #1: " + str(isZipFile_internal.value))
    pBuffer_intern_type = (c_char * (bufferSize_internal.value))
    pBuffer_intern = pBuffer_intern_type()
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_CameraGetXML_status = kydll.KYFG_CameraGetXML(camHandle, pBuffer_intern_p, byref(isZipFile_internal), byref(bufferSize_internal))
    #print("Internal Is Zipped #2: " + str(isZipFile_internal.value))
    isZipFile = bool(isZipFile_internal.value)
    pBuffer = []
    pBuffer.clear()
    if (isZipFile == False):
        for i in range(bufferSize_internal.value):
            pBuffer += pBuffer_intern[i].decode()
    else:
        for i in range(bufferSize_internal.value):
            pBuffer += pBuffer_intern[i]
    return (return_status(KYFG_CameraGetXML_status), isZipFile, pBuffer)
    

'''
@brief:
    Closes connection to specific camera
@param:
    camHandle - API handle to connected camera
@return (FGSTATUS,):
    FGSTATUS - The return status of the function
'''
def KYFG_CameraClose(camHandle):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    kydll.KYFG_CameraClose.argtypes = (c_uint,)
    kydll.KYFG_CameraClose.restype = c_uint32
    CameraClose_status = kydll.KYFG_CameraClose(camHandle)
    return (return_status(CameraClose_status),)
    


##################################### Callback functions ###############################################

    
'''
@brief:
    Register run-time callback for the Frame Grabber and all connected cameras
@params:
    handle_grabber - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    CallBackFunc - Pointer to callback function
    x - (optional) Pointer to user context. Afterwards this pointer is retrieved when the callback is issued. Helps to determine the origin of stream in host application.
@return (FGSTATUS,):
    FGSTATUS - The return status of the function
@note:
    DEPRECATED - please use KYFG_CameraCallbackRegister() or KYFG_StreamBufferCallbackRegister() instead 
'''
def KYFG_CallbackRegister(handle_grabber, CallBackFunc, x):
    warnings.warn("Function 'KYFG_CallbackRegister()' is deprecated, please use function 'KYFG_CameraCallbackRegister()' or 'KYFG_StreamBufferCallbackRegister()'.", DeprecationWarning)
    global CallBackFunc_ref
    if ( (isinstance(handle_grabber, int) != True) and (isinstance(handle_grabber, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_CallbackRegister.restype = c_uint32
    CallBackFuncType = CFUNCTYPE(None, c_uint, c_void_p)
    CallBackFunc_ref = CallBackFuncType(CallBackFunc)
    KYFG_CallbackRegister_status = kydll.KYFG_CallbackRegister(handle_grabber, CallBackFunc_ref, x)
    return (return_status(KYFG_CallbackRegister_status),)

'''
@brief:
    Unregister run-time callback for the Frame Grabber and all connected cameras
@params:
    handle_grabber - API handle to chosen Frame Grabber. Type: FGHANDLE
    CallBackFunc - Pointer to callback function
@return (FGSTATUS,):
    FGSTATUS - The return status of the function
@note:
    DEPRECATED - please use KYFG_CameraCallbackUnregister() or KYFG_StreamBufferCallbackUnregister() instead 
    '''
def KYFG_CallbackUnregister(handle_grabber, CallBackFunc):
    warnings.warn("Function 'KYFG_CallbackUnregister()' is deprecated, please use function 'KYFG_CameraCallbackUnregister()' or 'KYFG_StreamBufferCallbackUnregister()'.", DeprecationWarning)
    global CallBackFunc_ref
    if ( (isinstance(handle_grabber, int) != True) and (isinstance(handle_grabber, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_CallbackRegister.restype = c_uint32
    CallBackFuncType = CFUNCTYPE(None, c_uint, c_void_p)
    CallBackFunc_ref = CallBackFuncType(CallBackFunc)
    KYFG_CallbackUnregister_status = kydll.KYFG_CallbackUnregister(handle_grabber, CallBackFunc_ref)
    return (return_status(KYFG_CallbackUnregister_status),)


'''
@brief:
    Callback prototype and registration of runtime callback function for specific camera
@params:
    camHandle - API handle to chosen camera. Type: CAMHANDLE
    userFunc - Pointer to user callback function
    userContext - (optional) Pointer to user context. Afterwards this pointer is retrieved when the callback is issued. Helps to determine the origin of stream in host application.
@return (FGSTATUS,):
    FGSTATUS - The return status of the function
'''
def KYFG_CameraCallbackRegister(camHandle, userFunc, userContext):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    global CameraCallBackFunc_ref
    kydll.KYFG_CameraCallbackRegister.restype = c_uint32
    CameraCallBackFuncType = CFUNCTYPE(None, c_void_p, c_uint)
    CameraCallBackFunc_ref = CameraCallBackFuncType(userFunc)
    KYFG_CameraCallbackRegister_status = kydll.KYFG_CameraCallbackRegister(camHandle, CameraCallBackFunc_ref, userContext)
    return (return_status(KYFG_CameraCallbackRegister_status),)


'''
@brief:
    Unregisters a previously registered general runtime acquisition callback function.
@params:
    camHandle - API handle to chosen camera. Type: CAMHANDLE
    userFunc - Pointer to user callback function
@return (FGSTATUS,):
    FGSTATUS - The return status of the function
    '''
def KYFG_CameraCallbackUnregister(camHandle, userFunc):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    global CameraCallBackFunc_ref
    kydll.KYFG_CameraCallbackUnregister.restype = c_uint32
    CameraCallBackFuncType = CFUNCTYPE(None, c_void_p, c_uint)
    CameraCallBackFunc_ref = CameraCallBackFuncType(userFunc)
    KYFG_CameraCallbackUnregister_status = kydll.KYFG_CameraCallbackUnregister(camHandle, CameraCallBackFunc_ref)
    return (return_status(KYFG_CameraCallbackUnregister_status),)

'''
@brief:
    Register user's run-time callback for video stream
@params:
    streamHandle - API handle to received data. Type: STREAM_HANDLE
    userFunc - Pointer to user callback function
    userContext - (optional) Pointer to user context. Afterwards this pointer is retrieved when the callback is issued. Helps to determine the origin of stream in host application.
@return (FGSTATUS,):
    FGSTATUS - The returned status
'''
def KYFG_StreamBufferCallbackRegister(streamHandle, userFunc, userContext):
    if ( (isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    global StreamBufferCallbackFunc_ref
    streamHandle = int(streamHandle)
    kydll.KYFG_StreamBufferCallbackRegister.restype = c_uint32
    StreamBufferCallbackFuncType = CFUNCTYPE(None, c_uint64, c_void_p)
    StreamBufferCallbackFunc_ref = StreamBufferCallbackFuncType(userFunc)
    KYFG_StreamBufferCallbackRegister_status = kydll.KYFG_StreamBufferCallbackRegister(streamHandle, StreamBufferCallbackFunc_ref, userContext)
    return (return_status(KYFG_StreamBufferCallbackRegister_status),)


'''
@brief:
    Unregister run-time callback for video stream
@params:
    streamHandle - API handle to chosen camera. Type: STREAM_HANDLE
    userFunc - Pointer to user callback function
@return (FGSTATUS,):
    FGSTATUS - The returned status
'''
def KYFG_StreamBufferCallbackUnregister(streamHandle, userFunc):
    if ( (isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    global StreamBufferCallbackFunc_ref
    streamHandle = int(streamHandle)
    kydll.KYFG_StreamBufferCallbackUnregister.restype = c_uint32
    StreamBufferCallbackFuncType = CFUNCTYPE(None, c_uint64, c_void_p)
    StreamBufferCallbackFunc_ref = StreamBufferCallbackFuncType(userFunc)
    KYFG_StreamBufferCallbackUnregister_status = kydll.KYFG_StreamBufferCallbackUnregister(streamHandle, StreamBufferCallbackFunc_ref)
    return (KYFG_StreamBufferCallbackUnregister_status,)

'''
@brief:
    Register run-time callback for receiving auxiliary data
@params:
    handle - API handle to connected device. Type: FGHANDLE
    userFunc - Pointer to user callback function
    userContext - (optional) Pointer to the data to be sent back with callback
@return (FGSTATUS,):
    FGSTATUS - The returned status
'''
def KYFG_AuxDataCallbackRegister(handle, userFunc, userContext):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    global FGAuxDataCallbackFunc_ref
    kydll.KYFG_AuxDataCallbackRegister.restype = c_uint32
    KYFG_AUX_DATA_C_STYLE_POINTER = POINTER(KYFG_AUX_DATA_C_STYLE)
    FGAuxDataCallbackFuncType = CFUNCTYPE(None, KYFG_AUX_DATA_C_STYLE_POINTER, c_void_p)
    FGAuxDataCallbackFunc_ref = FGAuxDataCallbackFuncType(userFunc)
    KYFG_AuxDataCallbackRegister_status = kydll.KYFG_AuxDataCallbackRegister(handle, FGAuxDataCallbackFunc_ref, userContext)
    return (return_status(KYFG_AuxDataCallbackRegister_status),)

    
'''
@brief:
    Unregister run-time auxiliary data callback
@params:
    handle - API handle to connected device. Type: FGHANDLE
    userFunc - pointer to the callback function to unregister, if NULL is passed, all registered callbacks will be unregistered
@return (FGSTATUS,):
    FGSTATUS - The returned status
'''  
def KYFG_AuxDataCallbackUnregister(handle, userFunc):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    global FGAuxDataCallbackFunc_ref
    kydll.KYFG_AuxDataCallbackUnregister.restype = c_uint32
    KYFG_AUX_DATA_C_STYLE_POINTER = POINTER(KYFG_AUX_DATA_C_STYLE)
    FGAuxDataCallbackFuncType = CFUNCTYPE(None, KYFG_AUX_DATA_C_STYLE_POINTER, c_void_p)
    FGAuxDataCallbackFunc_ref = FGAuxDataCallbackFuncType(userFunc)
    KYFG_AuxDataCallbackUnregister_status = kydll.KYFG_AuxDataCallbackUnregister(handle, FGAuxDataCallbackFunc_ref)
    return (return_status(KYFG_AuxDataCallbackUnregister_status),)

    
'''
@brief:
    internal callback - do not use outside the file
'''
def Device_event_callback_func_INTERNAL(userContext, event):
    kydevice_event_pointer = cast(event, POINTER(KYDEVICE_EVENT_C_STYLE))
    event_id = kydevice_event_pointer.contents.eventId
    dbg_print("eventId: " + str(event_id))
    if (event_id == KYDEVICE_EVENT_ID.KYDEVICE_EVENT_CAMERA_START_REQUEST):
        dbg_print("KYDEVICE_EVENT_CAMERA_START_REQUEST event recognized")
        camera_start_request_event_pointer = cast(event, POINTER(KYDEVICE_EVENT_CAMERA_START_C_STYLE))
        camStartRequestObj = KYDEVICE_EVENT_CAMERA_START()
        camStartRequestObj.deviceEvent = KYDEVICE_EVENT()
        camStartRequestObj.deviceEvent.eventId = event_id
        camStartRequestObj.camHandle = CAMHANDLE(camera_start_request_event_pointer.contents.camHandle)
        KYDeviceEventCallBack_ref(userContext, camStartRequestObj)
    elif (event_id == KYDEVICE_EVENT_ID.KYDEVICE_EVENT_CAMERA_CONNECTION_LOST_ID):
        dbg_print("KYDEVICE_EVENT_CAMERA_CONNECTION_LOST_ID event recognized")
        connection_lost_event_pointer = cast(event, POINTER(KYDEVICE_EVENT_CAMERA_CONNECTION_LOST_C_STYLE))
        connectionLostObj = KYDEVICE_EVENT_CAMERA_CONNECTION_LOST()
        connectionLostObj.deviceEvent = KYDEVICE_EVENT()
        connectionLostObj.deviceEvent.eventId = event_id
        connectionLostObj.camHandle = CAMHANDLE(connection_lost_event_pointer.contents.camHandle)
        connectionLostObj.iDeviceLink = connection_lost_event_pointer.contents.iDeviceLink
        connectionLostObj.iCameraLink = connection_lost_event_pointer.contents.iCameraLink
        KYDeviceEventCallBack_ref(userContext, connectionLostObj)
    elif (event_id == KYDEVICE_EVENT_ID.KYDEVICE_EVENT_SYSTEM_TEMPERATURE_ID):
        dbg_print("KYDEVICE_EVENT_SYSTEM_TEMPERATURE_ID event recognized")
        device_temperature_event_pointer = cast(event, POINTER(KYDEVICE_EVENT_SYSTEM_TEMPERATURE_C_STYLE))
        deviceTemperatureObj = KYDEVICE_EVENT_SYSTEM_TEMPERATURE()
        deviceTemperatureObj.deviceEvent = KYDEVICE_EVENT()
        deviceTemperatureObj.deviceEvent.eventId = event_id
        deviceTemperatureObj.temperatureThresholdId = KYDEVICE_EVENT_SYSTEM_TEMPERATURE_THRESHOLDS_ID(device_temperature_event_pointer.contents.temperatureThresholdId)
        KYDeviceEventCallBack_ref(userContext, deviceTemperatureObj)
    elif (event_id == KYDEVICE_EVENT_ID.KYDEVICE_EVENT_CXP2_HEARTBEAT_ID):
        dbg_print("KYDEVICE_EVENT_CXP2_HEARTBEAT_ID event recognized")
        CXP2_Heartbit_event_pointer = cast(event, POINTER(KYDEVICE_EVENT_CXP2_HEARTBEAT_C_STYLE))
        CXP2HeartbitEventObj = KYDEVICE_EVENT_CXP2_HEARTBEAT()
        CXP2HeartbitEventObj.deviceEvent = KYDEVICE_EVENT()
        CXP2HeartbitEventObj.deviceEvent.eventId = event_id
        CXP2HeartbitEventObj.camHandle = CAMHANDLE(CXP2_Heartbit_event_pointer.contents.camHandle)
        CXP2HeartbitEventObj.heartBeat = KY_CXP2_HEARTBEAT()
        CXP2HeartbitEventObj.heartBeat.masterHostConnectionID = CXP2_Heartbit_event_pointer.contents.heartBeat.masterHostConnectionID
        CXP2HeartbitEventObj.heartBeat.cameraTime = CXP2_Heartbit_event_pointer.contents.heartBeat.cameraTime
        KYDeviceEventCallBack_ref(userContext, CXP2HeartbitEventObj)
    elif (event_id == KYDEVICE_EVENT_ID.KYDEVICE_EVENT_CXP2_EVENT_ID):
        dbg_print("KYDEVICE_EVENT_CXP2_EVENT_ID event recognized")
        event_CXP2_event_pointer = cast(event, POINTER(KYDEVICE_EVENT_CXP2_EVENT_C_STYLE))
        EventCXP2EventObj = KYDEVICE_EVENT_CXP2_EVENT()
        EventCXP2EventObj.deviceEvent = KYDEVICE_EVENT()
        EventCXP2EventObj.deviceEvent.eventId = event_id
        EventCXP2EventObj.camHandle = CAMHANDLE(event_CXP2_event_pointer.contents.camHandle)
        EventCXP2EventObj.cxp2Event = KY_CXP2_EVENT()
        EventCXP2EventObj.cxp2Event.masterHostConnectionID = event_CXP2_event_pointer.contents.cxp2Event.masterHostConnectionID
        EventCXP2EventObj.cxp2Event.tag = event_CXP2_event_pointer.contents.cxp2Event.tag
        EventCXP2EventObj.cxp2Event.dataSize = event_CXP2_event_pointer.contents.cxp2Event.dataSize
        for i in range(event_CXP2_event_pointer.contents.cxp2Event.dataWords.size()):
            EventCXP2EventObj.cxp2Event.dataWords[i] = event_CXP2_event_pointer.contents.cxp2Event.dataWords[i].decode()
        KYDeviceEventCallBack_ref(userContext, EventCXP2EventObj)
    elif (event_id == KYDEVICE_EVENT_ID.KYDEVICE_EVENT_GENCP_EVENT_ID):
        dbg_print("KYDEVICE_EVENT_GENCP_EVENT_ID event recognized")
        Gencp_event_pointer = cast(event, POINTER(KYDEVICE_EVENT_GENCP_EVENT_C_STYLE))
        GencpEventObj = KYDEVICE_EVENT_GENCP_EVENT()
        GencpEventObj.deviceEvent = KYDEVICE_EVENT()
        GencpEventObj.deviceEvent.eventId = event_id
        GencpEventObj.srcDevicePort = Gencp_event_pointer.contents.srcDevicePort
        GencpEventObj.gencpEvent = KY_GENCP_EVENT()
        GencpEventObj.gencpEvent.eventSize = Gencp_event_pointer.contents.gencpEvent.eventSize
        GencpEventObj.gencpEvent.eventId = Gencp_event_pointer.contents.heartBeat.eventId
        GencpEventObj.gencpEvent.timestamp = Gencp_event_pointer.contents.gencpEvent.timestamp
        for i in range(Gencp_event_pointer.contents.gencpEvent.data.size()):
            GencpEventObj.gencpEvent.data[i] = Gencp_event_pointer.contents.gencpEvent.data[i].decode()
        KYDeviceEventCallBack_ref(userContext, GencpEventObj)
    elif (event_id == KYDEVICE_EVENT_ID.KYDEVICE_EVENT_GIGE_EVENTDATA_ID):
        dbg_print("KYDEVICE_EVENT_GIGE_EVENTDATA_ID event recognized")
        event_Gige_event_pointer = cast(event, POINTER(KYDEVICE_EVENT_GIGE_EVENTDATA_C_STYLE))
        EventGigeEventObj = KYDEVICE_EVENT_GIGE_EVENTDATA()
        EventGigeEventObj.deviceEvent = KYDEVICE_EVENT()
        EventGigeEventObj.deviceEvent.eventId = event_id
        EventGigeEventObj.srcDevicePort = event_Gige_event_pointer.contents.srcDevicePort
        EventGigeEventObj.gigeEvent = KY_GIGE_EVENTDATA_EVENT()
        EventGigeEventObj.gigeEvent.eventSize = event_Gige_event_pointer.contents.gigeEvent.eventSize
        EventGigeEventObj.gigeEvent.eventId = event_Gige_event_pointer.contents.gigeEvent.eventId
        EventGigeEventObj.gigeEvent.streamChannel = event_Gige_event_pointer.contents.gigeEvent.streamChannel
        EventGigeEventObj.gigeEvent.blockId = event_Gige_event_pointer.contents.gigeEvent.blockId
        EventGigeEventObj.gigeEvent.timestamp = event_Gige_event_pointer.contents.gigeEvent.timestamp
        for i in range(event_Gige_event_pointer.contents.gigeEvent.data.size()):
            EventGigeEventObj.gigeEvent.data[i] = event_Gige_event_pointer.contents.gigeEvent.data[i].decode()
        KYDeviceEventCallBack_ref(userContext, EventGigeEventObj)


'''
@brief:
    Register a generic runtime callback function. The callback (CallBackFunc) will be called to inform user application about various events in the system.
@params:
    handle_grabber - API handle to connected device. Type: int or FGHANDLE
    CallBackFunc - the callback function of the user
    userContext - user context. May be "None"
@return (FGSTATUS,):
    FGSTATUS - The return status of the function
'''
def KYDeviceEventCallBackRegister(handle_grabber, CallBackFunc, userContext):
    global KYDeviceEventCallBack_ref
    global KYDeviceEventCallBack_INTERNAL_ref
    if ( (isinstance(handle_grabber, int) != True) and (isinstance(handle_grabber, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYDeviceEventCallBackRegister.restype = c_uint32
    KYDeviceEventCallBackFuncType = CFUNCTYPE(None, c_void_p, c_void_p)
    KYDeviceEventCallBack_ref = CallBackFunc
    KYDeviceEventCallBack_INTERNAL_ref = KYDeviceEventCallBackFuncType(Device_event_callback_func_INTERNAL)
    KYDeviceEventCallBackRegister_status = kydll.KYDeviceEventCallBackRegister(handle_grabber, KYDeviceEventCallBack_INTERNAL_ref, userContext)
    return (return_status(KYDeviceEventCallBackRegister_status),)

    
'''
@brief:
    Unregisters a previously registered user runtime callback function
@params:
    handle_grabber - API handle to connected device. Type: int or FGHANDLE
    CallBackFunc - the callback function of the user
@return (FGSTATUS,):
    FGSTATUS - The return status of the function
'''
def KYDeviceEventCallBackUnregister(handle_grabber, CallBackFunc):
    global KYDeviceEventCallBack_ref
    global KYDeviceEventCallBack_INTERNAL_ref
    if ( (isinstance(handle_grabber, int) != True) and (isinstance(handle_grabber, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYDeviceEventCallBackUnregister.restype = c_uint32
    KYDeviceEventCallBackFuncType = CFUNCTYPE(None, c_void_p, c_void_p)
    KYDeviceEventCallBack_INTERNAL_ref = KYDeviceEventCallBackFuncType(Device_event_callback_func_INTERNAL)
    KYDeviceEventCallBackUnregister_status = kydll.KYDeviceEventCallBackUnregister(handle_grabber, KYDeviceEventCallBack_INTERNAL_ref)
    return (return_status(KYDeviceEventCallBackUnregister_status),)



##################################### Set Frame Grabber Values ###############################################


'''
@brief:
    Set Frame Grabber configuration field value.
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
    paramValue - Value of configuration parameter.
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''
def KYFG_SetGrabberValue(handle, paramName, paramValue):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)
    kydll.KYFG_GetGrabberValueType.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetGrabberValueType.restype = c_int32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    (paramValueType,) = KYFG_GetGrabberValueType(handle, paramName)
    if    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_INT):
        if (isinstance(paramValue, int) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        return KYFG_SetGrabberValueInt(handle, paramName, paramValue)
    elif (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_ENUM):
        if (isinstance(paramValue, int) != True and isinstance(paramValue, str) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        if (isinstance(paramValue, str) == True):
            return KYFG_SetGrabberValueEnum_ByValueName(handle, paramName, paramValue)
        else:
            return KYFG_SetGrabberValueEnum(handle, paramName, paramValue)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_BOOL):
        if (isinstance(paramValue, bool) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        return KYFG_SetGrabberValueBool(handle, paramName, paramValue)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_FLOAT):
        if (isinstance(paramValue, float) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        return KYFG_SetGrabberValueFloat(handle, paramName, paramValue)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_STRING):
        if (isinstance(paramValue, str) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        return KYFG_SetGrabberValueString(handle, paramName, paramValue)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_COMMAND):
        if (isinstance(paramValue, int) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
        paramValue_p = c_int(paramValue)
        kydll.KYFG_SetGrabberValue.argtypes = (c_uint, c_char_p, c_void_p)
        kydll.KYFG_SetGrabberValue.restype = c_uint32
        KYFG_SetGrabberValue_status = kydll.KYFG_SetGrabberValue(handle, paramName_str_buf, byref(paramValue_p))
        return (return_status(KYFG_SetGrabberValue_status),)
    return (return_status(FGSTATUS_WRONG_PARAMETER_NAME),)


'''
@brief:
    Set Frame Grabber configuration field value of Integer type
@params:
    handle - API handle to chosen camera. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
    value - The requested value. Type: int
@return (FGSTATUS, paramStr)
    FGSTATUS - The returned status.
'''  
def KYFG_SetGrabberValueInt(handle, paramName, value):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(value, int) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_SetGrabberValueInt.argtypes = (c_uint, c_char_p, c_int64)
    kydll.KYFG_SetGrabberValueInt.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    paramValue_p = c_int64(value)
    KYFG_SetGrabberValueInt_status = kydll.KYFG_SetGrabberValueInt(handle, paramName_str_buf, paramValue_p)
    return (return_status(KYFG_SetGrabberValueInt_status),)


'''
@brief:
    Set Frame Grabber configuration field value of Float type
@params:
    handle - API handle to chosen camera. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
    value - The requested value. Type: float
@return (FGSTATUS, paramStr)
    FGSTATUS - The returned status.
'''
def KYFG_SetGrabberValueFloat(handle, paramName, value):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(value, float) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)

    kydll.KYFG_SetGrabberValueFloat.argtypes = (c_uint, c_char_p, c_double)
    kydll.KYFG_SetGrabberValueFloat.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    c_param_double_value = c_double(value)
    KYFG_SetGrabberValueFloat_status = kydll.KYFG_SetGrabberValueFloat(handle, paramName_str_buf, c_param_double_value)
    return (return_status(KYFG_SetGrabberValueFloat_status),)
    
    
'''
@brief:
    Set Frame Grabber configuration field value of Boolean type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
    value - Value of configuration parameter. Type: bool
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''
def KYFG_SetGrabberValueBool(handle, paramName, value):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if ( isinstance(value, bool) != True ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)

    value_num = 0
    if (value == True):
        value_num = 1
    else:
        value_num = 0
    value_c_style = c_ubyte(value_num)

    kydll.KYFG_SetGrabberValueBool.argtypes = (c_uint, c_char_p, c_ubyte)
    kydll.KYFG_SetGrabberValueBool.restype = c_uint32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    KYFG_SetGrabberValueBool_status = kydll.KYFG_SetGrabberValueBool(handle, paramName_str_buf, value_c_style)
    return (return_status(KYFG_SetGrabberValueBool_status),)

    
'''
@brief:
    Set Frame Grabber configuration field value of String type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
    value - Value of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''
def KYFG_SetGrabberValueString(handle, paramName, value):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(value, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)

    kydll.KYFG_SetGrabberValueString.argtypes = (c_uint, c_char_p, c_char_p)
    kydll.KYFG_SetGrabberValueString.restype = c_uint32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    value_str_buf = create_string_buffer(bytes(value.encode()))

    KYFG_SetGrabberValueString_status = kydll.KYFG_SetGrabberValueString(handle, paramName_str_buf, value_str_buf)
    return (return_status(KYFG_SetGrabberValueString_status),)

    
'''
@brief:
    Set Frame Grabber configuration field value of Enumeration type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
    value - Value of configuration parameter. Type: int
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''
def KYFG_SetGrabberValueEnum(handle, paramName, value):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(value, int) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)

    value_c_style = c_int64(value)

    kydll.KYFG_SetGrabberValueEnum.argtypes = (c_uint, c_char_p, c_int64)
    kydll.KYFG_SetGrabberValueEnum.restype = c_uint32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    KYFG_SetGrabberValueEnum_status = kydll.KYFG_SetGrabberValueEnum(handle, paramName_str_buf, value_c_style)
    return (return_status(KYFG_SetGrabberValueEnum_status),)


'''
@brief:
    Set Frame Grabber configuration enumeration field by field name and enumeration name
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
    paramValueName - Value of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    ky_cam_property_type - Parameter camera type. Type: int
'''
def KYFG_SetGrabberValueEnum_ByValueName(handle, paramName, paramValueName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramValueName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)

    kydll.KYFG_SetGrabberValueEnum_ByValueName.argtypes = (c_uint, c_char_p, c_char_p)
    kydll.KYFG_SetGrabberValueEnum_ByValueName.restype = c_uint32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    value_str_buf = create_string_buffer(bytes(paramValueName.encode()))

    KYFG_SetGrabberValueEnum_ByValueName_status = kydll.KYFG_SetGrabberValueEnum_ByValueName(handle, paramName_str_buf, value_str_buf)
    return (return_status(KYFG_SetGrabberValueEnum_ByValueName_status),)
 
 
'''
@brief:
    Execute Frame Grabber command; applicable for values of Command type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, )
    FGSTATUS - The return status of the function
'''
def KYFG_GrabberExecuteCommand(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)

    kydll.KYFG_GrabberExecuteCommand.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GrabberExecuteCommand.restype = c_uint32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    KYFG_GrabberExecuteCommand_status = kydll.KYFG_GrabberExecuteCommand(handle, paramName_str_buf)
    return (return_status(KYFG_GrabberExecuteCommand_status),)


    
##################################### Get Frame Grabber Values ###############################################


'''
@brief:
    Get Frame Grabber configuration field type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - Return status
    grabber_value_type - Frame Grabber Parameter type. Type: KY_CAM_PROPERTY_TYPE  
'''
def KYFG_GetGrabberValueType(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueType.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetGrabberValueType.restype = c_int32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    grabber_value_type = kydll.KYFG_GetGrabberValueType(handle, paramName_str_buf)
    return (grabber_value_type,)
    
    
'''
@brief:
    Get Frame Grabber configuration field value.
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
    paramValue - Configuration value
@note:  In case of PROPERTY_TYPE_ENUM, the tupple includes 3 elements: status, paramValueInt and paramValueStr
        where paramValueInt and paramValueInt represent the required enum entry
'''
def KYFG_GetGrabberValue(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueType.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetGrabberValueType.restype = c_int32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    (paramValueType,) = KYFG_GetGrabberValueType(handle, paramName)

    if    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_INT):
        return KYFG_GetGrabberValueInt(handle, paramName)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_ENUM):
        (status_int, enum_int) = KYFG_GetGrabberValueEnum(handle, paramName)
        (status_str, enum_str) = KYFG_GetGrabberValueStringCopy(handle, paramName)
        if (status_int == FGSTATUS_OK and status_str == FGSTATUS_OK):
            return (return_status(FGSTATUS_OK), enum_int, enum_str)
        if (status_str != FGSTATUS_OK):
            return (return_status(status_str), enum_int, enum_str)
        if (status_int != FGSTATUS_OK):
            return (return_status(status_int), enum_int, enum_str)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_BOOL):
        return KYFG_GetGrabberValueBool(handle, paramName)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_FLOAT):
        return KYFG_GetGrabberValueFloat(handle, paramName)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_STRING):
        return KYFG_GetGrabberValueStringCopy(handle, paramName)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_COMMAND):
        command_executed = c_ubyte(0)
        kydll.KYFG_GetGrabberValue.argtypes = (c_uint, c_char_p, c_void_p)
        kydll.KYFG_GetGrabberValue.restype = c_uint32
        paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
        KYFG_GetGrabberValue_status = kydll.KYFG_GetGrabberValue(handle, paramName_str_buf, byref(command_executed))
        return (return_status(KYFG_GetGrabberValue_status), bool(command_executed.value))
    return (return_status(FGSTATUS_WRONG_PARAMETER_NAME), 0)    


'''
@brief:
    Get Frame Grabber configuration field value of Integer type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (Status, GetGrabberValueInt)
    Status - INPUT_ARGUMENT_TYPE_ERROR / FGSTATUS_OK
    GrabberValueInt - Frame Grabber configuration value of Integer type field. According to Gen<i>Cam standard naming and xml field definition and type. Type: int
'''
def KYFG_GetGrabberValueInt(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR), 0)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR), 0)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueInt.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetGrabberValueInt.restype = c_int64
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    grabber_value_int = c_int64(0)

    KYFG_GetGrabberValueInt_status = kydll.KYFG_GetGrabberValue(handle, paramName_str_buf, byref(grabber_value_int))

    return (return_status(FGSTATUS_OK), grabber_value_int.value)


'''
@brief:
    Get Frame Grabber maximum and minimum configuration field values of Integer type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (Status, GetGrabberValueInt_max, GetGrabberValueInt_min)
    Status - INPUT_ARGUMENT_TYPE_ERROR / FGSTATUS_OK
    GetGrabberValueInt_max - Frame Grabber maximum configuration value of integer type field. Type: int
    GetGrabberValueInt_min - Frame Grabber minimum configuration value of integer type field. Type: int
'''
def KYFG_GetGrabberValueIntMaxMin(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR), 0)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR), 0)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueIntMaxMin.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetGrabberValueIntMaxMin.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    grabber_value_int_max = c_int64(0)
    grabber_value_int_min = c_int64(0)

    KYFG_GetGrabberValueIntMaxMin_status = kydll.KYFG_GetGrabberValueIntMaxMin(handle, paramName_str_buf, byref(grabber_value_int_max),  byref(grabber_value_int_min))

    return (return_status(FGSTATUS_OK), grabber_value_int_max.value, grabber_value_int_min.value)


'''
@brief:
    Get Frame Grabber configuration field value of Float type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, grabber_value_float)
    FGSTATUS - The returned status.
    grabber_value_float - Float value of Frame Grabber configuration parameter
'''
def KYFG_GetGrabberValueFloat(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueFloat.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetGrabberValueFloat.restype = c_double

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    grabber_value_float = c_double(0)

    KYFG_GetGrabberValueFloat_status = kydll.KYFG_GetGrabberValue(handle, paramName_str_buf, byref(grabber_value_float))

    return (return_status(KYFG_GetGrabberValueFloat_status), grabber_value_float.value)


'''
@brief:
    Get Frame Grabber maximum and minimum configuration field values of Float type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (Status, GetGrabberValueFloat_max, GetGrabberValueFloat_min)
    Status - INPUT_ARGUMENT_TYPE_ERROR / FGSTATUS_OK
    GetGrabberValueFloat_max - Frame Grabber maximum configuration value of float type field. Type: double
    GetGrabberValueFloat_min - Frame Grabber minimum configuration value of float type field. Type: double
'''
def KYFG_GetGrabberValueFloatMaxMin(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR), 0)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR), 0)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueFloatMaxMin.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetGrabberValueFloatMaxMin.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    grabber_value_float_max = c_double(0)
    grabber_value_float_min = c_double(0)

    KYFG_GetGrabberValueFloatMaxMin_status = kydll.KYFG_GetGrabberValueFloatMaxMin(handle, paramName_str_buf, byref(grabber_value_float_max),  byref(grabber_value_float_min))

    return (return_status(KYFG_GetGrabberValueFloatMaxMin_status), grabber_value_float_max.value, grabber_value_float_min.value)


'''
@brief:
    Get Frame Grabber configuration field value of Boolean type
@params:
    handle - API handle to chosen camera. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The returned status.
    grabber_value_bool - Frame Grabber configuration value. Type: bool
'''
def KYFG_GetGrabberValueBool(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueBool.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetGrabberValueBool.restype = c_ubyte

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    grabber_value_bool = c_ubyte(0)

    KYFG_GetGrabberValueBool_status = kydll.KYFG_GetGrabberValue(handle, paramName_str_buf, byref(grabber_value_bool))

    return (return_status(KYFG_GetGrabberValueBool_status), bool(grabber_value_bool.value))
    
   
'''
@brief:
    Get Frame Grabber configuration field value of String type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
    paramStr - String value for chosen parameter. Type: str
@note:
    DEPRECATED - please use KYFG_GetGrabberValueStringCopy() instead 
'''
def KYFG_GetGrabberValueString(handle, paramName):
    warnings.warn("Function 'KYFG_GetGrabberValueString()' is deprecated, please use function 'KYFG_GetGrabberValueStringCopy()'.", DeprecationWarning)
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueString.argtypes = (c_uint, c_char_p, POINTER(c_char_p))
    kydll.KYFG_GetGrabberValueString.restype = c_uint32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    paramStr_p = c_char_p(0)
    KYFG_GetGrabberValueString_status = kydll.KYFG_GetGrabberValueString(handle, paramName_str_buf, byref(paramStr_p))

    paramStr = string_at(paramStr_p)
    return return_status(KYFG_GetGrabberValueString_status), paramStr.decode()
    

'''
@brief:
    Get Frame Grabber configuration field value of String type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
    paramStr - String value for chosen parameter. Type: str
'''
def KYFG_GetGrabberValueStringCopy(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueStringCopy.argtypes = (c_uint, c_char_p, c_char_p, POINTER(c_uint))
    kydll.KYFG_GetGrabberValueStringCopy.restype = c_uint32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    # Get the required size of the string
    str_size = c_uint(0)
    KYFG_GetGrabberValueStringCopy_status = kydll.KYFG_GetGrabberValueStringCopy(handle, paramName_str_buf, None, byref(str_size))
    # Create a new string of an appropriate size
    paramValue_c_string = create_string_buffer(str_size.value)
    # Fill the string with the data
    KYFG_GetGrabberValueStringCopy_status = kydll.KYFG_GetGrabberValueStringCopy(handle, paramName_str_buf, paramValue_c_string, byref(str_size))
    paramStr = string_at(paramValue_c_string)
    return return_status(KYFG_GetGrabberValueStringCopy_status), paramStr.decode()
    
    
'''
@brief:
    Get Frame Grabber configuration field value of Enumeration type field
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, grabber_value_enum)
    FGSTATUS - The returned status.
    grabber_value_enum - Enum value of Frame Grabber configuration parameter
'''
def KYFG_GetGrabberValueEnum(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)

    kydll.KYFG_GetGrabberValueEnum.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetGrabberValueEnum.restype = c_int64

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    grabber_value_enum = c_int64(0)

    KYFG_GetGrabberValueEnum_status = kydll.KYFG_GetGrabberValue(handle, paramName_str_buf, byref(grabber_value_enum))

    return (return_status(KYFG_GetGrabberValueEnum_status), grabber_value_enum.value)

    
'''
@brief:
    Get Frame Grabber configuration field value of Register type
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
    buffer_size - The size of requested register. Type: int
    buffer - The data from the register. Type: bytearray
'''
def KYFG_GetGrabberValueRegister(handle, paramName):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)

    kydll.KYFG_GetGrabberValue.argtypes = (c_uint, c_char_p, c_void_p)
    kydll.KYFG_GetGrabberValue.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    # Retrieving buffer size
    buffer_size = c_uint(0)
    kydll.KYFG_GetGrabberValueRegister(handle, paramName_str_buf, None, byref(buffer_size))

    # Create a buffer to be filled with a relevant data
    paramValue_c_buffer = create_string_buffer(buffer_size.value)

    # Get the data
    KYFG_GetGrabberValueRegister_status = kydll.KYFG_GetGrabberValueRegister(handle, paramName_str_buf, byref(paramValue_c_buffer), byref(buffer_size))
    paramStr = string_at(paramValue_c_buffer, buffer_size.value)

    return (return_status(KYFG_GetGrabberValueRegister_status), buffer_size.value, bytes(paramStr))
    
    

##################################### Set Camera Values ###############################################


'''
@brief:
    Set camera configuration field value
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
    paramValue - Value of configuration parameter.
@return (FGSTATUS,)
    FGSTATUS - The return status of the function
'''
def KYFG_SetCameraValue(camHandle, paramName, paramValue):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    camHandle = int(camHandle)

    kydll.KYFG_GetCameraValueType.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetCameraValueType.restype = c_int32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    (paramValueType,) = KYFG_GetCameraValueType(camHandle, paramName)

    if    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_INT):
        if (isinstance(paramValue, int) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        return KYFG_SetCameraValueInt(camHandle, paramName, paramValue)
    elif (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_ENUM):
        if (isinstance(paramValue, int) != True and isinstance(paramValue, str) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        if (isinstance(paramValue, str) == True):
            return KYFG_SetCameraValueEnum_ByValueName(camHandle, paramName, paramValue)
        else:
            return KYFG_SetCameraValueEnum(camHandle, paramName, paramValue)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_BOOL):
        if (isinstance(paramValue, bool) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        return KYFG_SetCameraValueBool(camHandle, paramName, paramValue)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_FLOAT):
        if (isinstance(paramValue, float) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        return KYFG_SetCameraValueFloat(camHandle, paramName, paramValue)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_STRING):
        if (isinstance(paramValue, str) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        return KYFG_SetCameraValueString(camHandle, paramName, paramValue)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_COMMAND):
        if (isinstance(paramValue, int) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
        paramValue_p = c_int(paramValue)
        kydll.KYFG_SetCameraValue.argtypes = (c_uint, c_char_p, c_void_p)
        kydll.KYFG_SetCameraValue.restype = c_uint32
        KYFG_SetCameraValue_status = kydll.KYFG_SetCameraValue(camHandle, paramName_str_buf, byref(paramValue_p))
        return (return_status(KYFG_SetCameraValue_status),)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_REGISTER):
        if (isinstance(paramValue, bytes) != True and isinstance(paramValue, bytearray) != True and isinstance(paramValue, list) != True):
            return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
        return KYFG_SetCameraValueRegister(camHandle, paramName, paramValue)
    return (return_status(FGSTATUS_WRONG_PARAMETER_NAME),)

    
'''
@brief:
    Set camera configuration field value of Integer type
@params:
    camHandle - API handle to chosen Camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
    paramValue - Value of configuration parameter. Type: int
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''  
def KYFG_SetCameraValueInt(camHandle, paramName, paramValue):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramValue, int) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_SetCameraValueInt.argtypes = (c_uint, c_char_p, c_int64)
    kydll.KYFG_SetCameraValueInt.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    paramValue_p = c_int64(paramValue)
    SetCameraValueInt_status = kydll.KYFG_SetCameraValueInt(camHandle, paramName_str_buf, paramValue_p)
    return (return_status(SetCameraValueInt_status),)


'''
@brief:
    Set camera configuration field value of Float type
@params:
    camHandle - API handle to chosen Camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
    value - Floating point value of chosen parameter configuration. Type: double
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''    
def KYFG_SetCameraValueFloat(camHandle, paramName, value):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(value, float) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_SetCameraValueFloat.argtypes = (c_uint, c_char_p, c_double)
    kydll.KYFG_SetCameraValueFloat.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    c_param_double_value = c_double(value)
    KYFG_SetCameraValueFloat_status = kydll.KYFG_SetCameraValueFloat(camHandle, paramName_str_buf, c_param_double_value)
    return (return_status(KYFG_SetCameraValueFloat_status),)
    
    
'''
@brief:
    Set camera configuration field value of Boolean type
@params:
    camHandle - API handle to chosen Camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
    value - Value of configuration parameter. Type: bool
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''
def KYFG_SetCameraValueBool(camHandle, paramName, value):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(value, bool) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    camHandle = int(camHandle)
    value_num = 0
    if (value == True):
        value_num = 1
    else:
        value_num = 0
    value_c_style = c_ubyte(value_num)
    kydll.KYFG_SetCameraValueBool.argtypes = (c_uint, c_char_p, c_ubyte)
    kydll.KYFG_SetCameraValueBool.restype = c_uint
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    KYFG_SetCameraValueBool_status = kydll.KYFG_SetCameraValueBool(camHandle, paramName_str_buf, value_c_style)
    return (return_status(KYFG_SetCameraValueBool_status),)

    
'''
@brief:
    Set camera configuration field value of String type
@params:
    camHandle - API handle to chosen Camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
    value - Value of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''
def KYFG_SetCameraValueString(camHandle, paramName, value):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(value, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)
    kydll.KYFG_SetCameraValueString.argtypes = (c_uint, c_char_p, c_char_p)
    kydll.KYFG_SetCameraValueString.restype = c_uint
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    value_str_buf = create_string_buffer(bytes(value.encode()))
    KYFG_SetCameraValueString_status = kydll.KYFG_SetCameraValueString(camHandle, paramName_str_buf, value_str_buf)
    return (return_status(KYFG_SetCameraValueString_status),)
 
    
'''
@brief:
    Set camera configuration field value of Enumeration type
@params:
    camHandle - API handle to chosen Camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
    value - Enumeration value of chosen parameter configuration. Type: int
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''
def KYFG_SetCameraValueEnum(camHandle, paramName, value):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(value, int) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    camHandle = int(camHandle)
    value_c_style = c_int64(value)
    kydll.KYFG_SetCameraValueEnum.argtypes = (c_uint, c_char_p, c_int64)
    kydll.KYFG_SetCameraValueEnum.restype = c_uint
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    KYFG_SetCameraValueEnum_status = kydll.KYFG_SetCameraValueEnum(camHandle, paramName_str_buf, value_c_style)
    return (return_status(KYFG_SetCameraValueEnum_status),)


'''
@brief:
    Set camera configuration enumeration field by field name and enumeration name
@params:
    camHandle - API handle to chosen Camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
    value - Name of parameter enumeration choice. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
'''
def KYFG_SetCameraValueEnum_ByValueName(camHandle, paramName, paramValueName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramValueName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_SetCameraValueEnum_ByValueName.argtypes = (c_uint, c_char_p, c_char_p)
    kydll.KYFG_SetCameraValueEnum_ByValueName.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    paramValueName_str_buf = create_string_buffer(bytes(paramValueName.encode()))
    SetCameraValueEnum_ByValueName_status = kydll.KYFG_SetCameraValueEnum_ByValueName(camHandle, paramName_str_buf, paramValueName_str_buf)
    return (return_status(SetCameraValueEnum_ByValueName_status),)


'''
@brief:
    Set camera configuration field value of Register type
@params:
    camHandle - API handle to chosen Camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
    value - Data to wirte to the chosen register. Type: bytearray
@return (FGSTATUS,)
    FGSTATUS - The return status of the function
'''
def KYFG_SetCameraValueRegister(camHandle, paramName, value):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(value, bytes) != True and isinstance(value, bytearray) != True and isinstance(value, list) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_SetCameraValue.argtypes = (c_uint, c_char_p, c_void_p)
    kydll.KYFG_SetCameraValue.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    camHandle = int(camHandle)

    # Retrieving buffer size
    buffer_size = c_uint(0)
    kydll.KYFG_GetCameraValueRegister(camHandle, paramName_str_buf, None, byref(buffer_size))

    carray = create_string_buffer(value, buffer_size.value)

    KYFG_SetCameraValueFloat_status = kydll.KYFG_SetCameraValue(camHandle, paramName_str_buf, byref(carray))
    return (return_status(KYFG_SetCameraValueFloat_status),)


'''
@brief:
    Execute camera command; applicable for values of Command type
@params:
    camHandle - API handle to chosen Camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS,)
    FGSTATUS - The return status of the function
'''
def KYFG_CameraExecuteCommand(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)

    kydll.KYFG_CameraExecuteCommand.argtypes = (c_uint, c_char_p)
    kydll.KYFG_CameraExecuteCommand.restype = c_uint

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    KYFG_CameraExecuteCommand_status = kydll.KYFG_CameraExecuteCommand(camHandle, paramName_str_buf)
    return (return_status(KYFG_CameraExecuteCommand_status),)
    
    

##################################### Get Camera Values ###############################################
    

'''
@brief:
    Get camera configuration field type
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    ky_cam_property_type - Camera parameter type. Type: KY_CAM_PROPERTY_TYPE  
'''
def KYFG_GetCameraValueType(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)
    kydll.KYFG_GetCameraValueType.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetCameraValueType.restype = c_int
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    cam_value_type = kydll.KYFG_GetCameraValueType(camHandle, paramName_str_buf)
    return (cam_value_type,)
    
    
'''
@brief:
    Get camera configuration field value
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
    paramValue - Camera configuration value
@note:  In case of PROPERTY_TYPE_ENUM, the tupple includes 3 elements: status, paramValueInt and paramValueStr
        where paramValueInt and paramValueStr represent the required enum entry
'''
def KYFG_GetCameraValue(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    camHandle = int(camHandle)

    kydll.KYFG_GetCameraValueType.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetCameraValueType.restype = c_int32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    (paramValueType,) = KYFG_GetCameraValueType(camHandle, paramName)

    if      (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_INT):
        return KYFG_GetCameraValueInt(camHandle, paramName)
    elif (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_ENUM):
        # return KYFG_GetCameraValueEnum(camHandle, paramName)
        (status_int, enum_int) = KYFG_GetCameraValueEnum(camHandle, paramName)
        (status_str, enum_str) = KYFG_GetCameraValueStringCopy(camHandle, paramName)
        if (status_int == FGSTATUS_OK and status_str == FGSTATUS_OK):
            return (return_status(FGSTATUS_OK), enum_int, enum_str)
        if (status_str != FGSTATUS_OK):
            return (return_status(status_str), enum_int, enum_str)
        if (status_int != FGSTATUS_OK):
            return (return_status(status_int), enum_int, enum_str)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_BOOL):
        return KYFG_GetCameraValueBool(camHandle, paramName)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_FLOAT):
        return KYFG_GetCameraValueFloat(camHandle, paramName)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_STRING):
        return KYFG_GetCameraValueStringCopy(camHandle, paramName)
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_COMMAND):
        command_executed = c_ubyte(0)
        kydll.KYFG_GetCameraValue.argtypes = (c_uint, c_char_p, c_void_p)
        kydll.KYFG_GetCameraValue.restype = c_uint32
        paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
        KYFG_GetCameraValue_status = kydll.KYFG_GetCameraValue(camHandle, paramName_str_buf, byref(command_executed))
        return (return_status(KYFG_GetCameraValue_status), bool(command_executed.value))
    elif    (paramValueType ==  KY_CAM_PROPERTY_TYPE.PROPERTY_TYPE_REGISTER):
        (status, size, buffer) = KYFG_GetCameraValueRegister(camHandle, paramName)
        return (return_status(status), buffer)
    return (return_status(FGSTATUS_WRONG_PARAMETER_NAME),)

    
'''
@brief:
    Get camera configuration field value of Integer type
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, cam_value_int)
    FGSTATUS - The returned status.
    cam_value_int - Integer value of camera configuration parameter
'''
def KYFG_GetCameraValueInt(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)
    kydll.KYFG_GetCameraValueInt.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetCameraValueInt.restype = c_int64
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    cam_value_int = c_int64(0)
    KYFG_GetCameraValueInt_status = kydll.KYFG_GetCameraValue(camHandle, paramName_str_buf, byref(cam_value_int))
    return (return_status(KYFG_GetCameraValueInt_status), cam_value_int.value)


'''
@brief:
    Get camera maximum and minimum configuration field values of Integer type
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, cam_value_int_max, cam_value_int_min)
    FGSTATUS - The returned status.
    cam_value_int_max - Integer value of maximum value of the camera parameter
    cam_value_int_min - Integer value of minimum value of the camera parameter
'''
def KYFG_GetCameraValueIntMaxMin(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)
    kydll.KYFG_GetCameraValueIntMaxMin.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetCameraValueIntMaxMin.restype = c_int64
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    cam_value_int_max = c_int64(0)
    cam_value_int_min = c_int64(0)
    KYFG_GetCameraValueIntMaxMin_status = kydll.KYFG_GetCameraValueIntMaxMin(camHandle, paramName_str_buf, byref(cam_value_int_max),byref(cam_value_int_min))
    return (return_status(KYFG_GetCameraValueIntMaxMin_status), cam_value_int_max.value, cam_value_int_min.value)


'''
@brief:
    Get camera configuration field value of Float type
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, cam_value_float)
    FGSTATUS - The returned status.
    cam_value_float - Float value of camera configuration parameter
'''
def KYFG_GetCameraValueFloat(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)
    kydll.KYFG_GetCameraValueFloat.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetCameraValueFloat.restype = c_double
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    cam_value_float = c_double(0)
    KYFG_GetCameraValueFloat_status = kydll.KYFG_GetCameraValue(camHandle, paramName_str_buf, byref(cam_value_float))
    return (return_status(FGSTATUS_OK), cam_value_float.value)

 
'''
@brief:
    Get camera maximum and minimum configuration field values of Float type
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, cam_value_float_max, cam_value_float_min)
    FGSTATUS - The returned status.
    cam_value_float_max - Float value of maximum value of the camera parameter
    cam_value_float_min - Float value of minimum value of the camera parameter
'''
def KYFG_GetCameraValueFloatMaxMin(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)
    kydll.KYFG_GetCameraValueFloatMaxMin.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetCameraValueFloatMaxMin.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    cam_value_float_max = c_double(0)
    cam_value_float_min = c_double(0)
    KYFG_GetCameraValueFloatMaxMin_status = kydll.KYFG_GetCameraValueFloatMaxMin(camHandle, paramName_str_buf, byref(cam_value_float_max), byref(cam_value_float_min))
    return (return_status(KYFG_GetCameraValueFloatMaxMin_status), cam_value_float_max.value, cam_value_float_min.value)


'''
@brief:
    Get camera configuration field value of Boolean type
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The returned status.
    cam_value_bool - Camera configuration value. Type: bool
'''
def KYFG_GetCameraValueBool(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)

    kydll.KYFG_GetCameraValueBool.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetCameraValueBool.restype = c_ubyte

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    cam_value_bool = c_ubyte(0)
    KYFG_GetCameraValueBool_status = kydll.KYFG_GetCameraValue(camHandle, paramName_str_buf, byref(cam_value_bool))

    return (return_status(KYFG_GetCameraValueBool_status), bool(cam_value_bool.value))

    
'''
@brief:
    Get camera configuration field value of String type
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
    paramStr - String value for chosen parameter. Type: str
@note:
    DEPRECATED - please use KYFG_GetCameraValueStringCopy() instead 
'''
def KYFG_GetCameraValueString(camHandle, paramName):
    warnings.warn("Function 'KYFG_GetCameraValueString()' is deprecated, please use function 'KYFG_GetCameraValueStringCopy()'.", DeprecationWarning)
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    camHandle = int(camHandle)

    kydll.KYFG_GetCameraValueString.argtypes = (c_uint, c_char_p, POINTER(c_char_p))
    kydll.KYFG_GetCameraValueString.restype = c_uint32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    paramStr_p = c_char_p(0)
    KYFG_GetCameraValueString_status = kydll.KYFG_GetCameraValueString(camHandle, paramName_str_buf, byref(paramStr_p))

    paramStr = string_at(paramStr_p)
    return return_status(KYFG_GetCameraValueString_status), paramStr.decode()


'''
@brief:
    Get camera configuration field value of String type
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
    paramStr - String value for chosen parameter. Type: str
'''
def KYFG_GetCameraValueStringCopy(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)

    kydll.KYFG_GetCameraValueStringCopy.argtypes = (c_uint, c_char_p, c_char_p, POINTER(c_uint))
    kydll.KYFG_GetCameraValueStringCopy.restype = c_uint32

    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    # Get the required size of the string
    str_size = c_uint(0)
    KYFG_GetCameraValueStringCopy_status = kydll.KYFG_GetCameraValueStringCopy(camHandle, paramName_str_buf, None, byref(str_size))
    # Create a new string of an appropriate size
    paramValue_c_string = create_string_buffer(str_size.value)
    # Fill the string with the data
    KYFG_GetCameraValueStringCopy_status = kydll.KYFG_GetCameraValueStringCopy(camHandle, paramName_str_buf, paramValue_c_string, byref(str_size))
    paramStr = string_at(paramValue_c_string)
    return return_status(KYFG_GetCameraValueStringCopy_status), paramStr.decode()


'''
@brief:
    Get camera configuration field value of Enumeration type field
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, cam_value_enum)
    FGSTATUS - The returned status.
    cam_value_enum - Enum value of camera configuration parameter
'''
def KYFG_GetCameraValueEnum(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(paramName, str) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)
    kydll.KYFG_GetCameraValueEnum.argtypes = (c_uint, c_char_p)
    kydll.KYFG_GetCameraValueEnum.restype = c_int64
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))
    cam_value_enum = c_int64(0)
    KYFG_GetCameraValueEnum_status = kydll.KYFG_GetCameraValue(camHandle, paramName_str_buf, byref(cam_value_enum))
    return (return_status(KYFG_GetCameraValueEnum_status), cam_value_enum.value)

    
'''
@brief:
    Get camera configuration field value of Register type
@params:
    camHandle - API handle to chosen camera. Type: int or CAMHANDLE
    paramName - Name of configuration parameter. Type: str
@return (FGSTATUS, paramStr)
    FGSTATUS - The return status of the function
    buffer_size - The size of requested register. Type: int
    buffer - The data from the register. Type: bytearray
'''
def KYFG_GetCameraValueRegister(camHandle, paramName):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(paramName, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)

    kydll.KYFG_GetCameraValue.argtypes = (c_uint, c_char_p, c_void_p)
    kydll.KYFG_GetCameraValue.restype = c_uint32
    paramName_str_buf = create_string_buffer(bytes(paramName.encode()))

    # Retrieving buffer size
    buffer_size = c_uint(0)
    kydll.KYFG_GetCameraValueRegister(camHandle, paramName_str_buf, None, byref(buffer_size))

    # Create a buffer to be filled with a relevant data
    paramValue_c_buffer = create_string_buffer(buffer_size.value)

    # Get the data
    KYFG_GetCameraValueRegister_status = kydll.KYFG_GetCameraValueRegister(camHandle, paramName_str_buf, byref(paramValue_c_buffer), byref(buffer_size))
    paramStr = string_at(paramValue_c_buffer, buffer_size.value)

    return (return_status(KYFG_GetCameraValueRegister_status), buffer_size.value, bytes(paramStr))



##################################### Stream Interface ###############################################


'''
@brief:
    Create and allocate a new stream for specified camera
@params:
    camHandle - API handle to connected camera
    frames - Number of frames that should be allocated for this stream. Type: int
    streamIndex - Index of stream. Currently unused and must be 0. Type: int
@return (FGSTATUS, pStreamHandle)
    FGSTATUS - The return status of the function / INPUT_ARGUMENT_TYPE_ERROR
    pStreamHandle - STREAM_HANDLE variable that will hold handle of newly created stream. Type: STREAM_HANDLE
@notes Add error checking, change output parameter pStreamHandle as return
'''
def KYFG_StreamCreateAndAlloc(camHandle, frames, streamIndex):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    pStreamHandle = STREAM_HANDLE()
    camHandle = int(camHandle)
    c_uint32_p = POINTER(c_uint)
    kydll.KYFG_StreamCreateAndAlloc.argtypes = (c_uint, c_uint32_p, c_uint, c_int)
    kydll.KYFG_StreamCreateAndAlloc.restype = c_uint32
    pStreamHandle_uin32 = c_uint(0)
    Stream_c_uint_p = pointer(pStreamHandle_uin32)
    StreamCreateAndAlloc_status = kydll.KYFG_StreamCreateAndAlloc(camHandle, Stream_c_uint_p, frames,streamIndex)
    pStreamHandle.set(pStreamHandle_uin32.value)
    return (return_status(StreamCreateAndAlloc_status),pStreamHandle)

    
'''
@brief:
    Create a new stream for specified camera
@params:
    camHandle - API handle to connected camera. Type: int or CAMHANDLE
    streamIndex - Index of stream. Currently unused and must be 0. Type int
@return (FGSTATUS, pStreamHandle)
    FGSTATUS - The return status of the function
    pStreamHandle - STREAM_HANDLE variable that will hold handle of newly created stream. Type: STREAM_HANDLE
'''
def KYFG_StreamCreate(camHandle, streamIndex: 'currently must be' = 0):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(streamIndex, int) != True ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)

    kydll.KYFG_StreamCreate.argtypes = (c_uint, POINTER(c_uint), c_int)
    kydll.KYFG_StreamCreate.restype = c_uint32

    pStreamHandle_c = c_uint(0)
    KYFG_StreamCreate_status = kydll.KYFG_StreamCreate(camHandle, byref(pStreamHandle_c), streamIndex)

    return return_status(KYFG_StreamCreate_status), STREAM_HANDLE(pStreamHandle_c.value)

'''
@brief:
    Link all announced frame buffers into a stream to form continuous cyclic buffer
@params:
    streamHandle - API handle of a previously created stream. Type: int or STREAM_HANDLE
@return (FGSTATUS)
    FGSTATUS - The return status of the function
'''
def KYFG_StreamLinkFramesContinuously(streamHandle):
    if ( (isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    streamHandle = int(streamHandle)

    KYFG_StreamLinkFramesContinuously_status = kydll.KYFG_StreamLinkFramesContinuously(streamHandle)
    return return_status(KYFG_StreamLinkFramesContinuously_status)


'''
@brief:
    Retrieves information about specified stream
@params:
    streamHandle - Handle of a stream. Type: int or STREAM_HANDLE
    cmdStreamInfo - Type: int (the value could be any of KY_STREAM_INFO_CMD enum values)
@return (FGSTATUS, pInfoBuffer, pInfoType)
    FGSTATUS - The return status of the function
    pInfoBuffer - Byte array memory block with required info
    pInfoSize - size of pInfoBuffer
    pInfoType - data type of pInfoBuffer for requested information.
'''
def KYFG_StreamGetInfo(streamHandle, cmdStreamInfo):
    if ((isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(cmdStreamInfo, int) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    streamHandle = int(streamHandle)

    c_uint64_p = POINTER(c_uint64)
    c_int_p = POINTER(c_int)
    kydll.KYFG_StreamGetInfo.argtypes = (c_uint, c_int, c_void_p, c_uint64_p, c_int_p)
    kydll.KYFG_StreamGetInfo.restype = c_uint32


    pInfoBuffer = c_size_t(0)
    pInfoSize = c_uint64(0)
    pInfoType = c_int(0)


    #KYFG_StreamGetInfo_status = kydll.KYFG_StreamGetInfo(streamHandle, cmdStreamInfo, None, byref(pInfoSize), byref(pInfoType))

    # https://stackoverflow.com/questions/46076118/python-how-interpret-memory-address-and-size-returned-by-dll-as-byte-array
    #pInfoBuffer_byte_array = string_at(pInfoBuffer, pInfoSize.value)

    KYFG_StreamGetInfo_status = kydll.KYFG_StreamGetInfo(streamHandle, cmdStreamInfo, byref(pInfoBuffer), None, None)

    return return_status(KYFG_StreamGetInfo_status), pInfoBuffer.value, pInfoSize.value, pInfoType.value


'''
@brief:
    Retrieves the size of the last acquired frame from specified stream
    This value will be used as internal buffer allocation size
@params:
    streamHandle - API handle to a stream. Type: int or STREAM_HANDLE
@return (FGSTATUS, StreamGetSize)
    StreamGetSize - size of the last acquired frame acquired from specified stream. Type: int
'''
def KYFG_StreamGetSize(streamHandle):
    if ( (isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True)):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    streamHandle = int(streamHandle)
    kydll.KYFG_StreamGetSize.argtypes = (c_uint,)
    kydll.KYFG_StreamGetSize.restype = c_int64
    StreamGetSize = kydll.KYFG_StreamGetSize(streamHandle)
    return (StreamGetSize,)

   
'''
@brief:
    Retrieves the index of the last acquired frame acquired from specified stream
@params:
    streamHandle - API handle to a stream. Type: int or STREAM_HANDLE
@return (Status, StreamGetFrameIndex)
    Status - INPUT_ARGUMENT_TYPE_ERROR / FGSTATUS_OK
    StreamGetFrameIndex - index of the last acquired frame acquired from specified stream. Type: int
@note Add error checking
'''
def KYFG_StreamGetFrameIndex(streamHandle):
    if ( (isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),0)
    streamHandle = int(streamHandle)

    kydll.KYFG_StreamGetFrameIndex.argtypes = (c_uint,)
    kydll.KYFG_StreamGetFrameIndex.restype = c_int

    StreamGetFrameIndex = kydll.KYFG_StreamGetFrameIndex(streamHandle)
    return (return_status(FGSTATUS_OK), StreamGetFrameIndex)

    
'''
@brief:
    Retrieves a pointer to data memory space of 1 frame in the chosen buffer. 
@params:
    streamHandle - API handle to a stream. Type: int or STREAM_HANDLE
    buffIndex - Frame index of data pointer to be retrieved. Type: int
@return (Status, StreamGetPtr)
    Status - INPUT_ARGUMENT_TYPE_ERROR / FGSTATUS_OK
    StreamGetPtr - pointer to data memory space of 1 frame in the chosen buffer.
'''
def KYFG_StreamGetPtr(streamHandle, buffIndex):
    if ((isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True)):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    streamHandle = int(streamHandle)
    kydll.KYFG_StreamGetPtr.argtypes = (c_uint, c_int)
    kydll.KYFG_StreamGetPtr.restype = c_void_p
    StreamGetPtr = kydll.KYFG_StreamGetPtr(streamHandle, buffIndex)
    return (StreamGetPtr,)
    
    
'''
@brief:
    
@params:
    streamHandle - API handle to a stream. Type: int or STREAM_HANDLE
    frame - Frame index of data pointer to be retrieved. Type: int
    pAuxData - KYFG_FRAME_AUX_DATA struct of auxilary data to be filled
@return FGSTATUS
    FGSTATUS - The return status of the function
'''
def KYFG_StreamGetAux(streamHandle, frame, pAuxData):
    if ((isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    streamHandle = int(streamHandle)
    
    kydll.KYFG_StreamGetAux.argtypes = (c_uint, c_int, POINTER(KYFG_FRAME_AUX_DATA_C_STYLE))
    kydll.KYFG_StreamGetAux.restype = c_uint32

    frame_aux_data = KYFG_FRAME_AUX_DATA_C_STYLE()
    frame_aux_data_p = pointer(frame_aux_data)

    KYFG_StreamGetAux_status = kydll.KYFG_StreamGetAux(streamHandle, frame, frame_aux_data_p)

    pAuxData.messageID = frame_aux_data.messageID
    pAuxData.aux_header_reserved = frame_aux_data.aux_header_reserved
    pAuxData.dataSize = frame_aux_data.dataSize
    pAuxData.sequence_number = frame_aux_data.sequence_number
    pAuxData.timestamp = frame_aux_data.timestamp
    pAuxData.aux_frame_reserved = frame_aux_data.aux_frame_reserved

    return (return_status(KYFG_StreamGetAux_status),)

    
'''
@brief:
    Deletes a stream. Any memory allocated by user is NOT freed by this function. 
    All memory allocated by library is freed and all API handles bound to the stream became invalid. 
@params:
    streamHandle - API handle to chosen Frame Grabber. Type: int or STREAM_HANDLE
@return status
    status - The return status of function
'''
def KYFG_StreamDelete(streamHandle):
    if ( (isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    streamHandle = int(streamHandle)
    KYFG_StreamDelete_status = kydll.KYFG_StreamDelete(streamHandle)
    kydll.KYFG_StreamDelete.argtypes = (c_uint,)
    kydll.KYFG_StreamDelete.restype = c_uint32
    return (return_status(KYFG_StreamDelete_status),)
   
    
'''
@brief:
    
@params:
    streamHandle - API handle to connected camera. Type: int or STREAM_HANDLE
    nBufferSize - The size of allocated memory. Currently this parameter MUST be equal to size returned by KYFG_StreamGetInfo()
                  with info command KY_STREAM_INFO_PAYLOAD_SIZE
    pPrivate - This parameter is currently ignored (None)
@return (FGSTATUS, pBufferHandle)
    FGSTATUS - The return status of the function
    pBufferHandle - STREAM_BUFFER_HANDLE variable that will hold handle of newly announced frame buffer. Type: STREAM_BUFFER_HANDLE
'''
def KYFG_BufferAllocAndAnnounce(streamHandle, nBufferSize, pPrivate):
    if ((isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    streamHandle = int(streamHandle)

    kydll.KYFG_BufferAllocAndAnnounce.argtypes = (c_uint, c_size_t, c_void_p, POINTER(c_uint64))
    kydll.KYFG_BufferAllocAndAnnounce.restype = c_uint32

    pBufferHandle = c_uint64(0)
    KYFG_BufferAllocAndAnnounce_status = kydll.KYFG_BufferAllocAndAnnounce(streamHandle, nBufferSize, pPrivate, byref(pBufferHandle))

    return (return_status(KYFG_BufferAllocAndAnnounce_status),STREAM_BUFFER_HANDLE(pBufferHandle.value))

       
# https://stackoverflow.com/questions/36155164/python-ctypes-align-data-structure
def aligned_array(alignment, dtype, n):
    mask = alignment - 1
    size = n * ctypes.sizeof(dtype) + mask
    buf = (ctypes.c_char * size)()
    misalignment = ctypes.addressof(buf) & mask
    if misalignment:
        offset = alignment - misalignment
    else:
        offset = 0
    return (dtype * n).from_buffer(buf, offset)

'''
@brief:
    Announce a buffer allocated by user and bind it to a stream
@params:
    streamHandle - API handle to connected camera. Type: int or STREAM_HANDLE
    pBuffer - Empty list (memory allocated by user) of nBufferSize size. Suitable buffer allocation methods: "bytearray(nBufferSize)", "aligned_array(4096, c_uint8, nBufferSize)" 
              It is advised that nBufferSize parameter will be equal to size returned by KYFG_StreamGetInfo() with info command KY_STREAM_INFO_PAYLOAD_SIZE
    pPrivate - This parameter is currently ignored (should be None)
@return (FGSTATUS, pBufferHandle)
    FGSTATUS - The return status of the function
    pBufferHandle - STREAM_BUFFER_HANDLE variable that will hold handle of newly announced frame buffer. Type: STREAM_BUFFER_HANDLE
'''
def KYFG_BufferAnnounce(streamHandle, pBuffer, pPrivate):
    if ((isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
#     if (isinstance(pBuffer, list) != True):
#         return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    streamHandle = int(streamHandle)

    kydll.KYFG_BufferAnnounce.argtypes = (c_uint, c_void_p, c_size_t, c_void_p, POINTER(c_uint64))
    kydll.KYFG_BufferAnnounce.restype = c_uint32
    pBufferHandle_c = c_uint64(0)
    # https://stackoverflow.com/questions/15377338/convert-ctype-byte-array-to-bytes
    # https://stackoverflow.com/questions/37422662/how-can-i-use-ctypes-to-pass-a-bytearray-into-a-c-function-that-takes-a-char-as
    pBuffer_c = (ctypes.c_uint8 * len(pBuffer)).from_buffer(pBuffer)

    KYFG_BufferAnnounce_status = kydll.KYFG_BufferAnnounce(streamHandle, pBuffer_c, len(pBuffer), pPrivate, byref(pBufferHandle_c))
    return return_status(KYFG_BufferAnnounce_status), STREAM_BUFFER_HANDLE(pBufferHandle_c.value)

    
'''
@brief:
    Retrieves information about previously announced buffer
@params:
    streamBufferHandle - Handle of a stream buffer. Type: int or STREAM_BUFFER_HANDLE
    cmdStreamBufferInfo - Type: int (the value could be any of KY_STREAM_BUFFER_INFO_CMD enum values)
@return (FGSTATUS, pInfoBuffer, pInfoType)
    FGSTATUS - The return status of the function
    pInfoBuffer - Byte array memory block with required info
    pInfoType - data type of pInfoBuffer for requested information.
'''
def KYFG_BufferGetInfo(streamBufferHandle, cmdStreamBufferInfo):
    if ((isinstance(streamBufferHandle, int) != True) and (isinstance(streamBufferHandle, STREAM_BUFFER_HANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(cmdStreamBufferInfo, int) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    streamBufferHandle = int(streamBufferHandle)

    c_uint64_p = POINTER(c_uint64)
    c_int_p = POINTER(c_int)
    kydll.KYFG_BufferGetInfo.argtypes = (c_uint64, c_int, c_void_p, c_uint64_p, c_int_p)
    kydll.KYFG_BufferGetInfo.restype = c_uint32

    pInfoBuffer = 0
    pInfoSize = c_uint64(0)
    pInfoType = c_int(0)

    KYFG_BufferGetInfo_status = kydll.KYFG_BufferGetInfo(streamBufferHandle, cmdStreamBufferInfo, None, byref(pInfoSize), byref(pInfoType))

    if (pInfoType.value == KY_DATA_TYPE.KY_DATATYPE_SIZET):
        pInfoBuffer = c_size_t(0)
        KYFG_BufferGetInfo_status = kydll.KYFG_BufferGetInfo(streamBufferHandle, cmdStreamBufferInfo, byref(pInfoBuffer), None, None)
    elif (pInfoType.value == KY_DATA_TYPE.KY_DATATYPE_UINT64):
        pInfoBuffer = c_uint64(0)
        KYFG_BufferGetInfo_status = kydll.KYFG_BufferGetInfo(streamBufferHandle, cmdStreamBufferInfo, byref(pInfoBuffer), None, None)
    elif (pInfoType.value == KY_DATA_TYPE.KY_DATATYPE_UINT32):
        pInfoBuffer = c_uint32(0)
        KYFG_BufferGetInfo_status = kydll.KYFG_BufferGetInfo(streamBufferHandle, cmdStreamBufferInfo, byref(pInfoBuffer), None, None)
    elif (pInfoType.value == KY_DATA_TYPE.KY_DATATYPE_PTR):
        pInfoBuffer = c_void_p(0)
        KYFG_BufferGetInfo_status = kydll.KYFG_BufferGetInfo(streamBufferHandle, cmdStreamBufferInfo, byref(pInfoBuffer), None, None)
    elif (pInfoType.value == KY_DATA_TYPE.KY_DATATYPE_FLOAT64):
        pInfoBuffer = c_double(0)
        KYFG_BufferGetInfo_status = kydll.KYFG_BufferGetInfo(streamBufferHandle, cmdStreamBufferInfo, byref(pInfoBuffer), None, None)
    else:
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)

    # https://stackoverflow.com/questions/46076118/python-how-interpret-memory-address-and-size-returned-by-dll-as-byte-array
    #pInfoBuffer_byte_array = string_at(pInfoBuffer.value, pInfoSize.value)

    return return_status(KYFG_BufferGetInfo_status), pInfoBuffer.value, pInfoSize.value, pInfoType.value


'''
@brief:
    Moves a previously announced buffer to specified queue
@params:
    streamBufferHandle - Handle of a stream buffer. Type: int or STREAM_BUFFER_HANDLE
    dstQueue - Destination queue. Type: int [the values from KY_ACQ_QUEUE_TYPE]
@return FGSTATUS
    FGSTATUS - The return status of the function
'''
def KYFG_BufferToQueue(streamBufferHandle, dstQueue):
    if ((isinstance(streamBufferHandle, int) != True) and (isinstance(streamBufferHandle, STREAM_BUFFER_HANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    streamBufferHandle = int(streamBufferHandle)

    kydll.KYFG_BufferToQueue.argtypes = (c_uint64, c_int)
    kydll.KYFG_BufferToQueue.restype = c_uint32

    KYFG_BufferToQueue_status = kydll.KYFG_BufferToQueue(streamBufferHandle, dstQueue)
    return (return_status(KYFG_BufferToQueue_status),)

    
'''
@brief:
    Moves all frame buffers bound to specified stream from one queue to another queue
@params:
    streamHandle - Type: int or STREAM_HANDLE
    srcQueue - Type: int [the values from KY_ACQ_QUEUE_TYPE]
    dstQueue - Type: int [the values from KY_ACQ_QUEUE_TYPE]
@return FGSTATUS
    FGSTATUS - The return status of the function
'''
def KYFG_BufferQueueAll(streamHandle, srcQueue, dstQueue):
    if ((isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    streamHandle = int(streamHandle)

    kydll.KYFG_BufferQueueAll.argtypes = (c_uint64, c_int, c_int)
    kydll.KYFG_BufferQueueAll.restype = c_uint32

    KYFG_BufferQueueAll_status = kydll.KYFG_BufferQueueAll(streamHandle, srcQueue, dstQueue)
    return (return_status(KYFG_BufferQueueAll_status),)


'''
@brief:
    Allocation of a stream for a list of buffers consisting of contiguous physical memory, 
    these should be accessed via provided direct physical address.
@params:
    camHandle - API handle to connected camera
    streamHandle - API handle to data stream for selected camera Type: STREAM_HANDLE
    bufferPtrArray - List of buffers 
    frames - Number of frames that should be allocated for this stream. If 0 is passed, number of frames per stream will be retrieved by the function
    frameSize - Size of a single frame (height * width * bitness in Bytes)
    flags  - Type: int Flags parameter value should always be SUBMIT_BUFF_PHYSICAL_ADDRESS
@return FGSTATUS
    FGSTATUS - The return status of the function
'''
def KYFG_BufferSubmit(camHandle, streamHandle, bufferPtrArray, frames, frameSize, flags):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR))
    if ((isinstance(streamHandle, int) != True) and (isinstance(streamHandle, STREAM_HANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(frames, int) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR))
    if (isinstance(frameSize, int) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR))
    if ((isinstance(flags.value, int) != True) and (isinstance(flags.value, SUBMIT_BUFF_FLAGS) != True)):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR))

    camHandle = int(camHandle)
    streamHandle = int(streamHandle)
    p_streamHandle = cast(streamHandle, POINTER(c_uint32))
    flags = int(flags.value)

    for i in range(len(bufferPtrArray)):
        bufferPtrArray[i] = cast(bufferPtrArray[i], POINTER(c_char_p))
    p_bufferPtrArray = cast(bufferPtrArray[0], POINTER(c_void_p))

    kydll.KYFG_BufferQueueAll.argtypes = (c_uint, c_uint32, c_void_p, c_uint, c_uint, c_uint)
    kydll.KYFG_BufferQueueAll.restype = c_uint32
    KYFG_BufferSubmit_status = kydll.KYFG_BufferSubmit(camHandle, p_streamHandle, byref(p_bufferPtrArray), frames, frameSize, flags)
    return (return_status(KYFG_BufferSubmit_status),)



##################################### Data acquisition ###############################################


'''
@brief:
    Starts transmission for the chosen camera. The chosen stream would be filled with data from the camera. 
    Only 1 stream can be active at a time, per camera. 
@params:
    camHandle - API handle to connected camera
    streamHandle - API handle to data stream for selected camera Type: STREAM_HANDLE
    frames - Number of frames to be acquired. After the specified number of frames were acquired, the camera would be stopped. 0 for continues acquisition mode. Type: int
@return (FGSTATUS,)
    FGSTATUS - The return status of the function / INPUT_ARGUMENT_TYPE_ERROR
'''
def KYFG_CameraStart(camHandle, streamHandle, frames):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if ( isinstance(streamHandle, STREAM_HANDLE) != True ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(frames, int) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    camHandle = int(camHandle)
    streamHandle = int(streamHandle)
    kydll.KYFG_CameraStart.argtypes = (c_uint, c_uint, c_uint)
    kydll.KYFG_CameraStart.restype = c_uint32
    CameraStart_status = kydll.KYFG_CameraStart(camHandle,streamHandle,frames)
    return (return_status(CameraStart_status),)


'''
@brief:
    Stops transmission for the chosen camera.
@params:
    camHandle - API handle to connected camera
@return FGSTATUS
    FGSTATUS - The return status of the function
'''
def KYFG_CameraStop(camHandle):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    kydll.KYFG_CameraStop.argtypes = (c_uint,)
    kydll.KYFG_CameraStop.restype = c_uint32
    CameraStop_status = kydll.KYFG_CameraStop(camHandle)
    return (return_status(CameraStop_status),)

    
##################################### Data loading ###############################################


'''
@brief:
    Allocates the needed space in memory and commits it to stream as a video source for stream simulation. 
    Several patterns types are available for generation. 
    Patterns image format is defined by the camera configuration parameters regardless whether it’s colored or non-colored pattern.
@params:
    streamHandle - API handle to data stream for selected camera Type: STREAM_HANDLE
    type - Pattern type to be simulated Type: PATTERN_TYPE
    FixedPatternColor - A pointer to an array of 16bit (Little Endian) aligned color channels.
                        Color should be specified in case a fixed pattern (PATTERN_FIXED) is to be generated.
                        Whether an 8, 10, 12, 14 or 16bit color plane is chosen, the array values should be 16bit values, cropped to the right bit width.
@return (FGSTATUS)
    FGSTATUS - The return status of the function / INPUT_ARGUMENT_TYPE_ERROR
'''
def KYFG_LoadPatternData(streamHandle, type, FixedPatternColor):
    if ( isinstance(streamHandle, STREAM_HANDLE) != True ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(type, int) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(FixedPatternColor, list) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)

    streamHandle = int(streamHandle)
    c_uint64_p = POINTER(c_uint64)
    kydll.KYFG_LoadPatternData.argtypes = (c_uint, c_uint, c_uint64_p)
    kydll.KYFG_LoadPatternData.restype = c_uint32
    loadPatternData_status = kydll.KYFG_LoadPatternData(streamHandle, type, None)
    return (return_status(loadPatternData_status))


'''
@brief:
    Allocates the needed space in memory, and commits it to stream as a video source for simulation. 
    Image types “.bmp”, “.tif”, “.pgn”, and “.raw” are supported. 
    A RAW file may contain several frames; number of frames is calculated according to image format configurations and RAW file size.
@params:
    streamHandle - API handle to data stream for selected camera Type: STREAM_HANDLE
    path - The path of chosen image file
    type - Type of image file: “bmp”, “tip”, “png” or “raw”
    frames - Number of frames to generate
@return FGSTATUS
    FGSTATUS - The return status of the function
'''
def KYFG_LoadFileData(streamHandle, path, type, frames):
    if ( isinstance(streamHandle, STREAM_HANDLE) != True ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if ( isinstance(path, str) != True ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if ( isinstance(type, str) != True ):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(frames, int) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)

    streamHandle = int(streamHandle)
    path_str_buf = create_string_buffer(bytes(path.encode()))
    type_str_buf = create_string_buffer(bytes(type.encode()))
    frames = c_uint(frames)

    kydll.KYFG_LoadFileData.argtypes = (c_uint, c_char_p, c_char_p, c_uint)
    kydll.KYFG_LoadFileData.restype = c_uint32
    loadFileData_status = kydll.KYFG_LoadFileData(streamHandle, path_str_buf, type_str_buf, frames)
    return (return_status(loadFileData_status))



##################################### Low level bootstrap access ###############################################


'''
@brief:
    Read bootstrap registers from specific port, 32bit value each time. 
    This function access the link directly disregarding the camera connection topology.
@params:
    handle  -   API handle to chosen Frame Grabber(int or FGHANDLE)
    port    -   Frame Grabber port index
    address -   Address of the register
@return (status, read_data)
    status  - The return status of function
    read_data    - Integer of 4 bytes, that represents the read register
'''
def KYFG_ReadPortReg(handle, port, address):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    c_uint_p = POINTER(c_uint)
    kydll.KYFG_ReadPortReg.argtypes = (c_uint, c_int, c_uint64, c_uint_p)
    kydll.KYFG_ReadPortReg.restype = c_uint32
    read_data_c = c_uint(0)
    KYFG_ReadPortReg_status = kydll.KYFG_ReadPortReg(handle, port, address, byref(read_data_c))
    return return_status(KYFG_ReadPortReg_status), read_data_c.value

    
'''
@brief:
    Write bootstrap registers from specific port, 32bit value each time. 
    This function access the link directly disregarding the camera connection topology. 
@params:
    handle  -   API handle to chosen Frame Grabber
    port    -   Frame Grabber port index
    address -   Address of the register
    data    -   Integer of 4 bytes, that represents the Bootstrap registers value
@return status
    status - The return status of function
'''
def KYFG_WritePortReg(handle, port, address, data):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    kydll.KYFG_WritePortReg.argtypes = (c_uint, c_int, c_uint64, c_uint)
    kydll.KYFG_WritePortReg.restype = c_uint32
    KYFG_WritePortReg_status = kydll.KYFG_WritePortReg(handle, port, address, data)
    return (return_status(KYFG_WritePortReg_status),)

   
'''
@brief:
    Read buffer of specified size from specific port. 
    This function access the link directly disregarding the camera connection topology. 
@params:
    handle  -   API handle to chosen Frame Grabber
    port    -   Device port index
    address -   Start address of the data to read
    pBuffer -   Empty list that will hold read data
    pSize   -   Size in bytes of buffer to read
@return (status, pSize)
    status - The return status of function
    pSize - size of processed bytes
'''
def KYFG_ReadPortBlock(handle, port, address, pBuffer, pSize):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    pSize_c = c_uint(pSize)
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_ReadPortBlock_status = kydll.KYFG_ReadPortBlock(handle, port, address, pBuffer_intern_p, byref(pSize_c))
    pBuffer.clear()
    for i in range(pSize_c.value):
        pBuffer.append(pBuffer_intern[i])
    return return_status(KYFG_ReadPortBlock_status), pSize_c.value

     
'''
@brief:
    Write buffer of specified size to specific port. 
    This function access the link directly disregarding the camera connection topology. 
@params:
    handle  -   handle to connected device
    port    -   device port through which data will be sent
    address -   destination address on remote device
    pBuffer -   data buffer to write
@return (status, write_bytes)
    status - The return status of function
    write_bytes - Size of processed bytes
'''
def KYFG_WritePortBlock(handle, port, address, pBuffer):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    pSize_c = c_uint(len(pBuffer))
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    for i in range(pSize_c.value):
        pBuffer_intern[i] = pBuffer[i]
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_WritePortBlock_status = kydll.KYFG_WritePortBlock(handle, port, address, pBuffer_intern_p, byref(pSize_c))
    return return_status(KYFG_WritePortBlock_status), pSize_c.value

    
'''
@brief:
    Direct read data buffer from the selected camera
@params:
    camHandle -  API handle to connected camera
    address -   Start address of the data to read
    pBuffer -   Empty list which will be filled with read data
    pSize   -   Size in bytes of buffer to read
@return (status, pSize)
    status - The return status of function
    pSize - size of processed bytes
'''
def KYFG_CameraReadReg(camHandle, address, pBuffer, pSize):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)
    pSize_c = c_uint(pSize)
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_CameraReadReg_status = kydll.KYFG_CameraReadReg(camHandle, address, pBuffer_intern_p, byref(pSize_c))
    pBuffer.clear()
    for i in range(pSize_c.value):
        pBuffer.append(pBuffer_intern[i])
    return return_status(KYFG_CameraReadReg_status), pSize_c.value

    
'''
@brief:
    Direct write data buffer to the selected camera
@params:
    camHandle - API handle to connected camera
    address - Start address of the data to write
    pBuffer - Empty list to write data
@return (status, pSize)
    status - The return status of function
    pSize - Size of processed bytes
@note:
    The values of pBuffer should be bytes
'''
def KYFG_CameraWriteReg(camHandle, address, pBuffer):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    camHandle = int(camHandle)
    pSize_c = c_uint(len(pBuffer))
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    for i in range(pSize_c.value):
        pBuffer_intern[i] = pBuffer[i]
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_CameraWriteReg_status = kydll.KYFG_CameraWriteReg(camHandle, address, pBuffer_intern_p, byref(pSize_c))
    return return_status(KYFG_CameraWriteReg_status), pSize_c.value
    
    
'''
@brief:
    Direct Read from registers of a connected device
@params:
    handle -  API handle to connected Frame Grabber
    address -   Start address of the data to read
    pBuffer -   Empty list which will be filled with read data
    pSize   -   Size in bytes of buffer to read
@return (status, pSize)
    status - The return status of function
    pSize - size of processed bytes
'''
def KYFG_GrabberReadReg(handle, address, pBuffer, pSize):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    pSize_c = c_uint(pSize)
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_GrabberReadReg_status = kydll.KYFG_GrabberReadReg(handle, address, pBuffer_intern_p, byref(pSize_c))
    pBuffer.clear()
    for i in range(pSize_c.value):
        pBuffer.append(pBuffer_intern[i])
    return return_status(KYFG_GrabberReadReg_status), pSize_c.value

    
'''
@brief:
    Direct Write to registers of a connected device
@params:
    handle - API handle to connected Frame Grabber
    address - Start address of the data to write
    pBuffer - Integer of 4 bytes, that represents the Bootstrap registers value
@return (status, pSize)
    status - The return status of function
    pSize - Size of processed bytes
@note:
    The values of pBuffer shoud be bytes
'''
def KYFG_GrabberWriteReg(handle, address, pBuffer):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    pSize_c = c_uint(len(pBuffer))
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    for i in range(pSize_c.value):
        pBuffer_intern[i] = pBuffer[i]
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_GrabberWriteReg_status = kydll.KYFG_GrabberWriteReg(handle, address, pBuffer_intern_p, byref(pSize_c))
    return return_status(KYFG_GrabberWriteReg_status), pSize_c.value
    
    
'''
@brief:
    Direct Read from an address of connected device
@params:
    handle -  API handle to connected Frame Grabber
    address -   Start address of the data to read
    pBuffer -   Empty list which will be filled with readed data
    pSize   -   Size in bytes of buffer to read
@return (status, pSize)
    status - The return status of function
    pSize - size of processed bytes
'''
def KYFG_DeviceDirectHardwareRead(handle, address, pBuffer, pSize):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    pSize_c = c_uint(pSize)
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_GrabberReadHW_status = kydll.KYFG_DeviceDirectHardwareRead(handle, address, pBuffer_intern_p, byref(pSize_c))
    pBuffer.clear()
    for i in range(pSize_c.value):
        pBuffer.append(pBuffer_intern[i])
    return return_status(KYFG_GrabberReadHW_status), pSize_c.value

    
'''
@brief:
    Direct Write to an address of connected device
@params:
    handle - API handle to connected Frame Grabber
    address - Start address of the data to write
    pBuffer - data buffer to write
@return (status, pSize)
    status - The return status of function
    pSize - Size of processed bytes
@note:
    The values of pBuffer shoud be bytes
'''
def KYFG_DeviceDirectHardwareWrite(handle, address, pBuffer):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    pSize_c = c_uint(len(pBuffer))
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    for i in range(pSize_c.value):
        pBuffer_intern[i] = pBuffer[i]
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_GrabberWriteHW_status = kydll.KYFG_DeviceDirectHardwareWrite(handle, address, pBuffer_intern_p, byref(pSize_c))
    return return_status(KYFG_GrabberWriteHW_status), pSize_c.value


'''
@brief:
    Status of specific device physical port regarding connectivity with remote device (i.e camera)
@params:
    handle - API handle to connected Frame Grabber
    port    -   device port number
@return (status, pSize)
    status - The return status of function
    pPortStatus - port status. Type: int (the value could be any of PORT_STATUS enum values)
'''
def KYFG_GetPortStatus(handle, port):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)

    pPortStatus = c_int(0)
    KYFG_PortStatus_status = kydll.KYFG_GetPortStatus(handle, port, byref(pPortStatus))
    pp_portStatus = PORT_STATUS(pPortStatus.value)
    return (return_status(KYFG_PortStatus_status), pp_portStatus)


'''
@brief:
    Direct access to Chameleon camera Simulator 's hardware registers.
@params:
    handle  -   API handle to connected device
    address -   Address of the register
    buffer -   Empty list which will be filled with read data
    size   -   Size in bytes of buffer to read
@return (status, read_data)
    status  - The return status of function
    pSize - size of processed bytes
'''


def KYCS_ReadBootstrapRegs(handle, address, buffer, size):
    if ((isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    pSize_c = c_uint(size)
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    pBuffer_intern_p = pointer(pBuffer_intern)

    KYFG_ReadPortReg_status = kydll.KYCS_ReadBootstrapRegs(handle, address, pBuffer_intern_p, byref(pSize_c))
    buffer.clear()
    for i in range(pSize_c.value):
        buffer.append(pBuffer_intern[i])

    return return_status(KYFG_ReadPortReg_status), pSize_c.value


'''
@brief:
    Write to Chameleon camera Simulator's hardware registers. 
@params:
    handle  -   API handle to connected device
    address -   AStart address of the data to write
    buffer    -   Integer of 4 bytes, that represents the Bootstrap registers value
@return status
    status - The return status of function
    pSize - Size of processed bytes
'''


def KYCS_WriteBootstrapRegs(handle, address, buffer):
    if ((isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    pSize_c = c_uint(len(buffer))
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    for i in range(pSize_c.value):
        pBuffer_intern[i] = buffer[i]
    pBuffer_intern_p = pointer(pBuffer_intern)

    KYFG_WritePortReg_status = kydll.KYCS_WriteBootstrapRegs(handle, address, pBuffer_intern_p, byref(pSize_c))
    return (return_status(KYFG_WritePortReg_status), pSize_c.value)


'''
@brief:
    Send Event Message as specified by GenCP for CLHS, or EVENTDATA message for 10GigE
@details:
    Event message from remote device can be received using "KYDeviceEventCallBackRegister" event id "KYDEVICE_EVENT_GENCP_EVENT_ID" 
    for CLHS, and "KYDEVICE_EVENT_GIGE_EVENTDATA_ID" for 10GigE
@params:
    handle  -   API handle to connected device
    port    -   device port through which data will be sent
    eventId -   id of the event message
    pBuffer -   event data payload
@return (status, pSize)
    status -    The return status of function
    pSize -     Size of processed bytes
@note:
    The values of pBuffer should be bytes
'''
def KYFG_DevicePortSendEventMessage(handle, port, eventId, pBuffer):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    pSize_c = c_uint(len(pBuffer))
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    for i in range(pSize_c.value):
        pBuffer_intern[i] = pBuffer[i]
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_DevicePortSendEventMessage_status = kydll.KYFG_DevicePortSendEventMessage(handle, port, eventId, pBuffer_intern_p, byref(pSize_c))
    return return_status(KYFG_DevicePortSendEventMessage_status), pSize_c.value


'''
@brief:
    Send Event Message as specified by GenCP for CLHS, or EVENTDATA message for 10GigE
@details:
    Event message from remote device can be received using "KYDeviceEventCallBackRegister" event id "KYDEVICE_EVENT_GENCP_EVENT_ID" 
    for CLHS, and "KYDEVICE_EVENT_GIGE_EVENTDATA_ID" for 10GigE
@params:
    camHandle - API handle to connected camera
    eventId   - id of the event message
    pBuffer   - event data payload
@return (status, pSize)
    status    - The return status of function
    pSize     - Size of processed bytes
@note:
    The values of pBuffer should be bytes
'''
def KYFG_CameraSendEventMessage(camHandle, eventId, pBuffer):
    if ( (isinstance(camHandle, int) != True) and (isinstance(camHandle, CAMHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
        camHandle = int(camHandle)
    pSize_c = c_uint(len(pBuffer))
    pBuffer_intern_type = (c_ubyte * pSize_c.value)
    pBuffer_intern = pBuffer_intern_type()
    for i in range(pSize_c.value):
        pBuffer_intern[i] = pBuffer[i]
    pBuffer_intern_p = pointer(pBuffer_intern)
    KYFG_CameraSendEventMessage_status = kydll.KYFG_CameraSendEventMessage(camHandle, port, eventId, pBuffer_intern_p, byref(pSize_c))
    return return_status(KYFG_CameraSendEventMessage_status), pSize_c.value



########################################### IO Control #######################################################


'''
@brief:
    Allows to generate CXP2 HeartBeats and Events using Chameleon camera simulator (starting from firmware version 5.x.x).
@params:
    handle - API handle to the camera simulator device
@return (status, pEvent)
    status - The return status of function
    pEvent - Structure containing a CXP2 device event pack
'''
def KYCS_GenerateCxpEvent(handle):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)

    KY_CXPEVENT_PACK_C_STYLE_POINTER = POINTER(KY_CXPEVENT_PACK_C_STYLE)
    p_event = KY_CXPEVENT_PACK_C_STYLE()
    p_event_p = pointer(p_event)
    kydll.KYCS_GenerateCxpEvent.argtypes = (c_int, KY_CXPEVENT_PACK_C_STYLE_POINTER)
    kydll.KYCS_GenerateCxpEvent.restype = c_uint32

    KYFG_Cxp2Event_status = kydll.KYCS_GenerateCxpEvent(handle, byref(p_event))
    if (KYFG_Cxp2Event_status != CSSTATUS_OK):
        return (return_status(INVALID_INPUT_ARGUMENT),)

    pEvent = KY_CXPEVENT_PACK()
    pEvent.nDataWords = p_event.nDataWords
    for i in range(p_event.nDataWords):
        pEvent.eventDataWord[i] = p_event.eventDataWord[i]

    return (return_status(KYFG_Cxp2Event_status), pEvent)



########################################### CRC injection ####################################################


'''
@brief:
    Allow to set a wrong CRC in one stream packet of one image generation, during a configurable number of image generation cycles.
@params:
    handle - API handle to the camera simulator device
    cycles - Number of image generation cycles. Any value less than 1 is treated as -1 and stops further injections
@return (status)
    status - The return status of function
'''
def KYCS_InjectVideoCRCErrors(handle, cycles):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)

    KYFG_CRCErrors_status = kydll.KYCS_InjectVideoCRCErrors(handle, cycles)
    return (return_status(KYFG_CRCErrors_status))


'''
@brief:
    Allow to set a wrong CRC in the next return Control/Command packets, during a configurable number of cycles.
@params:
    handle - API handle to the camera simulator device
    cycles - Number of image generation cycles. Any value less than 1 is treated as -1 and stops further injections
@return (status)
    status - The return status of function
'''
def KYCS_InjectControlCRCErrors(handle, cycles):
    if ( (isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True) ):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)

    KYFG_CRCErrors_status = kydll.KYCS_InjectVideoCRCErrors(handle, cycles)
    return (return_status(KYFG_CRCErrors_status))

##################################### Authentication interface ###############################################


'''
@brief:
    
@params:
    handle - API handle to a Frame Grabber. Type: int or FGHANDLE
    pKey - KY_AuthKey structure containing information to be programmed into Frame Grabber. Type: KY_AuthKey
    lock -  If this parameter is 0 the grabber can be re-programmed with a different key later.
            If this parameter is 1 then provided key is locked in the Frame Grabber and following call of this function will fail.
            Type: int
@return FGSTATUS
    FGSTATUS - The return status of the function
'''
def KY_AuthProgramKey(handle, pKey, lock):
    if ((isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    if (isinstance(pKey, KY_AuthKey) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    if (isinstance(lock, int) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)

    KY_AuthKey_C_STYLE_POINTER = POINTER(KY_AuthKey_C_STYLE)
    kydll.KY_AuthProgramKey.argtypes = (c_uint, KY_AuthKey_C_STYLE_POINTER, c_int)
    kydll.KY_AuthProgramKey.restype = c_uint32

    pKey_c = KY_AuthKey_C_STYLE()
    for i in range(len(pKey)):
        pKey_c.secret[i] = pKey.secret[i]

    pKey_c_p = pointer(pKey_c)
    KY_AuthProgramKey_status = kydll.KY_AuthProgramKey(handle, pKey_c_p, lock)
    return (return_status(KY_AuthProgramKey_status),)


'''
@brief:
    
@params:
    handle - API handle to a Frame Grabber. Type: int or FGHANDLE
    pKey - KY_AuthKey structure to be verified with Frame Grabber. Type: KY_AuthKey
@return FGSTATUS
    FGSTATUS - The return status of the function
'''
def KY_AuthVerify(handle, pKey):
    if ((isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True)):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)
    handle = int(handle)
    if (isinstance(pKey, KY_AuthKey) != True):
        return return_status(INPUT_ARGUMENT_TYPE_ERROR)

    KY_AuthKey_C_STYLE_POINTER = POINTER(KY_AuthKey_C_STYLE)
    kydll.KY_AuthVerify.argtypes = (c_uint, KY_AuthKey_C_STYLE_POINTER)
    kydll.KY_AuthVerify.restype = c_uint32

    pKey_c = KY_AuthKey_C_STYLE()
    for i in range(len(pKey)):
        pKey_c.secret[i] = pKey.secret[i]

    pKey_c_p = pointer(pKey_c)
    KY_AuthVerify_status = kydll.KY_AuthVerify(handle, pKey_c_p)
    return (return_status(KY_AuthVerify_status),)


    
##################################### License Validation ###############################################

  
'''
@brief:
    
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    license_path - Path to License file. Type: str
@return (FGSTATUS, )
    FGSTATUS - The return status of the function
'''
def KYFG_UploadLicense(handle, license_path):
    if ((isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True)):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(license_path, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)

    kydll.KYFG_UploadLicense.argtypes = (c_uint, c_char_p)
    kydll.KYFG_UploadLicense.restype = c_uint

    license_path_str_buf = create_string_buffer(bytes(license_path.encode()))

    result = kydll.KYFG_UploadLicense(handle, license_path_str_buf)

    return (return_status(result),)


'''
@brief:
    
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
@return (FGSTATUS, )
    FGSTATUS - The return status of the function
'''
def KYFG_ValidateLicense(handle):
    if ((isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True)):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)

    kydll.KYFG_UploadLicense.argtypes = (c_uint, c_char_p)
    kydll.KYFG_UploadLicense.restype = c_uint

    result = kydll.KYFG_ValidateLicense(handle)

    return (return_status(result),)


'''
@brief:
    
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
@return (FGSTATUS, )
    FGSTATUS - The return status of the function
'''
def KYFG_StartTrial(handle):
    if ((isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True)):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)

    kydll.KYFG_UploadLicense.argtypes = (c_uint, c_char_p)
    kydll.KYFG_UploadLicense.restype = c_uint

    result = kydll.KYFG_StartTrial(handle)

    return (return_status(result),)


'''
@brief:
    
@params:
    handle - API handle to chosen Frame Grabber. Type: int or FGHANDLE
    backdoor_path - Path to Backdoor Command file. Type: str
@return (FGSTATUS, )
    FGSTATUS - The return status of the function
'''
def KYFG_BackdoorLicenseCmd(handle, backdoor_path):
    if ((isinstance(handle, int) != True) and (isinstance(handle, FGHANDLE) != True)):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    if (isinstance(backdoor_path, str) != True):
        return (return_status(INPUT_ARGUMENT_TYPE_ERROR),)
    handle = int(handle)
    kydll.KYFG_UploadLicense.argtypes = (c_uint, c_char_p)
    kydll.KYFG_UploadLicense.restype = c_uint
    backdoor_path_str_buf = create_string_buffer(bytes(backdoor_path.encode()))
    result = kydll.KYFG_BackdoorLicenseCmd(handle, backdoor_path_str_buf)
    return (return_status(result),)
