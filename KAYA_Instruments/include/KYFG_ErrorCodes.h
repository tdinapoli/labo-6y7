#ifndef KYFG_ERROR_CODES_H_
#define KYFG_ERROR_CODES_H_

// Error and status reporting
typedef enum _fgstatus
{
    CSSTATUS_OK                                 = 0x2000,
    CSSTATUS_UNKNOWN_SIM_HANDLE                 = 0x2001,
    CSSTATUS_HW_NOT_FOUND                       = 0x2002,
    CSSTATUS_BUSY                               = 0x2003,
    CSSTATUS_FILE_NOT_FOUND                     = 0x2004,
    CSSTATUS_FILE_READ_ERROR                    = 0x2005,
    CSSTATUS_CONFIG_NOT_LOADED                  = 0x2006,
    CSSTATUS_INVALID_VALUE                      = 0x2007,
    CSSTATUS_MAX_CONNECTIONS                    = 0x2008,
    CSSTATUS_COULD_NOT_STOP                     = 0x2009,
    CSSTATUS_CANNOT_LOAD_IMAGE_FILE             = 0x200A,
    CSSTATUS_MEMORY_ERROR                       = 0x200B,
    CSSTATUS_UNKNOWN_SIM_CONTROL                = 0x200C,
    CSSTATUS_WRONG_PARAMETER_NAME               = 0x200D,
    CSSTATUS_WRONG_PARAMETER_TYPE               = 0x200E,
    CSSTATUS_GENICAM_EXCEPTION                  = 0x200F,
    CSSTATUS_OUT_OF_RANGE_ADDRESS               = 0x2010,
    CSSTATUS_PATH_INVALID                       = 0x2011,
    CSSTATUS_FILE_TYPE_INVALID                  = 0x2012,
    CSSTATUS_UNSUPPORTED_IMAGE                  = 0x2013,
    CSSTATUS_UNSUPPORTED_IMAGE_CONVERSION       = 0x2014,
    CSSTATUS_UNSUPPORTED_DEPTH_CONVERSION       = 0x2015,
    CSSTATUS_INVALID_VALUES_FILE                = 0x2016,
    CSSTATUS_FILE_WRITE_ERROR                   = 0x2017,
    CSSTATUS_BUFFER_NOT_LOADED                  = 0x2018,
    CSSTATUS_TRIGGER_NOT_SET                    = 0x2019,
    CSSTATUS_CANNOT_SET_USER_REGISTER_ADDRESS   = 0x201A,
    CSSTATUS_CANNOT_READ_USER_REGISTER          = 0x201B,
    CSSTATUS_CANNOT_WRITE_USER_REGISTER         = 0x201C,
    CSSTATUS_CANNOT_READ_REGISTER               = 0x201D,
    CSSTATUS_CANNOT_WRITE_REGISTER              = 0x201E,
    CSSTATUS_IMAGE_HEADER_INJECTION_SIZE_TOO_BIG = 0x201F,
    CSSTATUS_NO_EXTENDED_HW_FEATURES            = 0x2020,
    CSSTATUS_MAX_USER_ADDRESS_EXCEEDED          = 0x2021,


    FGSTATUS_OK                                 = 0x3000,
    FGSTATUS_UNKNOWN_HANDLE                     = 0x3001,
    FGSTATUS_HW_NOT_FOUND                       = 0x3002,
    FGSTATUS_BUSY                               = 0x3003,
    FGSTATUS_FILE_NOT_FOUND                     = 0x3004,
    FGSTATUS_FILE_READ_ERROR                    = 0x3005,
    FGSTATUS_CONFIG_NOT_LOADED                  = 0x3006,
    FGSTATUS_INVALID_VALUE                      = 0x3007,
    FGSTATUS_MAX_CONNECTIONS                    = 0x3008,
    FGSTATUS_MEMORY_ERROR                       = 0x3009,
    FGSTATUS_WRONG_PARAMETER_NAME               = 0x300A,
    FGSTATUS_WRONG_PARAMETER_TYPE               = 0x300B,
    FGSTATUS_GENICAM_EXCEPTION                  = 0x300C,
    FGSTATUS_OUT_OF_RANGE_ADDRESS               = 0x300D,
    FGSTATUS_COULD_NOT_START                    = 0x300E,
    FGSTATUS_COULD_NOT_STOP                     = 0x300F,
    FGSTATUS_XML_FILE_NOT_LOADED                = 0x3010,
    FGSTATUS_INVALID_VALUES_FILE                = 0x3011,
    FGSTATUS_NO_REQUIRED_PARAMETERS_SECTION     = 0x3012,
    FGSTATUS_WRONG_PARAMETERS_SECTION           = 0x3013,
    FGSTATUS_VALUE_HAS_NO_SELECTOR              = 0x3014,
    FGSTATUS_CALLBACK_NOT_ASSIGNED              = 0x3015,
    FGSTATUS_HANDLE_DOES_NOT_MATCH_CONFIG       = 0x3016,
    FGSTATUS_BUFFER_TOO_SMALL                   = 0x3017,
    FGSTATUS_BUFFER_UNSUPPORTED_SIZE            = 0x3018,
    FGSTATUS_GRABBER_FIRMWARE_NOT_SUPPORTED     = 0x3019,
    FGSTATUS_PARAMETER_NOT_WRITABLE             = 0x301A,
    FGSTATUS_CANNOT_START_HW_STREAM             = 0x301B,
    FGSTATUS_WRONG_SCHEMA_VERSION               = 0x301C,
    FGSTATUS_CAMERA_OR_GRABBER_SECTION_NOT_ARRAY= 0x301D,
    FGSTATUS_ROOT_IS_NOT_OBJECT                 = 0x301E,
    FGSTATUS_NO_PARAMETER_TYPE                  = 0x301F,
    FGSTATUS_FILE_CREATE_ERROR                  = 0x3020,
    FGSTATUS_COULD_NOT_STOP_STREAM              = 0x3021,
    FGSTATUS_BUFFER_MEMORY_OVERLAP              = 0x3022,
    FGSTATUS_UNSUPPORTED_PARAMETER_TYPE         = 0x3023,
    FGSTATUS_OPERATION_TIMEOUT                  = 0x3024,
    FGSTATUS_OPERATION_BLOCKED                  = 0x3025,
    FGSTATUS_PARAMETER_NOT_READABLE             = 0x3026,
    FGSTATUS_PARAMETER_NO_CONTEXT               = 0x3027,

    FGSTATUS_EXCEEDED_MAX_CAMERA_CONNECTIONS    = 0x3100,

    FGSTATUS_QUEUED_BUFFERS_NOT_SUPPORTED       = 0x3101,
    FGSTATUS_DESTINATION_QUEUE_NOT_SUPPORTED    = 0x3102,
    FGSTATUS_INVALID_STREAM_INFO_CMD            = 0x3103,
    FGSTATUS_INVALID_STREAM_BUFFER_INFO_CMD     = 0x3104,
    FGSTATUS_STREAM_NOT_CREATED                 = 0x3105,

    FGSTATUS_GRABBER_NOT_CONNECTED              = 0x3106,
    FGSTATUS_CAMERA_NOT_CONNECTED               = 0x3107,

    FGSTATUS_GRABBER_NOT_OPENED                 = 0x3108,
    FGSTATUS_CAMERA_NOT_OPENED                  = 0x3109,

    FGSTATUS_BUFFER_ALREADY_IN_INPUT_QUEUE      = 0x310A,
    FGSTATUS_STREAM_CANNOT_LOCK                 = 0x310B,  // a Stream is started and cannot be re-started
    FGSTATUS_STREAM_IS_LOCKED                   = 0x310C,  // a Stream is being used and cannot be deleted 

    FGSTATUS_CAMERA_NODES_NOT_INITIALIZED       = 0x3200,

    FGSTATUS_UPDATE_WRONG_VID                   = 0x3300,
    FGSTATUS_UPDATE_WRONG_BOARD_ID              = 0x3301,

    FGSTATUS_CANNOT_WRITE_IMAGE                 = 0x3400,
    FGSTATUS_CANNOT_READ_IMAGE                  = 0x3401,

    FGSTATUS_CONCURRENT_API_CALL                = 0x3500,  // concurrent API call detected

    FGSTATUS_FACILITY_DISABLED                  = 0x3FFD,
    FGSTATUS_FEATURE_NOT_IMPLEMENTED            = 0x3FFE,
    FGSTATUS_UNKNOWN_ERROR                      = 0x3FFF,

}FGSTATUS;

#endif  // #ifndef KYFG_ERROR_CODES_H_
