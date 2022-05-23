import KYFGLib as ky
import ctypes
import traceback

import numpy as np
import matplotlib.pyplot as plt 
from abc import ABC, abstractmethod
from typing import Tuple, Optional

from time import sleep, time, perf_counter
import sys
import os
import threading
import queue

#Roi = Tuple[int, int]
Roi = Tuple[Tuple[int, int], Tuple[int, int]]


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

class ImperxCamera(Camera):
    def __init__(self, queue, stream_callback_func, bit_depth: int = 8, roi: Optional[Roi] = None):
        inicio_init = perf_counter()
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
        self.n_frames = 1
        self.camera_index = 0
        self.image = 0 
        self._time_stamp = 0
        self.image_offset_x = None
        self.image_offset_y = None
        self.image_width = None
        self.image_height = None
        self.image_array = np.array([])
        self.queue = queue

        ky.KYFGLib_Initialize(self.init_params)
        inicio_grabber = perf_counter()
        self._connect_to_grabber()
        final_grabber = perf_counter()
        print("grabber: ", final_grabber - inicio_grabber)
        inicio_camera = perf_counter()
        self._connect_to_camera()
        final_camera = perf_counter()
        print("camara: ", final_camera - inicio_camera)
        self._set_roi(roi)

        _, self.exposure_time =  ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureTime")
        _, self.gain = ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "Gain")

        #La configuración de los bits del adc y del color puede cambiar si se abre la app de vision point
        #si se quiere cambiar el bit depht o el pixel format hay que cambiar el tipo de dato que aparece
        #en la función _stream_callback_func en data = np.frombuffer(buffer_byte_array, dtype=np.int16)
        # a data = np.frombuffer(buffer_byte_array, dtype=np.uint8)
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "AdcBitDepth", "Bit12")
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "PixelFormat", "Mono12")
        self.bit_depth = ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "AdcBitDepth")
        self.pixel_format = ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "PixelFormat")
        print("Bit Depth ADC:",self.bit_depth)
        print("Bit PixelFormat:",self.pixel_format)

        #seteamos el modo de exposición
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureAuto", "Off")
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "TriggerMode", "Off")
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureMode", "Timed")
        _, _, self.exposure_mode = ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureMode")
        print(ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "TriggerMode"))
        print(ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureAuto"))
        print(self.exposure_mode)

        _, self.camera_stream_handle = ky.KYFG_StreamCreateAndAlloc(self.cam_handle_array[self.grabber_index][0], 1, 0)

        _, = ky.KYFG_StreamBufferCallbackRegister(self.camera_stream_handle, stream_callback_func, ky.py_object(self.stream_info_struct))

        final_init = perf_counter()
        print("tiempo init: ", final_init - inicio_init)

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
            self.image_offset_x = 0
            self.image_offset_y = 0
            self.image_width = self._max_image_width
            self.image_height = self._max_image_height


        else: 
            self.image_offset_x = roi[0][0]
            self.image_offset_y = roi[0][1]
            self.image_width = roi[1][0] - roi[0][0]
            self.image_height = roi[1][1] - roi[0][1]
            print("height", type(self.image_height), self.image_height)
            print("width", type(self.image_width), self.image_width)
            print("offset x", type(self.image_offset_x), self.image_offset_x)
            print("offset y ", type(self.image_offset_y), self.image_offset_y)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], 'OffsetX', self.image_offset_x)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], 'OffsetY', self.image_offset_y)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Width", self.image_width)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Height", self.image_height)
            


    def _start_camera(self, n_frames):
        KYFG_CameraStart_status, = ky.KYFG_CameraStart(self.cam_handle_array[self.grabber_index][self.camera_index], self.camera_stream_handle, n_frames)
        return 0

    def set_gain_exposure(self,gain, exposure_time):
        _,  = ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureTime", exposure_time)
        _, self.exposure_time =  ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureTime")
        _,  = ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "Gain", gain)
        _, self.gain =  ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "Gain")
        
        return

    def get_frame(self, n_frames=1):
        self._start_camera(n_frames)
        sh = self.image_height, self.image_width
        out = []
        while len(out) < n_frames:
            #print("QUEUE ANTES", len(self.queue.queue))
            try:
                raw = self.queue.get(timeout=1)
            except:
                print("exception get_frame")
                _, = ky.KYFG_CameraStop(self.cam_handle_array[self.grabber_index][0])
                with self.queue.mutex:
                    self.queue.queue.clear()
                return
            #print("QUEUE DESPUES", len(self.queue.queue))
            out.append(np.frombuffer(raw, dtype=np.uint16).reshape(sh))
            #print(len(out)) 
        _, = ky.KYFG_CameraStop(self.cam_handle_array[self.grabber_index][0])

        return np.stack(out)

    def close(self):

        _, = ky.KYFG_CameraClose(self.cam_handle_array[self.grabber_index][0])
        _, = ky.KYFG_Close(self.handle[self.grabber_index])

    class StreamInfoStruct:
        def __init__(self):
            self.width = 640
            self.height = 480
            self.callbackCount = 0
            return

#colas
queue = queue.Queue()

def _stream_callback_func(buff_handle, user_context):
    #print("hola")
    if buff_handle == 0:
        return
    _, pointer, _, _ = ky.KYFG_BufferGetInfo(buff_handle, ky.KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_BASE)
    _, buffer_size, _, _ = ky.KYFG_BufferGetInfo(buff_handle, ky.KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_SIZE)

    buffer_byte_array = bytearray(ctypes.string_at(pointer, buffer_size))
    data = np.frombuffer(buffer_byte_array, dtype=np.uint16)
    queue.put(buffer_byte_array, timeout=2)
    #print("QUEUE CALLBACK", len(queue.queue))

#IMPORTANTE: el offset en x va en múltiplos de 32 y el offset de y va en múltiplos de 2
offset_x = int(3200)
offset_y = int(3200)
width = int(offset_x + 640)
height = int(offset_y + 480)
roi_nuestro = ((offset_x,offset_y), (width, height))
roi_nuestro = ((0,0), (512, 512))

imperx = ImperxCamera(queue, _stream_callback_func, roi=roi_nuestro)
try: 
    exp_times = np.linspace(15.0, 2000.0, 50)
#exp_times = [15.0, 100.0, 1000.0, 15000.0, 25000.0, 40500.0]
    means = np.zeros(shape = (len(exp_times), 50))
    stds = np.zeros(shape = (len(exp_times), 50))
    for i in range(1000):
        imagen = imperx.get_frame(1)
        print(i)
#        for i, tiempo_exp in enumerate(exp_times):
#            # imperx.set_gain_exposure(1.25, round(tiempo_exp, 0))
#            sleep(0.1)
#            # _, exposure_time =  ky.KYFG_GetCameraValue(imperx.cam_handle_array[imperx.grabber_index][0], "ExposureTime")
#            # print(exposure_time)
#            #imagen = imperx.get_frame(20)
#            #print(imperx.image_array)
#            #raise Exception
#            for j in range(50):
#                imagen = imperx.get_frame(1)
#                means[i, j] = np.mean(imagen)
#                stds[i, j] = np.std(imagen)
#                print("imagen", j, "tiempo de exposicion", i, j)#round(tiempo_exp, 0))
       # np.save("means_oscuridad_2", means)
       # np.save("stds_oscuridad_2", stds)
       # np.save("tiempos_de_exposicion_oscuridad_2", exp_times)
except Exception as e:
    print("exception:", str(e))
    print(traceback.format_exc())
finally:
    imperx.close()
#plt.plot(exp_times, promedios, "ok")
#plt.show()
#
#np.save("pix_620_480_12bit", promedios)
#np.save("pix_620_480_12bit_exp_time", exp_times)
