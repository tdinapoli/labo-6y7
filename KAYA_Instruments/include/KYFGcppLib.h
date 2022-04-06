#ifndef KYFG_CPP_LIB_H_
#define KYFG_CPP_LIB_H_

#include "KYFGLib.h"

#include <string>

#ifdef __GNUG__
#include "ky_lib_defines.h" // #if(GCC_VERSION <= 40407) #define nullptr 0
#endif

// C++ only API:
#ifdef __cplusplus

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable: 4190)
#endif // #ifdef _MSC_VER

enum class NodeDescriptorType
{
    Invalid = 0,
    NewNode = 1,
    NewEnumEntry = 2,
    UpdateNode = 3
};

enum class ParameterInterfaceType
{
    intfIValue,
    intfIBase,
    intfIInteger,
    intfIBoolean,
    intfICommand,
    intfIFloat,
    intfIString,
    intfIRegister,
    intfICategory,
    intfIEnumeration,
    intfIEnumEntry,
    intfIPort, 

    intfIUnknown
};

enum class ParameterRepresentation
{
    Linear,
    Logarithmic,
    Boolean,
    PureNumber,
    HexNumber,
    IPV4Address,
    MACAddress,
    _UndefinedRepresentation
};

enum class ParameterVisibility
{
    Unknown		= 0xFF,
	Zero        = 0x00,
    Beginner	= 0x01,
    Expert		= 0x02,
	Guru        = 0x03,
	Developer   = 0x04,
	Invisible	= 0x05
};

// Gen<i>Cam nodes description
struct NodeDescriptor
{
	NodeDescriptor()
		// Initially descriptor should be invalid to avoid noise effects
		// callback issuers are responsible to change descriptor's type appropriately
		:descriptorType(NodeDescriptorType::Invalid)
        ,interfaceType(ParameterInterfaceType::intfIUnknown)

        // nullify all pointers
        , paramName(nullptr)
        , paramDisplayName(nullptr)
        , toolTip(nullptr)
        ,isAvailable(false)
        ,isWritable(false)
        ,isReadable(false)
        ,representation(ParameterRepresentation::_UndefinedRepresentation)
        ,visibility(ParameterVisibility::Unknown)
        ,minIntValue(LLONG_MIN)
        ,maxIntValue(LLONG_MAX)
        ,incIntValue(-1) // no increment unless ptrFloat->HasInc() && ptrInteger->GetInc() doesn't throw
        ,curIntValue(0)
        ,minFloatValue(LDBL_MIN)
        ,maxFloatValue(LDBL_MAX)
        ,incFloatValue(-1) // no increment unless ptrFloat->HasInc() && ptrFloat->GetInc() doesn't throw
        ,floatDisplayPrecision(2)
        ,curFloatValue(0)
        ,curBoolValue(false)
        , curStringValue(nullptr)
        ,isSelector(false)
        , selectorName(nullptr)
        , pParentNode(nullptr)
        , curSelectorValue(-1)
        , description(nullptr)
        , bTracing(false)
    {
    }
    NodeDescriptorType descriptorType;
    ParameterInterfaceType interfaceType;
    const char* paramName;                  // Machine name of parameter. This name should be used as argument ‘paramName’ for KYFG_SetGrabberValueXXX() and KYFG_GetGrabberValueXXX() calls
    const char* paramDisplayName;           // Human readable name of parameter, used in GUI
    const char* toolTip;
    bool isAvailable;                       // `true’ if parameter is currently available, 'false' if any attempt to access this parameter will result in an error (GUI should not show it)
    bool isWritable;                        /* `true’ if parameter is writable, i.e. KYFG_SetGrabberValueXXX() can be called for it;
                                               ‘false’ otherwise – attempt to set it will result in error FGSTATUS_PARAMETER_NOT_WRITABLE*/
    bool isReadable;
    ParameterRepresentation representation; // Indicates type of GUI element suggested for this parameter representation
    ParameterVisibility visibility;         // Visibility level. Used in GUI for filtering set of visible parameters
    int64_t minIntValue;                    // Minimum possible / allowed value in case parameter has ‘intfIInteger’ interfaceType
    int64_t maxIntValue;                    // Maximum possible / allowed value in case parameter has ‘intfIInteger’ interfaceType, length of register in case parameter has ‘intfIRegister’ interfaceType
    int64_t incIntValue;                    // Single increment / decrement step in case parameter has ‘intfIInteger’ interfaceType
    int64_t curIntValue;                    // Current value in case parameter has ‘intfIInteger’ interfaceType
    double minFloatValue;                   // Minimum possible / allowed value in case parameter has ‘intfIFloat’ interfaceType
    double maxFloatValue;                   // Maximum possible / allowed value in case parameter has ‘intfIFloat’ interfaceType
    double incFloatValue;                   // Single increment / decrement step in case parameter has ‘intfIFloat’ interfaceType
    int64_t  floatDisplayPrecision;         // Decimal precision in case parameter has ‘intfIFloat’ interfaceType
    double curFloatValue;                   // Current value in case parameter has ‘intfIFloat’ interfaceType
    bool   curBoolValue;                    // Current value in case parameter has ‘intfIBoolean’ interfaceType
    const char* curStringValue;             // Current value in case parameter has ‘intfIString’ or ‘intfIRegister’ interfaceType
    
    bool isSelector;                        // `true’ if this node acts as selector for other nodes, ‘false’ otherwise
    const char* selectorName;               // name of another node that acts as selector for this node, NULL if this node is not selected

    const NodeDescriptor* pParentNode;      // Pointer to parent node in nodes hierarchy

    int64_t curSelectorValue;
    const char* description;

    // Helper methods
    //std::string ValueAsString() const;

    // Debugging:
    bool bTracing; // parameter is being traced
};

// Grabber and Camera parameters definition as specified in loaded xml
typedef void (KYFG_CALLCONV *ParameterCallback)(void* userContext, const NodeDescriptor* pNodeDescriptor, int grouppingLevel);

// Grabber:
KAYA_API FGSTATUS KYFG_SetGrabberConfigurationParameterCallback(FGHANDLE grabberHandle, ParameterCallback userFunc, void* userContext);
KAYA_API FGSTATUS KYFG_GetGrabberConfigurationParameterDefinitions(FGHANDLE grabberHandle);


// Camera:
KAYA_API FGSTATUS KYFG_SetCameraConfigurationParameterCallback(CAMHANDLE camHandle, ParameterCallback userFunc, void* userContext);
KAYA_API FGSTATUS KYFG_GetCameraConfigurationParameterDefinitions(CAMHANDLE camHandle);

#ifdef _MSC_VER
#pragma warning(pop)
#endif // #ifdef _MSC_VER

#endif // #ifdef __cplusplus
// End of C++ only API


#endif  // #ifndef KYFG_CPP_LIB_H_
