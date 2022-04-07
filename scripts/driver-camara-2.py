import KYFGLib as ky
import ctypes
import time

import numpy as np
import matplotlib.pyplot as plt

from abc import ABC, abstractmethod
from typing import Tuple, Optional

class Camera(ABC):
    @abstractmethod
    def __init__(self, bit_depth: int = 8, roi: Optional[Roi] = None):
        pass

    @abstractmethod
    def set_gain_exposure(self, gain: int, exposure: int):
        pass

    @abstractmethod
    def get_frame(self) -> np.ndarray:
        pass

class ImperexCamera(Camera):
    def __init__(self, bit_depth: int = 8, roi: Optional[Roi] = None):
        self.grabberIndex = 0
        self.streamInfoStruct = StreamInfoStruct()
        initParams = ky.KYFGLib_InitParameters()
        ky.KYFGLib_InitParameters(initParams)

        (KYFG_Scan_status, fgAmount) = ky.KY_DeviceScan()
        (status, dev_info) = ky.KY_DeviceInfo(grabberIndex)
        self.camHandleArray = [[0]]
        self.handle = [0]
        self.buffHandle = ky.STREAM_HANDLE()

    ##########Conexión al grabber###############################################

        connection = -1
        try:
            connection = connectToGrabber(grabberIndex)
        except ky.KYException as err:
            print('error')

        if (connection == 0):
            (KYDeviceEventCallBackRegister_status,) = KYDeviceEventCallBackRegister(handle[grabberIndex], Device_event_callback_func, self.handle[self.grabberIndex])

    #########Conectamos la camara########################## 

        (CameraScan_status, camHandleArray[grabberIndex]) = ky.KYFG_UpdateCameraList(handle[grabberIndex])
        cams_num = len(camHandleArray[grabberIndex])
        if (cams_num < 1):
            print("no se encontraron camaras")
        (KYFG_CameraOpen2_status,) = ky.KYFG_CameraOpen2(camHandleArray[grabberIndex][0], None)
        if (KYFG_CameraOpen2_status == ky.FGSTATUS_OK):
            print("camara conectada correctamente")
        pass

def connectToGrabber(grabberIndex):
    global handle
    (connected_fghandle,) = ky.KYFG_Open(grabberIndex)
    connected = connected_fghandle.get()
    handle[grabberIndex] = connected


camara = Camera()
imperx = ImperexCamera(camara)
