""" yaml_loader.py -- loads the yaml file containing settings
"""

import yaml
from pathlib import Path

def load_yaml(file_path: Path) -> dict:
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
        
