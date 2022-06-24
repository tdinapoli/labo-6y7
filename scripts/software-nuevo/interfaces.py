from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Dict, Literal, Optional, Sequence, Tuple, Union

import numpy as np

Color = Literal["r", "g", "b", "rgb"]


@dataclass
class FpmConfig:
    wavelengths: Dict[Color, float]
    sample_height_mm: float
    center: Tuple[int, int]
    matrix_size: int
    led_gap_mm: float
    objetive_na: float
    pixel_size_um: float
    image_size: Tuple[int, int]

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


@dataclass
class FpmImage:
    frame: np.ndarray
    x: int
    y: int
    color: Color
    exposure: Union[int, float]

    def __str__(self):
        return (
            f"{self.x:02d}_"
            f"{self.y:02d}_"
            f"{self.color}_"
            f"{self.exposure:d}"
        )

    def get_name(self) -> str:
        return self.__str__() + ".npy"

    @classmethod
    def from_file(
        cls, path: Union[str, pathlib.Path], mmap: Optional[str] = "r"
    ) -> FpmImage:
        if isinstance(path, str):
            path = pathlib.Path(path)
        if not path.exists():
            raise FileNotFoundError(str(path))
        if not path.is_file():
            raise IsADirectoryError(str(path))

        parts = path.stem.split("_")
        x = int(parts[0])
        y = int(parts[1])
        color = parts[2]
        exposition = int(parts[3])
        frame = np.load(str(path), mmap_mode=mmap)
        return cls(frame, x, y, color, exposition)

    def save(self, path: Union[str, pathlib.Path]) -> str:
        name = path.joinpath(self.get_name())
        np.save(name, self.frame)
        return name

    def get_patch(self, x0, y0, x1, y1):
        return self.frame[x0:x1, y0:y1]


@dataclass
class FpmDataset:
    path: pathlib.Path
    colors: Sequence[Color]
    config: FpmConfig
    images: Dict[Color, Dict[Tuple[int, int], FpmImage]]

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
    def pr(self):
        return self.images['r']

    
    def get_image(self, x, y, color):
        return self.images[color][(x, y)]

    #def calculate_led_pos(self, )

import matplotlib.pyplot as plt
from fpm.microscope.base import Microscope, Optics, Illumination

path = "/home/chanoscopio/fpm_samples/22_junio_V2"
ds = FpmDataset.from_path(path)
print(ds.pr())
#img = ds.get_image(16, 16, "r")
#x0, y0, x1, y1 = 3000, 3000, 4000, 4000
#img = img.get_patch(x0, y0, x1, y1)
##plt.imshow(img)
##plt.show()
config  = ds.config

Leds = np.arange(13,19)
parches = []
for i in Leds:
    for j in Leds:
        img = ds.get_image(i, j, "b")
        img = img.get_patch(x0, y0, x1, y1)
        parches.append(img)


print(config)
opt = Optics(config['objective_na'], 1)
il = Illumination(config['sample_hight'])
#micro = Microscope(config)


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
