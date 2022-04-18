import KYFGLib as ky
import ctypes

import numpy as np
import matplotlib.pyplot as plt

from abc import ABC, abstractmethod
from typing import Tuple, Optional

from time import sleep, time
import sys

Roi = Tuple[int, int]

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
        self.grabber_index = 0 #número del grabber de la lista de grabbers
        self.max_boards = 4
        self.max_cams = 4
        self.device_queued_buffers_supported = "FW_DmaCapable_QueuedBuffers_Imp"

        self.init_params = ky.KYFGLib_InitParameters()
        self.connection = -1
        self.stream_info_struct = self.StreamInfoStruct()
        self.cam_handle_array = [[0 for x in range(0)] for y in range(self.max_boards)]
        self.handle = [0 for i in range(self.max_boards)]
        self.camera_stream_handle = 0
        self.frame_data_size = 0
        self.frame_data_aligment = 0
        self.stream_buffer_handle = [0 for i in range(16)]
        self.stream_alligned_buffer = [0 for i in range(16)]
        self._max_image_width = 9344
        self._max_image_height = 7000
        self.image_width = 0
        self.image_height = 0
        self.n_frames = 1
        self.camera_index = 0
        self.image = 0
        self._stream_callback_func.__func__.data = 0
        self._stream_callback_func.__func__.copyingDataFlag = 0

        ky.KYFGLib_Initialize(self.init_params)
        self._connect_to_grabber()
        self._connect_to_camera()
        self._set_roi(roi)

        _, self.exposure_time =  ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureTime")
        _, self.gain = ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "Gain")

        _, self.camera_stream_handle = ky.KYFG_StreamCreate(self.cam_handle_array[self.grabber_index][0], 0)

        _, = ky.KYFG_StreamBufferCallbackRegister(self.camera_stream_handle, self._stream_callback_func, ky.py_object(self.stream_info_struct))

        self._allocate_memory()

    def _connect_to_grabber(self):
        _, fg_amount = ky.KY_DeviceScan()
        _, dev_info = ky.KY_DeviceInfo(self.grabber_index)
        try:
            self.connection = self._set_grabber_connection()
        except ky.KYException as err:
            print("Error al conectar con el frame grabber")
        return

    def _set_grabber_connection(self):
        self.handle
        connected_fghandle, = ky.KYFG_Open(self.grabber_index)
        connected = connected_fghandle.get()
        self.handle[self.grabber_index] = connected
        ky.KYFG_GetGrabberValueInt(self.handle[self.grabber_index], self.device_queued_buffers_supported)
        return 0

    def _connect_to_camera(self):
        _, self.cam_handle_array[self.grabber_index] = ky.KYFG_UpdateCameraList(self.handle[self.grabber_index])
        cams_num = len(self.cam_handle_array[self.grabber_index])
        if (cams_num < 1):
            print("No se encontraron camaras")
        KYFG_CameraOpen2_status, = ky.KYFG_CameraOpen2(self.cam_handle_array[self.grabber_index][0], None)
        if KYFG_CameraOpen2_status == ky.FGSTATUS_OK:
            print("Camara conectada correctamente")

    def _set_roi(self, roi):
        if roi is None:
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Width", self._max_image_width)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Height", self._max_image_height)
            self.image_height = self._max_image_height
            self.image_width = self._max_image_width

        else: 
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Width", roi[0])
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Height", roi[1])

    def _allocate_memory(self):
        _, payload_size, _, _ = ky.KYFG_StreamGetInfo(self.camera_stream_handle, ky.KY_STREAM_INFO_CMD.KY_STREAM_INFO_PAYLOAD_SIZE)

        _, buf_allignment, _, _ = ky.KYFG_StreamGetInfo(self.camera_stream_handle, ky.KY_STREAM_INFO_CMD.KY_STREAM_INFO_BUF_ALIGNMENT)

        for iFrame in range(len(self.stream_buffer_handle)):
            self.stream_alligned_buffer[iFrame] = ky.aligned_array(buf_allignment, ky.c_ubyte, payload_size)
            _, self.stream_buffer_handle[iFrame] = ky.KYFG_BufferAnnounce(self.camera_stream_handle, self.stream_alligned_buffer[iFrame], None)


    def _stream_callback_func(self, buff_handle, user_context):
        if buff_handle == 0:
            self._stream_callback_func.__func__.copyingDataFlag = 0
            return

        stream_info = ky.cast(user_context, ky.py_object).value
        stream_info.callbackCount = stream_info.callbackCount + 1

        _, pointer, _, _ = ky.KYFG_BufferGetInfo(buff_handle, ky.KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_BASE)
        _, buffer_size, _, _ = ky.KYFG_BufferGetInfo(buff_handle, ky.KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_SIZE)

        buffer_byte_array = bytearray(ctypes.string_at(pointer, buffer_size))
        data = np.frombuffer(buffer_byte_array, dtype=np.ubyte)
        self.image = data.reshape(self.image_height, self.image_width)

        if self._stream_callback_func.__func__.copyingDataFlag == 0:
           self._stream_callback_func.__func__.copyingDataFlag = 1

        sys.stdout.flush()
        self._stream_callback_func.__func__.copyingDataFlag = 0

        return 

    def _start_camera(self):
        # put all buffers to input queue
        KYFG_BufferQueueAll_status, = ky.KYFG_BufferQueueAll(self.camera_stream_handle, ky.KY_ACQ_QUEUE_TYPE.KY_ACQ_QUEUE_UNQUEUED, ky.KY_ACQ_QUEUE_TYPE.KY_ACQ_QUEUE_INPUT)
        
        KYFG_CameraStart_status, = ky.KYFG_CameraStart(self.cam_handle_array[self.grabber_index][self.camera_index], self.camera_stream_handle, self.n_frames)
        return 0

    def set_gain_exposure(self, exposure_time, gain):
        print(self.exposure_time)
        _,  = ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureTime", exposure_time)
        _, self.exposure_time =  ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureTime")
        print(self.exposure_time)
        print(self.gain)
        _,  = ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "Gain", gain)
        _, self.gain =  ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "Gain")
        print(self.gain)
        
        return

    def get_frame(self):
        sys.stdout.flush()
        t0 = time()
        self._start_camera()
        print(time() - t0)

        sleep(1)
        sys.stdout.flush()
        _, = ky.KYFG_CameraStop(self.cam_handle_array[self.grabber_index][0])
        return self.image

    def close(self):

        _, = ky.KYFG_CameraClose(self.cam_handle_array[self.grabber_index][0])
        _, = ky.KYFG_Close(self.handle[self.grabber_index])

    class StreamInfoStruct:
        def __init__(self):
            self.width = 640
            self.height = 480
            self.callbackCount = 0
            return
        

imperx = ImperexCamera()
imperx.set_gain_exposure(5065.0, 1.25)
sleep(1)
imagen = imperx.get_frame()
imperx.close()
plt.imshow(imagen, cmap='gray', vmin=0, vmax=255)
plt.show()
