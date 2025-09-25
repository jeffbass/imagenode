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

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, root_validator, validator

log = logging.getLogger(__name__)

class LibrarianOptions(BaseModel):
    name: str
    patience: int = 10
    heartbeat: int = 10
    print_settings: bool = False
    stall_watcher: bool = False
    send_threading: bool = False

class CommChannelOptions(BaseModel):
    port: int = 5555
    protocol: str = 'zmq'

class CommChannels(BaseModel):
    CLI: CommChannelOptions

class Contacts(BaseModel):
    folder: str = 'contacts'
    file: str = 'contacts.txt'

class ImageHubData(BaseModel):
    computer: str  = 'localhost' # computer is 'localhost' or e.g. mac-2011
    directory: str = 'imagehub_data' # relative to Path.home()
    max_recent_events: int = 300  # keep how many "most recent" events?

class YamlOptions(BaseModel):
    librarian: LibrarianOptions
    comm_channels: Optional[CommChannels] = None  # the = None makes absence OK
    contacts: Optional[Contacts] = None 
    imagehub_data: Optional[ImageHubData] = None

class Settings:
    """ Load settings from YAML file

        Creates Model Classes for librarian.yaml file field parsing and
        validation. Model classes inheirit from Pydantic BaseModel class.

        TODO: Some things are directly coded here that should become settings
        or command line arguments: 1) name of yaml file is librarian.yaml, 2) the
        path for librarian log and data files is ~/librarian and 3) log file 
        name is librarian.log

    """ 

    def __init__(self):
        yaml_file_name = 'librarian.yaml'  # hardwired constant; may change later
        librarian_path = Path.home()/Path('librarian_data') # hardwired directory too
        self.logfile = librarian_path/Path('logs')/Path('librarian.log')
        yaml_file = librarian_path/Path(yaml_file_name)
        self.librarian_path = librarian_path
        if not Path.exists(yaml_file):
            raise YamlOptionsError('librarian.yaml not found')
        with open(yaml_file) as f:
            self.config = yaml.safe_load(f)  # config is dict of yaml file data
        self.yaml_vals = YamlOptions.model_validate(self.config) # Pyandic parse yaml vals
        if self.yaml_vals.librarian.print_settings:
            self.print_settings('Librarian Yaml File')

    def print_settings(self, title=None):
        # prints the settings in the yaml file
        if title:
            print(title)
        print('Contents of librarian.yaml:')
        pprint.pprint(self.config)
        print()