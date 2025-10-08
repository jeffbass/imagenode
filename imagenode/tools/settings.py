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
    ROI: str = ""            # (70,2),(100,25)
    draw_ROI: str = ""       # ((255,0,0),5) 
    draw_time: str = ""      # ((255,0,0),1)  # the timestamp text is blue with 1 pixel line width
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
    detectors: Optional[Dict[str, DetectorOptions]] = None
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
        if title:
            print(title)
        print('Validated contents of imagenode.yaml:')
        pprint.pprint(self.model_dump())
        print()
        if raw_yaml:
            # compare expected validated fields to raw_yaml fields
            defined = set(self.model_dump().keys())
            unknown = set(raw_yaml.keys()) - defined
            if unknown:
                print("Unknown YAML options:", unknown)

