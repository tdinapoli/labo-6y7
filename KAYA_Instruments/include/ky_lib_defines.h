#ifndef KY_LIB_DEFINES_H_
#define KY_LIB_DEFINES_H_

#ifndef _WIN32
    #define __STDC_LIMIT_MACROS
#endif
#include <stdint.h>
#include <limits.h>
#include <float.h>
#include <inttypes.h>

//#ifndef UINT32_MAX // TODO: Check the need for this in CentOS - issue 1446
//#   define UINT32_MAX  0x00000000ffffffffULL   /* maximum unsigned int32 value */
//#endif
#ifndef INT64_MAX
#   define INT64_MAX   0x7fffffffffffffffLL    /* maximum signed int64 value */
#endif
#ifndef INT64_MIN
#   define INT64_MIN   0x8000000000000000LL    /* minimum signed int64 value */
#endif

// KY_API definition
#ifdef _MSC_VER
    #ifdef KY_EXPORTS
        #define KY_API __declspec(dllexport)
    #else
        #define KY_API __declspec(dllimport)
    #endif
#else
    #define KY_API
#endif

// KYFG_CALLCONV definition
#ifdef __GNUC__
#define KYFG_CALLCONV
#ifndef KY_INLINE
    #define KY_FORCE_INLINE_GCC __attribute__((always_inline))
    #define KY_FORCE_INLINE_MSVC
    #define KY_INLINE __inline
#endif //KY_INLINE
#elif defined(_MSC_VER)
#ifndef KY_INLINE
    #define KY_FORCE_INLINE_GCC
    #define KY_FORCE_INLINE_MSVC __forceinline
    #define KY_INLINE
#endif //KY_INLINE
// TODO: specify KYFG_CALLCONV for ALL external API
#define KYFG_CALLCONV __cdecl
#else
#define KYFG_CALLCONV
#endif

#ifdef __cplusplus
#define _KY_MEMBER_DEFAULT(exp) =exp
#else
#define _KY_MEMBER_DEFAULT(exp)
#endif

#define _KY_TYPEDEF(t, d) typedef t d;

#define KYTRUE   1
#define KYFALSE  0

// DEPRECATED definition
#ifdef __GNUC__
#define KY_DEPRECATED(name, comment) name __attribute__ ((deprecated(comment)))
#define KY_DEPRECATED2(name, comment) name __attribute__ ((deprecated(comment)))
#elif defined(_MSC_VER)
#define KY_DEPRECATED(name, comment) __declspec(deprecated(comment)) name
#define KY_DEPRECATED2(name, comment) __declspec(deprecated(comment)) name
// TODO: specify KYFG_CALLCONV for ALL external API
#else
#pragma message("WARNING: You need to implement KY_DEPRECATED for this compiler")
#define KY_DEPRECATED(name, text) name
#endif

#ifndef SWIG
#ifndef _WIN32
/**/
    #define GCC_VERSION (__GNUC__ * 10000 \
                     + __GNUC_MINOR__ * 100 \
                     + __GNUC_PATCHLEVEL__)

    #if(GCC_VERSION <= 40407)
        #define nullptr 0
    #endif
    // We do NOT want to #define 'nullptr' as 0 when compiling in Visual Studio 2012, which does support keyword 'nullptr'
    // (as well as other C++ 11 features), but still #defines __cplusplus as 199711L
    #if __cplusplus < 201103L
        #define nullptr 0
    #endif

#endif // #ifndef _WIN32
#endif // #ifndef SWIG

#ifdef __GNUC__
#define VARIABLE_IS_NOT_USED __attribute__ ((unused))
#else
#define VARIABLE_IS_NOT_USED
#endif

#ifdef __cplusplus
static const uint8_t KY_DEVICE_STREAM_GRABBER = 0x1;
static const uint8_t KY_DEVICE_STREAM_GENERATOR = 0x2;
#else
#define KY_DEVICE_STREAM_GRABBER 0x1
#define KY_DEVICE_STREAM_GENERATOR 0x2
#endif

static const char* VARIABLE_IS_NOT_USED DEVICE_NEWINTERRUPTSOURCE_SUPPORTED = "FW_Dma_Capable_NewInterruptSource_Imp";
static const char* VARIABLE_IS_NOT_USED DEVICE_QUEUED_BUFFERS_SUPPORTED = "FW_Dma_Capable_QueuedBuffers_Imp";

#include "ky_lib_typedefs.h"

#endif // #ifndef KY_LIB_DEFINES_H_
