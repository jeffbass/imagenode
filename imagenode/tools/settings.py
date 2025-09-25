"""settings: Settings classes.

Contains Settings class and code that reads settings from librarian.yaml

Copyright (c) 2024 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import yaml
import pprint
import logging
from pathlib import Path
from helpers.utils import YamlOptionsError

from typing import Any, Dict, List, Tuple, Optional, Literal
from pydantic import BaseModel, root_validator, validator

log = logging.getLogger(__name__)

class ImagenodeOptions(BaseModel):
    name: str
    heartbeat: int = 10
    patience: int = 10
    REP_watcher: bool = False
    stall_watcher: bool = False
    send_threading: bool = False
    queuemax: int = 50
    print_settings: bool = False
    send_type: "jpg"

class HubAddressList(BaseModel):
    H1: str  # at least one hub address is required 
    H2: str = ""
    H3: str = ""

class CameraOptions(BaseModel):
    viewname: Optional[str] = None
    resolution: Optional[Tuple[int, int]] = (320, 240)
    framerate: Optional[int] = 10
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

class YamlOptions(BaseModel):
    node: ImagenodeOptions
    hub_address: HubAdressList
    cameras: Optional[CameraList] = None  # the = None makes absence OK
    lights: Optional[LightOptions] = None
    sensors: Optional[SensorList] = None 

class Settings:
    """ Load settings from YAML file

        Creates Model Classes for librarian.yaml file field parsing and
        validation. Model classes inheirit from Pydantic BaseModel class.

        TODO: Some things are directly coded here that should become settings
        or command line arguments: 1) name of yaml file is imagenode.yaml, 2) the
        path for imagenode log and data files is ~/imagenode_data and 3) log file 
        name is imagenode.log

    """ 

    def __init__(self):
        yaml_file_name = 'imagenode.yaml'  # hardwired constant; may change later
        librarian_path = Path.home()/Path('imagenode_data') # hardwired directory too
        self.logfile = librarian_path/Path('logs')/Path('imagenode.log')
        yaml_file = librarian_path/Path(yaml_file_name)
        self.librarian_path = librarian_path
        if not Path.exists(yaml_file):
            raise YamlOptionsError('imagenode.yaml not found')
        with open(yaml_file) as f:
            self.config = yaml.safe_load(f)  # config is dict of yaml file data
        self.yaml_vals = YamlOptions.model_validate(self.config) # Pyandic parse yaml vals
        if self.yaml_vals.librarian.print_settings:
            self.print_settings('Imagenode Yaml File')

    def print_settings(self, title=None):
        # prints the settings in the yaml file
        if title:
            print(title)
        print('Contents of imagenode.yaml:')
        pprint.pprint(self.config)
        print()
