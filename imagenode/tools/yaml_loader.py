""" yaml_loader.py -- loads the yaml file containing imagenode settings
"""

import sys
import yaml
from pathlib import Path

def load_yaml(file_path: Path) -> dict:
    try:
        file_path_str = str(file_path)
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        print(f"Required file {file_path_str}\n{e}")
        print("Cannot continue without imagenode.yaml file.")
        sys.exit(1)
        
