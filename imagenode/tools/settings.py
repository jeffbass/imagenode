"""settings: Settings classes.

Contains Settings class and code that reads settings from imagenode.yaml

Copyright (c) 2025 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""


import yaml
import pprint
import logging
from pathlib import Path

from typing import Any, Dict, List, Tuple, Optional, Literal
from pydantic import BaseModel, ConfigDict, root_validator, validator

log = logging.getLogger(__name__)

class YamlOptionsError(Exception):
    pass

class ImagenodeOptions(BaseModel):
    name: str
    heartbeat: int = 10
    patience: int = 10
    REP_watcher: bool = False
    stall_watcher: bool = False
    send_threading: bool = False
    queuemax: int = 50
    print_settings: bool = False
    send_type: str = "jpg"
    # model_config = ConfigDict(extra="forbid")

class HubAddressList(BaseModel):
    H1: str  # at least one hub address is required 
    H2: str = ""
    H3: str = ""

class DetectorOptions(BaseModel):
    ROI: str = ""              # (70,2),(100,25) OpenCV format
    draw_ROI: str = ""         # ((255,0,0),5) OpenCV format
    roi_name: str = ""         # optional ROI name
    log_roi_name: bool = False # add ROI to event detected message?
    draw_time: str = ""      # ((255,0,0),1) timestamp text blue with 1 pixel line width
    draw_time_org: str = ""  # (1,1)  # the timestamp text starts at pixel (1,1)
    draw_time_fontScale: int = 1   # the timestamp fontScale factor is 1
    threshold: int = 25 
    percent: int = 70
    min_frames: int = 5
    send_frames: Literal["continuous", "event", "none"] = "event"
    send_count: int = 10
    send_test_images: bool = False 
    delta_threshold: int = 5
    min_motion_frames: int = 4
    min_still_frames: int = 4 
    min_area: int = 3 
    blur_kernal_size: int = 21 

class CameraOptions(BaseModel):
    viewname: Optional[str] = None
    size: Optional[str] = "(320, 240)"  # will use literal_eval
    framerate: Optional[int] = 10
    src: Optional[int] = 0
    detectors: Optional[Dict[Literal["motion","light"], DetectorOptions]] = None
    auto_exposure: bool = True
    framerate: Optional[int] = None
    vflip: bool = False

    # Optional manual exposure/gain and other controls (use None if not provided)
    exposure_time: Optional[int] = None  # microseconds
    analog_gain: Optional[float] = None
    brightness: Optional[int] = None
    contrast: Optional[int] = None
    saturation: Optional[int] = None
    sharpness: Optional[int] = None
    awb_mode: Optional[str] = None
    # Allow additional controls to be passed through
    extra_controls: Optional[Dict[str, Any]] = None
    # model_config = ConfigDict(extra="forbid")
    # and many more, including nested ones

class LightOptions(BaseModel):
    name: str = "light"
    gpio: int
    on: Literal["continuous", "timed"]

class SensorOptions(BaseModel):
    name: str
    type: Literal["DS18B20", "DHT11", "DHT22"]
    gpio: int  # the DS18B20 can only be used on GPIO pin 4
    read_interval_minutes: int = 10  # check temperature every X minutes
    min_difference: int = 1  # send reading when changed by X degrees

class Settings(BaseModel):
    """ Load settings from YAML file

        Creates Model Classes for imagenode.yaml file field parsing and
        validation. Model classes inheirit from Pydantic BaseModel class.

    """ 
    node: ImagenodeOptions
    hub_address: HubAddressList
    cameras: Optional[Dict[str, CameraOptions]] = None  # the = None makes absence OK
    lights: Optional[LightOptions] = None
    sensors: Optional[Dict[str,SensorOptions]] = None 
    # model_config = ConfigDict(extra="forbid")

    def print_settings(self, title=None, raw_yaml=None):
        # prints the settings in the yaml file
        # argument raw_yaml is the raw dictionary of yaml file before validation.
        # if the raw_yaml argument is present, the raw_yaml file will be pprinted 
        # and a comparison to the validated settings (post Pydantic validation)
        # will print settings in the yaml file that aren't in the validated settings.
        # This will catch some, but not all typos of settings names
        if title:
            print(title)
        print('\nValidated contents of imagenode.yaml:')
        pprint.pprint(self.model_dump())
        print()
        if raw_yaml:
            n_unknowns = 0
            # compare expected validated fields to raw_yaml fields in various sections
            # The root first level settings of the YAML
            defined = set(self.model_dump().keys())
            unknown = set(raw_yaml.keys()) - defined
            if unknown:
                n_unknowns += 1
                print("Unknown YAML options:", unknown)
            # The settings in the node section
            defined = set(self.model_dump()["node"].keys())
            unknown = set(raw_yaml["node"].keys()) - defined
            if unknown:
                n_unknowns += 1
                print("Unknown node options:", unknown)
            # The settings for each camera (there may be multiple cameras)
            cams = self.model_dump()["cameras"]
            # print("Model Dump of cameras")
            # pprint.pprint(cams)
            for cam in cams:
                # print("One cam")
                # pprint.pprint(cam)
                defined = set(cams[cam].keys())
                # print("set of cam keys")
                # pprint.pprint(defined)
                unknown = set(raw_yaml["cameras"][cam].keys()) - defined
                if unknown:
                    n_unknowns += 1
                    print("Camera ", cam, "Unknown camera options:", unknown)
            if n_unknowns:
                print(f"\nUnknown YAML options were found in {n_unknowns} sections.")
                print("Dump of raw imagenode.yaml file as an unordered dictionary")
                print("Compare to Validated Settings above")
                print()
                pprint.pprint(raw_yaml)




