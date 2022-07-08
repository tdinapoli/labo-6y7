from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Dict, Literal, Optional, Sequence, Tuple, Union
from abc import ABC, abstractmethod

import numpy as np

#Color = Literal["r", "g", "b", "rgb"]
Channel = Literal["r", "g", "b"] #falta gene3rar carpetas de transmision y reflexión para agregarlas después acá
#Kvector
#Kvec = Tuple(float, float)
#FpmConfig = TypeVar()

@dataclass(frozen=True)
class BaseFpmImageMetadata(ABC):
    exposure: float
    channel: str

@dataclass(frozen=True)
class BaseFpmConfig(ABC):
    objetive_na: float
    image_size: Tuple[int, int]

    @property
    @abstractmethod
    def image_metadata_class(self) -> BaseFpmImageMetadata:
        pass

    @abstractmethod
    def calculate_led_pos(self, metadata: BaseFpmImageMetadata) ->  Tuple[float, float, float]:
        pass

    def calculate_wavevector(self, metadata: LedMatrixFpmImageMetadata):
        wavelength = self.wavelengths[metadata.channel]
        x, y, z = self.calculate_led_pos(metadata)
        k_versor = (-x, -y, -z)/(np.sqrt(x**2 +y**2 + z**2))
        k = 2*np.pi/ wavelength
        k_vector = k*k_versor
        return np.array(k_vector)

@dataclass(frozen=True)
class LedMatrixFpmImageMetadata(BaseFpmImageMetadata):
    led_no_x: int
    led_no_y: int

    @classmethod
    def from_path(cls, path: pathlib.Path):
        parts = path.stem.split("_")
        x = int(parts[0])
        y = int(parts[1])
        color = parts[2]
        exposure = int(parts[3])
        return cls(exposure, color, x, y)
    

@dataclass(frozen=True)
class LedMatrixFpmConfig(BaseFpmConfig):
    wavelengths: Dict[Color, float]
    sample_height_mm: float
    center: Tuple[int, int]
    matrix_size: int
    led_gap_mm: float
    pixel_size_um: float

    @property
    def image_metadata_class(self):
        return LedMatrixFpmImageMetadata

    ## cambiar con dataclass wizard
    @classmethod
    def from_json(cls, json_string: str):
        data = json.loads(json_string)
        return cls(**data["fpm_config"])

    def to_json(self, json_string: str):
        data = {"fpm_comfig": self.to_dict()}
        with open(json_string, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    @classmethod
    def from_path(cls, path):
        path = pathlib.Path(path) / "config.json"
        with path.open(mode="r", encoding="utf-8") as f:
            return cls.from_json(f.read())

    def to_dict(self) -> dict:
        data = {
            "wavelengths": self.wavelengths,
            "sample_height_mm": self.sample_height_mm,
            "center": self.center,
            "matrix_size": self.matrix_size,
            "led_gap_mm": self.led_gap_mm,
            "objetive_na": self.objetive_na,
            "pixel_size_um": self.pixel_size_um,
            "image_size": self.image_size,
        }
        return data

    def calculate_led_pos(self, metadata: LedMatrixFpmImageMetadata):
        centerx, centery = self.center
        height = self.sample_height_mm
        led_gap = self.led_gap_mm
        posx, posy = metadata.led_no_x, metadata.led_no_y
        x = (centerx - posx) * led_gap
        y = (centery - posy) * led_gap
        z = height
        return np.asarray([x, y, z])


@dataclass
class FpmImage:
    path: pathlib.Path
    metadata: BaseFpmImageMetadata

    @property
    def image(self):
        return np.load(str(self.path))

    @property
    def mmap_image(self):
        return np.load(str(self.path), mmap_mode="r")

@dataclass(frozen=True)
class FpmChannel:
    path: pathlib.Path
    config: BaseFpmConfig
    channel: Channel
    images: dict[Tuple(float, float), FpmImage] = field(default_factory=dict)

    def __post_init__(self):
        for p in self.path.glob("*_"+self.channel+"_*.npy"): #cambiar a solo *.npy y fijarse si se puede sacar de la metadata el path
            fpim = FpmImage(p, self.config.image_metadata_class.from_path(p))
            k = self.config.calculate_wavevector(fpim.metadata)
            self.images[tuple(k)] = fpim

    def iter_images(self):
        for k, fpim in self.images.items():
            yield np.asarray(k), fpim

    def get_patch(self, k, xslice = slice(0,None),
            yslice=slice(0,None)):
        return self.images[k][xslice, yslice]



@dataclass
class FpmDataset:
    path: pathlib.Path
    config: BaseFpmConfig
    channels: Dict[Channel, FpmChannel]

    @classmethod
    def from_path(
            cls, config_class: BaseFpmConfig, path: Union[str, pathlib.Path],
            ds_channels: list[str] = ["r", "g", "b"], mmap: Optional[str] = "r"
    ) -> FpmDataset:
        if isinstance(path, str):
            path = pathlib.Path(path)
        if not path.exists():
            raise FileNotFoundError(str(path))
        if not path.is_dir():
            raise NotADirectoryError(str(path))

        config = config_class.from_path(path)
        channels = {}

        for channel in ds_channels:
            channels[channel] = FpmChannel(path, config, channel)

        return cls(path, config, channels)


#for k, fpim in ds.channels[0].iter_images():
#    print(k, fpim.mmap_image.shape, fpim.mmap_image.dtype)



#def process(fpim):
#    img = fpim.image
#    img(img>mx) = np.nan
#    img(img<mn) = np.nan
#    img = img - background
#    return img / fpim.exp




#ds = FpmDataset.from_path()
#for chname, channel in ds.channels.items():
#    print(chname)
#    for k, fpim in channel.iter_images():
#        image = process(fpim)
#        if avg is None:
#            avg = image
#        else:
#            avg += image
#
#import matplotlib.pyplot as plt
##from fpmordered_images.microscope.base import Microscope, Optics, Illumination
#
#path = "/home/chanoscopio/fpm_samples/22_junio_V2"
#ds = FpmDataset.from_path(path)
##print(ds.images)
##img = ds.get_image(16, 16, "r")
#x0, y0, x1, y1 = 3000, 3000, 4000, 4000
##img = img.get_patch(x0, y0, x1, y1)
###plt.imshow(img)
###plt.show()
#config  = ds.config
##print(ds.calculate_led_pos())
#print(ds.calculate_wavevector())
#
#Leds = np.arange(13,19)
#patch = []
#for i in Leds:
#    for j in Leds:
#        img = ds.get_image(i, j, "b")
#        img = img.get_patch(x0, y0, x1, y1)
#        patch.append(img)


#print(parches)
#opt = Optics(config['objective_na'], 1)
#il = Illumination(config['sample_hight'], config['pixel_size_um']*8, config['wavelenght'])
#cam = Camera(config['pixel_size_um'], config['image_size'], 2**12-1)
#micro = Microscope(opt, il, cam)

############## RECONSTRUCCION ##################

#import fpmsample.math as pmath
#from stitch import Patch, Picture
#from fpmsample.simicro import RealMicroscope
#from phaseopt.containers import Options, ResultsContainer
#from phaseopt.solver import solver_run
#
#import itertools as it
#from tifffile import imwrite
#from pathlib import Path
#import os
#
#dirname = Path("/home/chanoscopio/fpm_samples/22_junio_V2")
#rm = RealMicroscope.from_dirname(dirname=dirname, color='b')
#overlap = 15
#
#pic_hr = Picture.from_microscope(rm, overlap=overlap, outfile="ft_image.h5py")
#opts = Options(
#    record_rss=True,
#    record_angular_rss=True,
#    xt=None,
#    max_iter=7,
#)
#
#
#pupil = pmath.aberrated_pupil(1e-6, rm)
#rm.y0, rm.x0 = pic_hr.get_lr_center(patch.position)
## rm._load_samples_dask()
#delta_gk = rm.get_phaseopt_input(background_matrix=10000, color=color)
#centers = rm.centers(mode="raw")
#centers = np.array((list(centers)))
#n = 16
#delta_gk = it.islice(delta_gk, n)
#
#
#
#res = solver_run(
#    delta_gk,
#    centers,
#    rm.no,
#    rm.patch,
#    rm.nsyn,
#    p0=pupil,
#    microscope=rm,
#    method="known_corrections",
#)
#
#
#
#mag = np.abs(res)
#mag = np.uint16(mag * (np.iinfo(np.uint16).max / np.max(mag)))  # Rescaling
#
#delta_gk = rm.get_phaseopt_input(background_matrix=1000)
#patch.image = np.flip(res, axis=0)
#
#plt.imshow(mag)
#plt.show(mag)


#avg = None
#path = "/home/chanoscopio/fpm_samples/22_junio_V2/"
#path = pathlib.Path(path)
#json_string = "config.json"
#cfg = LedMatrixFpmConfig.from_path(path)
#ch = FpmChannel(path, cfg, "b")
#avg = None
#
#def process(fpim):
#    return fpim.mmap_image[5000:5600, 5000:5600] / fpim.metadata.exposure
#
#def myfft(k, im):
#    sh = im.shape
#    pix_size = 3.2e-3
#    plane_x, plane_y = np.meshgrid(range(sh[0]), range(sh[1]))
#    return np.fft.fftshift(np.fft.fft2(im)) * np.exp(1j*(k[0]*plane_x*pix_size + k[1]*plane_y*pix_size))
#
#
#for k, fpim in ch.iter_images():
#    #print(k, fpim.mmap_image.shape, fpim.mmap_image.dtype)
#    image = process(fpim)
#    image = myfft(k, image)
#    if avg is None:
#        avg = image
#    else:
#        avg += image
#
#import matplotlib.pyplot as plt
#plt.imshow(np.abs(avg))
#plt.show()


path = "/home/chanoscopio/fpm_samples/22_junio_V2/"
path = pathlib.Path(path)
json_string = "config.json"
colors = ["r"]
ds = FpmDataset.from_path(LedMatrixFpmConfig, path, colors)
print(ds.channels)

#generate_reconstruction_dirs()



@dataclass
class FpmAcquisitionSetup:
    name: Optional[str] = None
    description: Optional[str] = None
    sample_dir: Optional[pathlib.Path] = None
    size: Optional[int] = None
    colors: Optional[Sequence[Color]] = None
    red_exp: Optional[int] = None
    green_exp: Optional[int] = None
    blue_exp: Optional[int] = None
    scheme: Optional[str] = None
    min_exposure: Optional[int] = None
    max_exposure: Optional[int] = None
    config: Optional[pathlib.Path] = None
    exposure_file: Optional[pathlib.Path] = None
    bit_depth: Optional[int] = None
    dry_run: Optional[bool] = None
    dummy_devices: Optional[bool] = None
