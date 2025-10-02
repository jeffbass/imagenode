"""settings: Settings classes.

Contains Settings class and code that reads settings from librarian.yaml

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
    model_config = ConfigDict(extra="forbid")

class HubAddressList(BaseModel):
    H1: str  # at least one hub address is required 
    H2: str = ""
    H3: str = ""

class CameraOptions(BaseModel):
    viewname: Optional[str] = None
    resolution: Optional[str] = "(320, 240)"  # will use literal_eval
    framerate: Optional[int] = 10
    model_config = ConfigDict(extra="forbid")
    # and many more, including nested ones

class CameraList(BaseModel):
    P1: Optional[CameraOptions]= None
    P2: Optional[CameraOptions] = None
    W1: Optional[CameraOptions] = None
    W2: Optional[CameraOptions] = None 

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

class SensorList(BaseModel):
    T1: Optional[SensorOptions] = None
    T2: Optional[SensorOptions] = None
    S1: Optional[SensorOptions] = None
    S2: Optional[SensorOptions] = None

class Settings(BaseModel):
    """ Load settings from YAML file

        Creates Model Classes for imagenode.yaml file field parsing and
        validation. Model classes inheirit from Pydantic BaseModel class.

    """ 
    node: ImagenodeOptions
    hub_address: HubAddressList
    cameras: Optional[CameraList] = None  # the = None makes absence OK
    lights: Optional[LightOptions] = None
    sensors: Optional[SensorList] = None 
    model_config = ConfigDict(extra="forbid")

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

