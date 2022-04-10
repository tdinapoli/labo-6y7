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
        GRABBER_INDEX = 0 #número del grabber de la lista de grabbers
        MAX_BOARDS = 4
        MAX_CAMS = 4
        DEVICE_QUEUED_BUFFERS_SUPPORTED = "FW_DmaCapable_QueuedBuffers_Imp"

        self.init_params = ky.KYFGLib_InitParameters()
        self.connection = -1
        self.stream_info_struct = self.StreamInfoStruct()
        self.cam_handle_array = [[0 for x in range(0)] for y in range(MAX_BOARDS)]
        self.handle = [0 for i in range(MAX_BOARDS)]
        self.camera_stream_handle = 0
        self.frame_data_size = 0
        self.frame_data_aligment = 0
        self.stream_buffer_handle = [0 for i in range(16)]
        self.stream_alligned_buffer = [0 for i in range(16)]

        ky.KYFGLib_Initialize(init_params)
        self._connect_to_grabber(self)

    def _connect_to_grabber(self):
        _, fg_amount = ky.KY_DeviceScan()
        _, dev_info = ky.KY_DeviceInfo(GRABBER_INDEX)
        try:
            self.connection = self._set_grabber_connection(self, GRABBER_INDEX)
        except ky.KYException as err:
            print("Error al conectar con el frame grabber")
        return

    def _set_grabber_connection(self, GRABBER_INDEX):
        self.handle
        connected_fghandle, = ky.KYFG_Open(GRABBER_INDEX)
        connected = connected_fghandle.get()
        self.handle[GRABBER_INDEX] = connected
        ky.KYFG_GetGrabberValueInt(self.handle[GRABBER_INDEX], DEVICE_QUEUED_BUFFERS_SUPPORTED)
        return 0

    def _connect_to_camera(self):
        _, self.cam_handle_array[GRABBER_INDEX] = ky.KYFG_UpdateCameraList(self.handle[GRABBER_INDEX])
        cams_num = len(self.cam_handle_array[GRABBER_INDEX])
        if (cams_num < 1):
            print("No se encontraron camaras")
        KYFG_CameraOpen2_status, = ky.KYFG_CameraOpen2(self.cam_handle_array[GRABBER_INDEX][0], None)
        if KYFG_CameraOpen2_status == ky.FGSTATUS_OK:
            print("Camara conectada correctamente")



    class StreamInfoStruct:
        def __init__(self):
            self.width = 640
            self.height = 480
            self.callbackCount = 0
            return
        

camara = Camera()
imperx = ImperexCamera(camara)
