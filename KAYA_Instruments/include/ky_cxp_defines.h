#ifndef KY_CXP_DEFINES
#define KY_CXP_DEFINES

#ifdef __cplusplus
extern "C" {
#endif

// Camera CoaXPress link available speed values
typedef enum _cxp_link_speed
{
    LINK_SPEED_CXP0 = 0,
    LINK_SPEED_CXP1 = 0x28,
    LINK_SPEED_CXP2 = 0x30,
    LINK_SPEED_CXP3 = 0x38,
    LINK_SPEED_CXP5 = 0x40,
    LINK_SPEED_CXP6 = 0x48,
    LINK_SPEED_CXP10 = 0x50,
    LINK_SPEED_CXP12 = 0x58,
}CXP_LINK_SPEED;

#define LINK_SPEED_MASK 0xFFFF

// Data width of the pixel , defined in section 9.4.1.2 of the JIIA CXP standard document
typedef enum _video_data_width
{
    DATA_WIDTH_UNKNOWN  = 0x00, // ?bit per pixel data
    DATA_WIDTH_8BIT     = 0x01, // 8bit per pixel data
    DATA_WIDTH_10BIT    = 0x02, // 10bit per pixel data
    DATA_WIDTH_12BIT    = 0x03, // 12bit per pixel data
    DATA_WIDTH_14BIT    = 0x04, // 14bit per pixel data
    DATA_WIDTH_16BIT    = 0x05  // 16bit per pixel data
}VIDEO_DATA_WIDTH;

// Data types of the pixel, defined in section 9.4.1 of the JIIA CXP standard document
typedef enum _video_data_type
{
    DATA_TYPE_RAW       = 0x00, // This is used for raw data type.
    DATA_TYPE_MONO      = 0x01, // This is used for luminance data. This has no sub-types. This is defined in Table 27 of JIIA CXP standard document.
    DATA_TYPE_PLANAR    = 0x02, // This is used for planar data, such as individual red, green or blue planes, additional alpha (overlay) planes, or the separate planes in YUV420. This is defined in Table 28 JIIA CXP standard document. Subtipes uncludes all the DATA_SUBTYPE_PLANAR_xx
    DATA_TYPE_BAYER     = 0x03, // This is used for Bayer data. This is defined in Table 29 JIIA CXP standard document. Subtipes include all DATA_SUBTYPE_BAYER_xx
    DATA_TYPE_RGB       = 0x04, // This is used for RGB data, transmitted in the order red, green, blue. This has no sub-types. This is defined in Table 30 JIIA CXP standard document.
    DATA_TYPE_RGBA      = 0x05, // This is used for RGBA data, where “A” is the alpha (or overlay) plane, transmitted in the order red, green, blue, alpha. This has no sub-types. This is defined in Table 31 JIIA CXP standard document.
    DATA_TYPE_YUV       = 0x06, // This is used for YUV data.This is defined in Table 32 JIIA CXP standard document.Subtipes include all DATA_SUBTYPE_YUV_xxx
    DATA_TYPE_YCBCR601  = 0x07, // This is used for YCbCr data, as specified by ITU-R BT.601.This is defined in Table 33 JIIA CXP standard document. Subtipes include all DATA_SUBTYPE_UCBCR_xxx
    DATA_TYPE_YCBCR709  = 0x08, // This is used for YCbCr data, as specified by ITU-R BT.709. This is defined in Table 34 JIIA CXP standard document. Subtipes include all DATA_SUBTYPE_UCBCR_xxx
    DATA_TYPE_INVALID   = 0xFF  // Invalid data type
}VIDEO_DATA_TYPE;

// Data sub-types of the pixel , defined in section 9.4.1 of the JIIA CXP standard document
typedef enum _video_data_subtype
{
    DATA_SUBTYPE_NONE           = 0x00,
    // Planar subtypes
    DATA_SUBTYPE_PLANAR_RY      = 0x01, // Standard usage: R, Y
    DATA_SUBTYPE_PLANAR_GUCB    = 0x02, // Standard usage: G, U, Cb
    DATA_SUBTYPE_PLANAR_BVCR    = 0x03, // Standard usage: B, V, Cr
    // Bayer subtypes
    DATA_SUBTYPE_BAYER_GR       = 0x01, // 1st line transmission order G, R. 2nd line transmission order B, G
    DATA_SUBTYPE_BAYER_RG       = 0x02, // 1st line transmission order R, G. 2nd line transmission order G, B
    DATA_SUBTYPE_BAYER_GB       = 0x03, // 1st line transmission order G, B. 2nd line transmission order R, G
    DATA_SUBTYPE_BAYER_BG       = 0x04, // 1st line transmission order B, G. 2nd line transmission order G, R
    // YUV subtypes
    DATA_SUBTYPE_YUV_411        = 0x01, // Transmission order Y, Y, U, Y, Y, V
    DATA_SUBTYPE_YUV_422        = 0x02, // Transmission order Y, U, Y, V
    DATA_SUBTYPE_YUV_444        = 0x03, // Transmission order Y, U, V
    // YCbCr subtypes
    DATA_SUBTYPE_YCBCR_411      = 0x01, // Transmission order Y, Y, Cb, Y, Y, Cr
    DATA_SUBTYPE_YCBCR_422      = 0x02, // Transmission order Y, Cb, Y, Cr
    DATA_SUBTYPE_YCBCR_444      = 0x03, // Transmission order Y, Cb, Cr
    DATA_SUBTYPE_INVALID        = 0x0F  // Invalid data subtype
}VIDEO_DATA_SUBTYPE;

// Specification of multi-tapped images
typedef enum _tapg
{
    TAPG_1X_1Y      = 0x0000, // 1X-1Y
    TAPG_1X_1Y2     = 0x0004, // 1X-1Y2
    TAPG_1X_2YE     = 0x0041 // 1X-2YE

}TAPG;

// Interlacing modes
typedef enum _scan_mode
{
    SCAN_PROGRESSIVE = 0,
    SCAN_INTERLACING = 1
} SCAN_MODE;


typedef enum _deinterlacing_mode
{
    DEINTERLACING_OFF      = 0,
    DEINTERLACING_LINEDUP  = 1,
    DEINTERLACING_WEAVE    = 2
} DEINTERLACING_MODE;

typedef enum _debayer_mode
{
    DEBAYER_HW_3X3      = 0x0000,
    DEBAYER_HW_3X2      = 0x0002,
    DEBAYER_SOFTWARE    = 0x0100
}DEBAYER_MODE;

typedef enum _packed_data_mode
{
    PACKED_DATA_MODE_UNPACKED       = 0,
    PACKED_DATA_MODE_LINE32ALIGNED  = 1,
    PACKED_DATA_MODE_LINE32ALIGNED_REVERSE  = 3,
}PACKED_DATA_MODE;

typedef enum _transfer_mode
{
    TRANSFER_MODE_AUTOMATIC         = 0,
    TRANSFER_MODE_USER_CONTROLLED   = 1,
}TRANSFER_MODE;

#pragma pack(push, 1)
typedef struct _CXP_HEARTBEAT
{
    uint32_t masterHostConnectionID; //according to CXP 2.0 standard, holds the Host Connection ID of the Host connection 
                                     //connected to the Device Master connection
    uint64_t cameraTime; // The Device time is expressed in nanoseconds.
                         // Note that this field is called "Device time" in the CXP standard
                         // but in this API the notion "device" is used for PCI devices - grabbers and simulators
}KY_CXP2_HEARTBEAT;
#pragma pack(pop)

#pragma pack(push, 1)
#define KY_CXP_EVENT_MAX_DATA_SIZE 1024 //according to CXP 2.0 standard
typedef struct _KY_CXP2_EVENT
{
    uint32_t masterHostConnectionID; //according to CXP 2.0 standard, holds the Host Connection ID of the Host connection 
                                     //connected to the Device Master connection
    uint8_t  tag; // 8 bit tag. Incremented for each new Event packet.
    uint16_t dataSize;   // the number of event data words, Maximum size = CXP_EVENT_MAX_DATA_SIZE bytes according to CXP 2.0 standard
    uint32_t dataWords[KY_CXP_EVENT_MAX_DATA_SIZE / 4];  // 'dataSize' words with one or more event messages
}KY_CXP2_EVENT;
#pragma pack(pop)

#ifdef __cplusplus
} // extern "C" {
#endif

#endif // #ifndef KY_CXP_DEFINES
