from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, fields
from typing import Dict, Literal, Optional, Sequence, Tuple, Union

import numpy as np

Color = Literal["r", "g", "b", "rgb"]

@dataclass(frozen=True)
class BaseFpmImageMetadata:
    exposure: float
    channel: str


class LedMatrixFpmImageMetadata(BaseFpmImageMetadata):
    led_no_x: int
    led_no_y: int

    @classmethod
    def from_path(path: pathlib.Path)
        parts = path.stem.split("_")
        x = int(parts[0])
        y = int(parts[1])
        color = parts[2]
        exposure = int(parts[3])
        return cls(exposure, color, x, y)


@dataclass
class BaseFpmConfig:
    objetive_na: float
    image_size: Tuple[int, int]

    @property
    def image_metadata_class(self):
        return BaseFpmImageMetadata
        #retrunr LedMatrixFpmImageMetadata o correspondiente

    def calculate_wavevector(self, metadata: LedMatrixFpmImageMetadata):
        wavelength = self.wavelengths[metadata.channel]
        x, y, z = self.calculate_led_pos
        k_versor = (-x, -y, -z)/(np.sqrt(x**2 +y**2 + z**2))
        k = 2*np.pi/ wavelength
        k_vector = k*k_versor
        return np.array(k_vector)

    @abstractmethod
    def calculate_led_pos(self) ->  Tuple(float, float, float)
        pass
    

@dataclass
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
    def from_json(cls, json_string: str) -> FpmConfig:
        data = json.loads(json_string)
        return cls(**data["fpm_config"])

    def to_json(self, json_string: str):
        data = {"fpm_comfig": self.to_dict()}
        with open(json_string, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

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
    
    def from_path(self, path) -> FpmConfig:
        with open(path) as f:
            data = json.load(f)
        cfg = FpmConfig.from_json(data)
        return cfg

    def calculate_led_pos(self, metadata: LedMatrixFpmImageMetadata):
        centerx, centery = self.config.center
        height = self.config.sample_height_mm
        led_gap = self.config.led_gap_mm
        posx, posy = metadata.led_no_x, metadata.led_no_y
        x = (centerx - posx) * led_gap
        y = (centery - posy) * led_gap
        z = height
        return led_positions


@dataclass
class FpmImage:
    path: pathlib.Path
    metadata: BaseFpmImageMetadata

    @property
    def image(self):
        return np.load(str(self.path))


@dataclass(frozen=True)
class FpmChannel:
    path: pathlib.Path
    config: FpmConfig
    images: dict[k, FpmImage] = fields(default_factory=dict)

    def __post_init__():
        for p in self.path.glob("*.npy"):
            fpim = FpmImage(p, config.image_metadata_class(p))
            k = config.calculate_wavevector(fpim.metadata)
            images[k] = fpim

    def iter_images(self):
        yield from self.images.items()


@dataclass
class FpmDataset:
    path: pathlib.Path
    colors: Sequence[Color]
    config: FpmConfig
    images: Dict[Color, Dict[Tuple[int, int], FpmImage]]
    channels: dict[str, FpmChannel]

    @classmethod
    def from_path(
        cls, path: Union[str, pathlib.Path], mmap: Optional[str] = "r"
    ) -> FpmDataset:
        if isinstance(path, str):
            path = pathlib.Path(path)
        if not path.exists():
            raise FileNotFoundError(str(path))
        if not path.is_dir():
            raise NotADirectoryError(str(path))

        with open(path.joinpath("config.json"), mode="r") as f:
            config = FpmConfig.from_json(f.read())

        images = [
            FpmImage.from_file(file, mmap=mmap)
            for file in path.glob("??_??_*_*.npy")
        ]

        colors = list(set([image.color for image in images]))

        ordered_images = {
            color: {
                (image.x, image.y): image
                for image in images
                if image.color == color
            }
            for color in colors
        }

        return cls(path, colors, config, ordered_images)

    def get_image(self, x, y, color):
        return self.images[color][(x, y)]


    def calculate_wavevector(self):
        k_vectors = {}
        for color in self.colors:
            wavelength = self.config.wavelengths[color]
            k_vectors[color]=[]
            for pos in self.calculate_led_pos():
                x,y,z = pos
                k_versor = (x,y,-z)/(np.sqrt(x**2 +y**2 + z**2))
                k = 2*np.pi/ wavelength
                k_vectors[color].append(k*k_versor)
        return k_vectors
        

def process(fpim):
    img = fpim.image
    img(img>mx) = np.nan
    img(img<mn) = np.nan
    img = img - background
    return img / fpim.exp


avg = None
ds = FpmDataset.from_path()
for chname, channel in ds.channels.items():
    print(chname)
    for k, fpim in channel.iter_images():
        image = process(fpim)
        if avg is None:
            avg = image
        else:
            avg += image

import matplotlib.pyplot as plt
#from fpmordered_images.microscope.base import Microscope, Optics, Illumination

path = "/home/chanoscopio/fpm_samples/22_junio_V2"
ds = FpmDataset.from_path(path)
#print(ds.images)
#img = ds.get_image(16, 16, "r")
x0, y0, x1, y1 = 3000, 3000, 4000, 4000
#img = img.get_patch(x0, y0, x1, y1)
##plt.imshow(img)
##plt.show()
config  = ds.config
#print(ds.calculate_led_pos())
print(ds.calculate_wavevector())

Leds = np.arange(13,19)
patch = []
for i in Leds:
    for j in Leds:
        img = ds.get_image(i, j, "b")
        img = img.get_patch(x0, y0, x1, y1)
        patch.append(img)


#print(parches)
#opt = Optics(config['objective_na'], 1)
#il = Illumination(config['sample_hight'], config['pixel_size_um']*8, config['wavelenght'])
#cam = Camera(config['pixel_size_um'], config['image_size'], 2**12-1)
#micro = Microscope(opt, il, cam)

############## RECONSTRUCCION ##################

import fpmsample.math as pmath
from stitch import Patch, Picture
from fpmsample.simicro import RealMicroscope
from phaseopt.containers import Options, ResultsContainer
from phaseopt.solver import solver_run

import itertools as it
from tifffile import imwrite
from pathlib import Path
import os

dirname = Path("/home/chanoscopio/fpm_samples/22_junio_V2")
rm = RealMicroscope.from_dirname(dirname=dirname, color='b')
overlap = 15

pic_hr = Picture.from_microscope(rm, overlap=overlap, outfile="ft_image.h5py")
opts = Options(
    record_rss=True,
    record_angular_rss=True,
    xt=None,
    max_iter=7,
)


pupil = pmath.aberrated_pupil(1e-6, rm)
rm.y0, rm.x0 = pic_hr.get_lr_center(patch.position)
# rm._load_samples_dask()
delta_gk = rm.get_phaseopt_input(background_matrix=10000, color=color)
centers = rm.centers(mode="raw")
centers = np.array((list(centers)))
n = 16
delta_gk = it.islice(delta_gk, n)



res = solver_run(
    delta_gk,
    centers,
    rm.no,
    rm.patch,
    rm.nsyn,
    p0=pupil,
    microscope=rm,
    method="known_corrections",
)



mag = np.abs(res)
mag = np.uint16(mag * (np.iinfo(np.uint16).max / np.max(mag)))  # Rescaling

delta_gk = rm.get_phaseopt_input(background_matrix=1000)
patch.image = np.flip(res, axis=0)

plt.imshow(mag)
plt.show(mag)


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
