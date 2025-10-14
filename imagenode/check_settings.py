"""check_settings: Check the Settings classes and yaml load of imagenode.yaml

Checks the Settings class and the yaml load from production directories

Run this program from imagenode/imagenode directory, which is the same directory
that imagenode.py is run from. 

Copyright (c) 2025 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import sys
import pprint
import argparse
from pathlib import Path
from pydantic import ValidationError
from tools.utils import print_attrs
from tools.yaml_loader import load_yaml
from tools.settings import Settings, DetectorOptions

# argparse to get imagenode_data alternative if any
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False,
	help="path to imagenode.yaml file")
args, _ = ap.parse_known_args()

print("args retrieved", args.path)

# attempt to open imagenode.yaml file
imagenode_data_directory = "imagenode_data"
if args.path:
    subdir = Path(args.path).expanduser()
    # If user gives absolute path, use as-is; if relative, place under home
    if not subdir.is_absolute():
        subdir = Path.home() / subdir
else:
    subdir = Path.home() / imagenode_data_directory

yaml_file = subdir / "imagenode.yaml"

raw_yaml = load_yaml(yaml_file)
print("Yaml File: ", yaml_file)

# sys.exit("Current Testing Endpoint")

try:
    settings = Settings(**raw_yaml)
    print("settings.model_fields", settings.model_fields.keys())
    print("settings.cameras.keys", settings.cameras.keys())
    for cam in settings.cameras:
        print("Camera", cam)
        print("Camera size", settings.cameras[cam].size)
        print("Camera framerate", settings.cameras[cam].framerate)
        detectors = settings.cameras[cam].detectors
        if isinstance(detectors, list):
            for lst in detectors:    # List of Detectors if 2 motion detectors, for example
                for detector in lst:
                    print("   in detector list, detector", detector)
                    det_opts = DetectorOptions(**lst[detector]) # Pydantic checking class
                    print("    in detector", detector, "type is", type(det_opts))
                    print("    in detector, option ROI: ", det_opts.ROI)
                    # in full imagenode cameras setup, it looks like
                    # det = Detector(detector, lst, nodename, viewname)  # create a Detector instance
                    # self.detectors.append(det)  # add to list of detectors for this camera
        else:
            for detector in detectors:  # for each camera listed in yaml file
                det_opts = detectors[detector]
                print("    in detector", detector, "type is", type(det_opts))
                print("    in detector, option ROI: ", det_opts.ROI)
                # in full imagenode cameras setup, it looks like
                # det = Detector(detector, detectors, nodename, viewname)  # create a Detector instance
                # self.detectors.append(det)  # add to list of detectors for this camera


    settings.print_settings(raw_yaml=raw_yaml)

    # Print out the entire validated settings object
    # Can be quite long for a large yaml file
    print("The Validated Settings object contents:")
    print_attrs(settings)


except ValidationError as e:
    print(f"Validation failed for imagenode.yaml:\n{e}")

# 

print("Reached end of check_settings.py")
