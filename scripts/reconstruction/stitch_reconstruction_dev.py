#!/usr/bin/python
# -*- coding: utf-8 -*-
""" File stich_reconstruction.py
UPDATE
Solving the phase retrieval problem using the phaseopt library.
"""
from h5py._hl import base
import numpy as np
import matplotlib.pyplot as plt

import fpmsample.math as pmath
from stitch import Patch, Picture
from fpmsample.simicro import RealMicroscope
from phaseopt.containers import Options, ResultsContainer
from phaseopt.solver import solver_run

import itertools as it
from tifffile import imwrite
from pathlib import Path
import os

from tifffile.tifffile import imwrite

dirname = Path("/home/chanoscopio/fpm_samples/22_junio_V2")

colors = ["b", "g", "r"]
basedir = Path("/home/chanoscopio/fpm_samples/rec_eipe")
rec_name = "Reconstruction"
mag_dir = "magnitude"
phase_dir = "phase"

def get_exposure_matrix(path):
    matrix = np.zeros(shape = (32, 32))
    for f in os.listdir(path):
        if f != 'config.json' and f!= 'exposure_matrix.npy':
            pix1 = int(f[0:2])
            pix2 = int(f[3:5])
            exp = int(f[8:13])
            matrix[pix1, pix2] = exp
    return matrix

def generate_reconstruction_dirs(colors, basedir, rec_name, mag_dir, phase_dir):
    rec_dir = basedir / rec_name
    os.makedirs(rec_dir, exist_ok=True)
    for color in colors:
        os.makedirs(rec_dir / color, exist_ok=True)
        os.makedirs(rec_dir / color / mag_dir, exist_ok=True)
        os.makedirs(rec_dir / color / phase_dir, exist_ok=True)


generate_reconstruction_dirs(colors, basedir, rec_name, mag_dir, phase_dir)
exp_matrix = get_exposure_matrix(dirname)
print(str(dirname), dirname)
#np.save(exp_matrix, str(dirname)+'/exposure_matrix')
np.save(str(dirname)+'/exposure_matrix', exp_matrix)
for color in colors:
    rm = RealMicroscope.from_dirname(dirname=dirname, color=color)
    overlap = 15

    pic_hr = Picture.from_microscope(rm, overlap=overlap, outfile="ft_image.h5py")
    opts = Options(
        record_rss=True,
        record_angular_rss=True,
        xt=None,
        max_iter=7,
    )
    for patch in pic_hr.patches():
        pupil = pmath.aberrated_pupil(1e-6, rm)
        rm.y0, rm.x0 = pic_hr.get_lr_center(patch.position)
        # rm._load_samples_dask()
        delta_gk = rm.get_phaseopt_input(background_matrix=10000, color=color)
        centers = rm.centers(mode="raw")
        centers = np.array((list(centers)))
        n = 16
        delta_gk = it.islice(delta_gk, n)
        centers = centers[:n]
        res = solver_run(
            delta_gk,
            centers,
            rm.no,
            rm.patch,
            rm.nsyn,
            p0=pupil,
            microscope=rm,
            method="error_reduction",
        )
        print("done")
        filename = "{:02d}_{:02d}.tif".format(patch.position[0], patch.position[1])
        mag = np.abs(res)
        mag = np.uint16(mag * (np.iinfo(np.uint16).max / np.max(mag)))  # Rescaling
        phase = np.angle(res)
        phase = np.uint16(
            phase * (np.iinfo(np.uint16).max / np.max(phase))
        )  # Rescaling
        imwrite(
            basedir / rec_name / color / mag_dir / filename,
            data=mag,
        )
        imwrite(
            basedir / rec_name / color / phase_dir / filename,
            data=phase,
        )

        delta_gk = rm.get_phaseopt_input(background_matrix=1000)

        patch.image = np.flip(res, axis=0)

    pic_hr.store_array()
