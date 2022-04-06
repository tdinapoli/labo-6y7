#ifndef clserkyi_defines_h_
#define clserkyi_defines_h_

#ifdef _MSC_VER
    #ifdef KYCLSER_EXPORTS
        #define KYCLSER_API __declspec(dllexport)
    #else
        #define KYCLSER_API __declspec(dllimport)
    #endif
#else
    #define KYCLSER_API
#endif

#ifdef __GNUC__
	#define KYCLSER_DEPRECATED(func, text) func __attribute__ ((deprecated))
#elif defined(_MSC_VER)
	#define KYCLSER_DEPRECATED(func, text) __declspec(deprecated(text)) func
#endif

#ifdef __GNUC__
	#define KYCLSER_CALLCONV
#elif defined(_MSC_VER)
	#define KYCLSER_CALLCONV __cdecl
#else
	#define KYCLSER_CALLCONV
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef void*       hSerRef;
typedef uint32_t	CAMHANDLE;

////////////////////////////////////////////////////////
// CL serial DLL versions
/////////////////////////////////////////
#define CL_DLL_VERSION_NO_VERSION               1   // Not a CL dll
#define CL_DLL_VERSION_1_0                      2   // Oct 2000 compliant
#define CL_DLL_VERSION_1_1                      3   // Oct 2001 compliant

////////////////////////////////////////////////////////
// Baud Rates
/////////////////////////////////////////
#define CL_BAUDRATE_9600                        1
#define CL_BAUDRATE_19200                       2
#define CL_BAUDRATE_38400                       4
#define CL_BAUDRATE_57600                       8
#define CL_BAUDRATE_115200                      16
#define CL_BAUDRATE_230400                      32
#define CL_BAUDRATE_460800                      64
#define CL_BAUDRATE_921600                      128

////////////////////////////////////////////////////////
// Error Codes
/////////////////////////////////////////
#define CL_ERR_NO_ERR                               0
#define CL_ERR_BUFFER_TOO_SMALL                     (-10001)
#define CL_ERR_MANU_DOES_NOT_EXIST                  (-10002)
#define CL_ERR_PORT_IN_USE                          (-10003)
#define CL_ERR_TIMEOUT                              (-10004)
#define CL_ERR_INVALID_INDEX                        (-10005)
#define CL_ERR_INVALID_REFERENCE                    (-10006)
#define CL_ERR_ERROR_NOT_FOUND                      (-10007)
#define CL_ERR_BAUD_RATE_NOT_SUPPORTED              (-10008)
#define CL_ERR_OUT_OF_MEMORY                        (-10009)
#define CL_ERR_REGISTRY_KEY_NOT_FOUND               (-10010)
#define CL_ERR_INVALID_PTR                          (-10011)
#define CL_ERR_UNABLE_TO_LOAD_DLL                   (-10098)
#define CL_ERR_FUNCTION_NOT_FOUND                   (-10099)
#define CL_ERR_INVALID_OPERATION					(-11000)

typedef enum _KYSP_EVENT_ID
{
	KYSP_EVENT_ID_RX_DATA_AVAIL = 0x1010,
}KYSP_EVENT_ID;

typedef struct _KYSP_EVENT
{
	KYSP_EVENT_ID eventId;
}KYSP_EVENT;

typedef struct _KYSP_EVENT_RX_DATA_AVAIL
{
	KYSP_EVENT serialPortEvent;
	// Specific KYSP_EVENT_RX_DATA_AVAIL data:
	hSerRef serialRef;
}KYSP_EVENT_RX_DATA_AVAIL;

typedef void(KYCLSER_CALLCONV *clSerialPortCallback)(void* userContext, KYSP_EVENT* pEvent);

#ifdef __cplusplus
} // extern "C" {
#endif

#endif /* clserkyi_defines_h_ */