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
    
    @abstractmethod
    def from_path(self, path: pathlib.Path) -> BaseFpmImageMetadata:
        pass

    @property
    @abstractmethod
    def file_name(self) -> str:
        pass

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

    @property
    def file_name(self):
        ledx = str(self.led_no_x)
        ledy = str(self.led_no_y)
        exposure = str(self.exposure)
        channel = str(self.channel)
        file_name = ledx+"_"+ledy+"_"+channel+"_"+exposure+".npy"
        return file_name
    

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

    @classmethod
    def from_array(cls, image: np.ndarray, path: pathlib.Path, metadata: BaseFpmImageMetadata):
        path = path/metadata.file_name
        print("PATH", path, type(path))
        np.save(path, image)
        return cls(path, metadata)

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

    def add_images(self, images: np.ndarray[FpmImage], config: BaseFpmConfig):
        for image in images:
            wavevector = config.calculate_wavevector(image.metadata)
            self.images[wavevector] = image

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

imagen_nueva = np.ones(shape=(3, 3))
print(imagen_nueva)

exposure = 10
channel = "r"
led_no_x = 12
led_no_y = 16
img_metadata = LedMatrixFpmImageMetadata(exposure, channel, led_no_x, led_no_y)
print(img_metadata)

path = pathlib.Path("/home/dina/facultad/labo-6y7/git-ale-dina/scripts/software-nuevo")
fpm_image = FpmImage.from_array(imagen_nueva, path,img_metadata)

imagen_2 = np.zeros(shape=(3,3))
print(imagen_2)
imagen_2


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
