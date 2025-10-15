# cameras.py -- define cameras including picamera2 and openCV WebCamera
"""
Picamera2 is the only Raspberry Pi camera that is supported here.
Webcamera is for any USB or Laptop camera that is accessed using OpenCV.

"""

import time
from typing import Dict, Tuple, Optional, Any
from abc import ABC, abstractmethod
from ast import literal_eval

import yaml
import numpy as np
import cv2
from pydantic import BaseModel, validator
from tools.settings import CameraOptions


class PiCamera2Camera:
    """Methods and attributes of a Picamera2 Camera

    Parameters:
        camera (str): dict key of current camera being instantiated
        cfg (CameraOptions): CameraOptions class validated from YAML file
        (later if needed?) settings (Settings object): settings object validated from YAML file
    """

    def __init__(self, name: str, cfg: CameraOptions):
        try:
            from picamera2 import Picamera2, Preview
        except ImportError:
            Picamera2 = None
        if Picamera2 is None:
            raise RuntimeError("Picamera2 not available on this system.")
        self.picam2 = Picamera2()
        # Convert size from string like "(640,480)" to Tuple(640,480)
        self.size_tuple = literal_eval(cfg.size)  # perhaps put this in try...except later

        # create_preview_configuration with RGB888 is reliable for continuous capture
        # (specifically NOT using create_still_configuration as it fails and hangs
        #     when used for continuous capture of images from Picamera)
        video_config = self.picam2.create_preview_configuration(
            {"size": self.size_tuple, "format": "RGB888"}
        )
        self.picam2.configure(video_config)

        self.controls = {}
        if cfg.brightness is not None:
            self.controls["Brightness"] = int(cfg.brightness)
        if cfg.contrast is not None:
            self.controls["Contrast"] = int(cfg.contrast)
        if cfg.saturation is not None:
            self.controls["Saturation"] = int(cfg.saturation)
        if cfg.sharpness is not None:
            self.controls["Sharpness"] = int(cfg.sharpness)
        if cfg.awb_mode is not None:
            self.controls["AwbMode"] = cfg.awb_mode
        # convert from framerate in frames-per-second to FrameDuration
        if cfg.framerate:
            frame_us = int(1_000_000 / float(cfg.framerate))
            self.controls["FrameDurationLimits"] = (frame_us, frame_us)
        if not cfg.auto_exposure:
            if cfg.exposure_time is not None:
                self.controls["ExposureTime"] = int(cfg.exposure_time)
            if cfg.analog_gain is not None:
                self.controls["AnalogueGain"] = float(cfg.analog_gain)
        if cfg.extra_controls:
            self.controls.update(cfg.extra_controls)
        self.vflip = bool(cfg.vflip)
        self.name = name
        self.viewname = cfg.viewname
        if self.viewname:
            self.name_viewname = self.name + " " + self.viewname
        else:
            self.name_viewname = self.viewname

    def start(self):
        if self.running:
            return
        self.picam2.start()
        if self.controls:
            self.picam2.set_controls(self.controls)
        self.running = True

    def read(self, append_to_queue: bool = True):
        if not self.running:
            raise RuntimeError(f"{self.name} not started")
        rgb = self.picam2.capture_array()
        if self.vflip:
            rgb = np.flipud(rgb)
        bgr_frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        return bgr_frame  # camera frame in OpenCV BGR format

    def close(self):
        if self.running:
            self.picam2.stop()
            self.picam2.close()
            self.running = False


class WebCamera:
    """Methods and attributes of a OpenCV Web Camera (USB camera or Laptop camera)

    Parameters:
        camera (str): dict key of current camera being instantiated
        cfg (CameraOptions): CameraOptions class validated from YAML file
        (later if needed?) settings (Settings object): settings object validated from YAML file
    """

    def __init__(self, name: str, cfg: CameraOptions):
        self.cap = None
        # Convert size from string like "(640,480)" to Tuple(640,480)
        self.size_tuple = literal_eval(
            cfg.size
        )  # perhaps put this in try...except later
        self.name = name
        self.src = cfg.src
        self.framerate = cfg.framerate
        self.vflip = cfg.vflip
        self.viewname = cfg.viewname
        if self.viewname:
            self.name_viewname = self.name + " " + self.viewname
        else:
            self.name_viewname = self.name

    def start(self):
        self.cap = cv2.VideoCapture(self.src)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open USB camera {self.name}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.size_tuple[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.size_tuple[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.framerate)

    def read(self):
        if self.cap is None:
            raise RuntimeError("Camera not started")

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        if self.vflip:
            frame = cv2.flip(frame, 0)
        return frame

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
