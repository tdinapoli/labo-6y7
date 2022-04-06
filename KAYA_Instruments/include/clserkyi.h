#ifndef clserkyi_h_
#define clserkyi_h_

#include <stdint.h>
#include <limits.h>

#include "clserkyi_defines.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifdef KY_PRIFIX	// #define KY_PRIFIX to add "KY_" prefix to all functions
	#define FUNCPREFIX(_func_) KY_##_func_
#else
	#define FUNCPREFIX(_func_) _func_
#endif

////////////////////////////////////////////////////////
// Exported functions
/////////////////////////////////////////
/**
 * @fn		clGetNumSerialPortsEx
 * @brief	Returns the number of serial ports provided by connected remote device.
 * @params	[in] CAMHANDLE camHandle - Handle for connected remote device
 *          [out] uint32_t* numSerialPorts - The number of serial ports in this machine supported by selected remote device
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_INVALID_PTR
 *          CL_ERR_INVALID_INDEX
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clGetNumSerialPortsEx(CAMHANDLE camHandle, uint32_t* numSerialPorts) );
/**
 * @fn		clSerialInitEx
 * @brief	Initializes the device referred to by serialIndex and returns a pointer to an internal serial reference structure.
 * @params	[in] CAMHANDLE camHandle - Handle for connected remote device
 *          [in] uint32_t serialIndex - A zero-based index value. For n serial ports of the connected remote device, serialIndex has a range of 0 to (n - 1).
 *          [out] hSerRef* serialRefPtr - On a successful call, points to a value that contains a pointer to the vendor-specific reference to the current session.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_PORT_IN_USE
 *          CL_ERR_INVALID_INDEX
 *          CL_ERR_INVALID_PTR
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clSerialInitEx(CAMHANDLE camHandle, uint32_t serialIndex, hSerRef* serialRefPtr) );

/**
 * @fn		clFlushPort
 * @brief	Discards any bytes that are available in the input buffer.
 * @params	[in] hSerRef serialRef - Handle to serial port
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_INVALID_REFERENCE
 *			CL_ERR_INVALID_OPERATION
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clFlushPort(hSerRef serialRef) );
/**
 * @fn		clGetNumBytesAvail
 * @brief	Outputs the number of bytes that are received at the port specified by serialRef but are not yet read out.
 * @params	[in] hSerRef serialRef - Handle to serial port
 *          [out] uint32_t* numBytes - The number of bytes currently available to be read from the port.
 *
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_INVALID_REFERENCE
 *          CL_ERR_INVALID_PTR
 *			CL_ERR_INVALID_OPERATION
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clGetNumBytesAvail(hSerRef serialRef, uint32_t* numBytes) );
/**
 * @fn		clSerialClose
 * @brief	Closes the serial device and cleans up the resources associated with serialRef. Upon return, serialRef is no longer usable
 * @params	[in] hSerRef serialRef - Handle to serial port
 *
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_INVALID_REFERENCE
 *          CL_ERR_INVALID_OPERATION
 */
KYCLSER_API void KYCLSER_CALLCONV FUNCPREFIX( clSerialClose(hSerRef serialRef) );

/**
 * @fn		clSerialRead
 * @brief	Reads numBytes from the serial device referred to by serialRef. Holds for when numBytes bytes are available at the serial port, 
            or specified timeout period has passed. Upon success, numBytes are copied into buffer. In the case of any error, including CL_ERR_TIMEOUT, 
			no data is copied into buffer.
 * @params	[in] hSerRef serialRef - Handle to serial port
			[out] char* buffer - Points to a user-allocated buffer. Upon a successful call, buffer contains the data read from the serial device. 
			               Upon failure, this buffer is not affected. Caller should ensure that buffer is at least numBytes in size.
			[in] uint32_t* numBytes - The number of bytes requested by the caller.
			[in] uint32_t serialTimeout - Indicates the timeout, in milliseconds, for reading specified buffer size.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_TIMEOUT
 *          CL_ERR_INVALID_REFERENCE
 *			CL_ERR_INVALID_OPERATION
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clSerialRead(hSerRef serialRef, char* buffer, uint32_t* numBytes, uint32_t serialTimeout) );

/**
 * @fn		clSerialWrite
 * @brief	Writes the data in the buffer to the serial device referenced by serialRef.
 * @params	[in] hSerRef serialRef - Handle to serial port
			[in] char* buffer - Contains data to write to the serial port.
			[in,out] uint32_t* bufferSize - Contains the buffer size indicating the maximum number of bytes to be written. Upon a successful call, 
			                              bufferSize contains the number of bytes written to the serial device.
			uint32_t serialTimeout - Indicates the timeout, in milliseconds, for sending specified buffer size.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_TIMEOUT
 *          CL_ERR_INVALID_REFERENCE
 *			CL_ERR_INVALID_OPERATION
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clSerialWrite(hSerRef serialRef, char* buffer, uint32_t* bufferSize, uint32_t serialTimeout) );

/**
 * @fn		clCallbackRegister
 * @brief	Registers a callback function for serial ports events specified in KYSP_EVENT_ID.
 * @params	[in] hSerRef serialRef - Handle to serial port.
 *          [in] clSerialPortCallback callbackFunc - Callback function for serial port events.
 *          [in] void* userContext - User specific context that will be returned upon callback execution.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_INVALID_REFERENCE
 *			CL_ERR_INVALID_OPERATION
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clCallbackRegister(hSerRef serialRef, clSerialPortCallback callbackFunc, void* userContext) );
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clCallbackUnregister(hSerRef serialRef, clSerialPortCallback callbackFunc) );

/**
 * @fn		clSerialComPortInitEx
 * @brief	Creates a Virtual COM Port with specified port number and display name.
 * @params	[in] CAMHANDLE camHandle - Handle for connected remote device
 *          [in] uint32_t serialIndex - A zero-based index value. For n serial ports of the connected remote device, serialIndex has a range of 0 to (n - 1).
 *          [in,out] uint32_t* portNumber - COM port number to open. If portNumber is 0 then next available port number will be assigned.
 *                                          Returns actual port number assigned to COM port.
 *          [in] const char* displayName - COM port display name. In case of NULL a generic name will be assigned.
 *          [out] hSerRef* serialRefPtr - On a successful call, points to a value that contains a pointer to the vendor-specific reference to the current session.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_INVALID_REFERENCE
 *          CL_ERR_INVALID_PTR
 *          CL_ERR_INVALID_INDEX
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clSerialComPortInitEx(CAMHANDLE camHandle, uint32_t serialIndex, uint32_t* portNumber, const char* displayName, hSerRef* serialRefPtr) );


/**
 * @fn		clSerialComPortClose
 * @brief	Close created COM port.
 * @params	[in] hSerRef serialRef - Handle to serial port.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_INVALID_REFERENCE
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clSerialComPortClose(hSerRef serialRef) );

////////////////////////////////////////////////////////
// Exported functions for standard compatibility
/////////////////////////////////////////
/**
 * @fn		clGetNumSerialPorts
 * @brief	Returns the number of serial ports in your system.
 * @params	[out] uint32_t* numSerialPorts - The number of serial ports in this machine supported by this DLL.
 * @return	CL_ERR_NO_ERR
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clGetNumSerialPorts(uint32_t* numSerialPorts) );

/**
 * @fn		clSerialInit
 * @brief	Initializes the device referred to by serialIndex and returns a pointer to an internal serial reference structure.
 * @params	[in] uint32_t serialIndex - A zero-based index value. For n serial devices in the system supported by this library, serialIndex has a range of 0 to (n - 1).
 *          [out] hSerRef* serialRefPtr - On a successful call, points to a value that contains a pointer to the vendor-specific reference to the current session.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_PORT_IN_USE
 *          CL_ERR_INVALID_INDEX
 *          CL_ERR_INVALID_PTR
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clSerialInit(uint32_t serialIndex, hSerRef* serialRefPtr) );

/**
 * @fn		clGetErrorText
 * @brief	Converts an error code to error text for display in a dialog box or in a standard I/O window.
 * @params	[in] int32_t errorCode - The error code used to find the appropriate error text. An error code is returned by every function in this library.
 *          [out] char* errorText - User allocated buffer which contains the NULL-terminated error text on function return.
 *          [in,out] uint32_t* errorTextSize - On success, contains the number of bytes written into the buffer, including the NULL-termination character. 
 *                                             This value should be the size in bytes of the error text buffer passed in. On CL_ERR_BUFFER_TOO_SMALL, 
 *                                             contains the size of the buffer needed to write the error text.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_BUFFER_TOO_SMALL
 *          CL_ERR_ERROR_NOT_FOUND
 *          CL_ERR_INVALID_PTR
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clGetErrorText(int32_t errorCode, char* errorText, uint32_t* errorTextSize) );

/**
 * @fn		clGetManufacturerInfo
 * @brief	Returns the name of the frame grabber manufacturer who created the DLL and the version of the Camera Link specifications with which the DLL complies.
 * @params	[out] char* manufacturerName - A pointer to a user-allocated buffer into which the function copies the manufacturer name. The returned name is NULL-terminated.
 *          [in,out] uint32_t* bufferSize - As an input, this value should be the size of the buffer that is passed. On successful return, this parameter contains the 
 *                                          number of bytes written into the buffer, including the NULL termination character. On CL_ERR_BUFFER_TOO_SMALL, this parameter 
                                            contains the size of the buffer needed to write the data text.
 *          [out] uint32_t* version - A constant stating the version of the Camera Link specifications with which this DLL complies.
 *
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_FUNCTION_NOT_FOUND
 *          CL_ERR_BUFFER_TOO_SMALL
 *          CL_ERR_INVALID_PTR
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clGetManufacturerInfo(char* manufacturerName, uint32_t* bufferSize, uint32_t* version) );

////////////////////////////////////////////////////////
// Exported functions currently not implemented
/////////////////////////////////////////
/**
 * @fn		clGetSupportedBaudRates
 * @brief	Returns the valid baud rates of the current interface.
 * @params	[in] hSerRef serialRef - Handle to serial port
			[in] uint32_t* baudRates - Bitfield that describes all supported baud rates of the serial port represented by the CL_BAUDRATE constants.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_FUNCTION_NOT_FOUND
 *          CL_ERR_INVALID_REFERENCE
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clGetSupportedBaudRates(hSerRef serialRef, uint32_t* baudRates) );

/**
 * @fn		clGetSerialPortIdentifier
 * @brief	Returns a manufacturer-specific identifier for each serial port in your system.
 * @params	[in] uint32_t serialIndex - A zero-based index value. The valid range for serialIndex is 0 to (n–1), where n is the value of numSerialPorts, 
 *                                      as returned by clGetNumSerialPorts.
 *          [out] char* portID - Manufacturer-specific identifier for the serial port.
 *          [in,out] uint32_t* bufferSize - As an input, this value should be the size of the buffer that is passed. On successful return, this parameter contains 
 *                                          the number of bytes written into the buffer, including the NULL termination character.
 *                                          On CL_ERR_BUFFER_TOO_SMALL, this parameter contains the size of the buffer needed to write the data text.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_BUFFER_TOO_SMALL
 *          CL_ERR_INVALID_INDEX
 *          CL_ERR_INVALID_PTR
 *          CL_ERR_FUNCTION_NOT_FOUND
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clGetSerialPortIdentifier(uint32_t serialIndex, char* portID, uint32_t* bufferSize) );

/**
 * @fn		clSetBaudRate
 * @brief	Sets the baud rate for the serial port of the selected device. Use clGetSupportedBaudRate to determine supported baud rates.
 * @params	[in] hSerRef serialRef - Handle to serial port
			[in] uint32_t baudRate - The baud rate you want to use. This parameter expects the values represented by the CL_BAUDRATE constants.
 * @return	CL_ERR_NO_ERR
 *          CL_ERR_BAUD_RATE_NOT_SUPPORTED
 *          CL_ERR_INVALID_REFERENCE
 *          CL_ERR_FUNCTION_NOT_FOUND
 */
KYCLSER_API int32_t KYCLSER_CALLCONV FUNCPREFIX( clSetBaudRate(hSerRef serialRef, uint32_t baudRate) );

#ifdef __cplusplus
} // extern "C" {
#endif

#endif /* clserkyi_h_ */