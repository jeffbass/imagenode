"""check_settings: Check the Settings classes and yaml load of imagenode.yaml

Checks the Settings class and the yaml load from production directories

Run this program from imagenode/imagenode directory, which is the same directory
that imagenode.py is run from. 

Copyright (c) 2025 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import sys
import argparse
from pathlib import Path
from tools.yaml_loader import load_yaml
from tools.settings import Settings

# argparse to get imagenode_data alternative if any
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False,
	help="path to imagehub.yaml file")
args = vars(ap.parse_args())

print("args retrieved", args)

# attempt to open imagenode.yaml file
# YAML_DIR = Path(__file__).parent / "test_yaml_files"
# yaml_file = Path() 
imagenode_data_directory = "imagenode_data"
if args.path:
    subdir = Path(args.path).expanduser()
    # If user gives absolute path, use as-is; if relative, place under home
    if not subdir.is_absolute():
        subdir = Path.home() / subdir
else:
    subdir = Path.home() / imagenode_data_directory

yaml_file = subdir / "imagenode.yaml"

print("Yaml File: ", yaml_file)

sys.exit("Current Testing Endpoint")

raw_yaml = load_yaml(yaml_file)
    print("Yaml File: ", yaml_file)
    try:
        settings = Settings(**raw_yaml)
        settings.print_settings(raw_yaml=raw_yaml)
    except ValidationError as e:
        pytest.fail(f"Validation failed for {yaml_file.name}:\n{e}")

# 

print("Reached end of check_settings.py")
