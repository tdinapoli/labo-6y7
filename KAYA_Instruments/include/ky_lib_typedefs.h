#ifndef KY_LIB_TYPEDEFS_H_
#define KY_LIB_TYPEDEFS_H_

typedef uint8_t  KYBOOL;

// Parameter camera type
typedef enum _cam_property_type
{
    PROPERTY_TYPE_UNKNOWN   = -1,
    PROPERTY_TYPE_INT       = 0x00,
    PROPERTY_TYPE_BOOL      = 0x01,
    PROPERTY_TYPE_STRING    = 0x02,
    PROPERTY_TYPE_FLOAT     = 0x03,
    PROPERTY_TYPE_ENUM      = 0x04,
    PROPERTY_TYPE_COMMAND   = 0x05,
    PROPERTY_TYPE_REGISTER= 0x06
}KY_CAM_PROPERTY_TYPE;

typedef enum _KY_DATA_TYPE
{
    KY_DATATYPE_UNKNOWN     = 0,    // Unknown data type
    KY_DATATYPE_STRING      = 1,    // NULL-terminated C string (ASCII encoded).
    KY_DATATYPE_STRINGLIST  = 2,    // Concatenated INFO_DATATYPE_STRING list. End of list is signaled with an additional NULL.
    KY_DATATYPE_INT16       = 3,    // Signed 16 bit integer
    KY_DATATYPE_UINT16      = 4,    // Unsigned 16 bit integer
    KY_DATATYPE_INT32       = 5,    // Signed 32 bit integer
    KY_DATATYPE_UINT32      = 6,    // Unsigned 32 bit integer
    KY_DATATYPE_INT64       = 7,    // Signed 64 bit integer
    KY_DATATYPE_UINT64      = 8,    // Unsigned 64 bit integer
    KY_DATATYPE_FLOAT64     = 9,    // Signed 64 bit floating point number.
    KY_DATATYPE_PTR         = 10,   // Pointer type (void*). Size is platform dependent (32 bit on 32 bit platforms).
    KY_DATATYPE_BOOL8       = 11,   // Boolean value occupying 8 bit. 0 for false and anything for true.
    KY_DATATYPE_SIZET       = 12,   // Platform dependent unsigned integer (32 bit on 32 bit platforms).
    KY_DATATYPE_BUFFER      = 13,   // Like a INFO_DATATYPE_STRING but with arbitrary data and no NULL termination.
}KY_DATA_TYPE;

typedef enum _KY_DEVICE_PROTOCOL
{
    KY_DEVICE_PROTOCOL_CoaXPress = 0x0,
    KY_DEVICE_PROTOCOL_CLHS = 0x1,
    KY_DEVICE_PROTOCOL_GigE = 0x2,
    KY_DEVICE_PROTOCOL_Mixed = 0xFF,
    KY_DEVICE_PROTOCOL_Unknown = 0xFFFF
}KY_DEVICE_PROTOCOL;



#ifdef __cplusplus
static const int KY_MAX_DEVICE_INFO_VERSION = 4;
#else
#define KY_MAX_DEVICE_INFO_VERSION 4
#endif

#pragma pack(push, 1)
typedef struct _KY_DEVICE_INFO
{
    // Version of this structure
    // on input must be no greater than KY_MAX_DEVICE_INFO_VERSION, value 0 is treated as 1
    // on output indicates version supported by current library
    uint32_t version;

    // since version 1:
    char     szDeviceDisplayName[256];
    int      nBus;
    int      nSlot;
    int      nFunction;
    uint32_t DevicePID;
    KYBOOL   isVirtual;

    // following fields will be set by library only if caller initializes 'version' with number 2 (or more in library versions)
    // since version 2:
    uint8_t  m_Flags;   // mask KY_DEVICE_STREAM_GRABBER indicates device that supports grabbing (input streams).
                        // mask KY_DEVICE_STREAM_GENERATOR indicates device that supports generation (output streams).

    // since version 3:
    KY_DEVICE_PROTOCOL m_Protocol;

    // since version 4:
    uint32_t DeviceGeneration; // 1 or 2 (I or II)

    // following fields will be set by future library versions and only if caller initializes 'version' with number KY_MAX_DEVICE_INFO_VERSION+1 or more (when supported by library)
}KY_DEVICE_INFO;
#pragma pack(pop)

//
// CXP 2 Device events
//

#pragma pack(push, 1)
typedef struct _KY_CXPEVENT_PACK
{
    uint16_t nDataWords; // Number of data WORDS in 'eventDataWord'
    uint32_t eventDataWord[256]; // according to CXP standard, there can be maximum 1024 bytes of data
}KY_CXPEVENT_PACK;
#pragma pack(pop)



#endif // #ifndef KY_LIB_TYPEDEFS_H_
