/************************************************************************ 
*   File: KAYA_SystemStartup.c
*   This program is intended to be added to the system startup and perform various initializations of KAYA devices
*
*   KAYA Instruments Ltd.
*************************************************************************/

#include "stdafx.h"

#include "KYFGLib.h"


#if !defined(_countof)
#define _countof(_Array) (sizeof(_Array) / sizeof(_Array[0]))
#endif

#ifdef _MSC_VER
#define PRISIZET "Iu" //https://msdn.microsoft.com/en-us/library/tcxf1dw6%28v=vs.110%29.aspx
#else
#define PRISIZET "zu"
#endif

#define MAXBOARDS 4
FGHANDLE handle[MAXBOARDS];

int ConnectToDevice(unsigned int deviceIndex)
{
    if ((handle[deviceIndex] = KYFG_Open(deviceIndex)) != -1) // connect to selected device
    {
        printf("Good connection to grabber #%d, handle=%X\n", deviceIndex, handle[deviceIndex] );
        return 0;
    }
    else
    {
        printf("Could not connect to grabber #%d\n", deviceIndex);
        return -1;
    }
}

void InitDevice(FGHANDLE fgHandle, KY_DEVICE_INFO* pDeviceInfo)
{
    fgHandle; // suppress warning
    if (KY_DEVICE_PROTOCOL_CLHS == pDeviceInfo->m_Protocol)
    {
        printf("Found CLHS-X device on PCI slot {%d:%d:%d}\n", pDeviceInfo->nBus, pDeviceInfo->nSlot, pDeviceInfo->nFunction);

        //KYFG_SetGrabberValueFloat(fgHandle, "PWM_min_temp", 61);
        //KYFG_SetGrabberValueFloat(fgHandle, "PWM_max_temp", 68);
    }
}

void CloseDevice(unsigned int deviceIndex)
{
    if (INVALID_FGHANDLE != handle[deviceIndex])
    {
        if (FGSTATUS_OK != KYFG_Close(handle[deviceIndex])) // Close the selected device and unregisters all associated routines
        {
            printf("wasn't able to close grabber #%d\n", deviceIndex);
        }
    }
    else
    {
        printf("grabber #%d wasn't open\n", deviceIndex);
    }
}

int main()
{
    int infosize = 0;
    int deviceIndex = 0;
    KYFGLib_InitParameters kyInit;

    memset(&kyInit, 0, sizeof(kyInit));
    kyInit.version = 1;

    if (FGSTATUS_OK != KYFGLib_Initialize(&kyInit))
    {
        printf("Library initialization failed \n ");
        return 1;
    }

    for(deviceIndex = 0; deviceIndex < MAXBOARDS; deviceIndex++)
    {
        handle[deviceIndex] = INVALID_FGHANDLE;
    }


    KY_DeviceScan(&infosize);// Retrieve the number of virtual and hardware devices connected to PC
    printf("%d devices found:\n", infosize);

    for(deviceIndex = 0; deviceIndex < infosize; deviceIndex++)
    {
        KY_DEVICE_INFO deviceInfo;
        memset(&deviceInfo, 0, sizeof(KY_DEVICE_INFO));
        deviceInfo.version = KY_MAX_DEVICE_INFO_VERSION;
        if (FGSTATUS_OK != KY_DeviceInfo(deviceIndex, &deviceInfo))
        {
            printf("wasn't able to retrive information from device #%d\n", deviceIndex);
            continue;
        }
        printf("[%d] %s on PCI slot {%d:%d:%d}: Protocol 0x%X, Generation %d\n", deviceIndex + 1,
               deviceInfo.szDeviceDisplayName,
               deviceInfo.nBus, deviceInfo.nSlot, deviceInfo.nFunction, 
               deviceInfo.m_Protocol, deviceInfo.DeviceGeneration);

        ConnectToDevice(deviceIndex);

        InitDevice(handle[deviceIndex], &deviceInfo);

        CloseDevice(deviceIndex);
    }// for(deviceIndex = 0; deviceIndex < infosize; deviceIndex++)

    printf("Press any key to exit");
    getchar();

    return 0;
}

