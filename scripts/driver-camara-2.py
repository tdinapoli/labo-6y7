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
        self.initParams = ky.KYFGLib_InitParameters()
        ky.KYFGLib_Initialize(initParams)

        self.grabberIndex = 0 #número del grabber de la lista de grabbers

        fgAmount, dev_info = _connectToGrabber(grabberIndex)

    def _connectToGrabber(grabberIndex):
        _, fgAmount = ky.KY_DeviceScan()
        _, dev_info = ky.KY_DeviceInfo(grabberIndex)
        return fgAmount, dev_info
        


def connectToGrabber(grabberIndex):
    global handle
    (connected_fghandle,) = ky.KYFG_Open(grabberIndex)
    connected = connected_fghandle.get()
    handle[grabberIndex] = connected


camara = Camera()
imperx = ImperexCamera(camara)
