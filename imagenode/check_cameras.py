"""check_cameras: Set up cameras and show captured images

Checks simple code that sets up and reads images from the cameras.
For all the cameras in the yaml file, reads and diplays images.
Uses Settings class & loads the yaml file options from production directories.
Uses a simplified camera setup and simplified detector setup.
Shows images for each camera on the screen in a separate cv2.imshow() window

Run this program from imagenode/imagenode directory, which is the same directory
that imagenode.py is run from.

Copyright (c) 2025 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import sys
import cv2
import time
import pprint
import argparse
import tools.cameras
from pathlib import Path
from pydantic import ValidationError
from tools.utils import print_attrs
from tools.yaml_loader import load_yaml
from tools.settings import Settings, DetectorOptions
from tools.cameras import PiCamera2Camera, WebCamera

# argparse to get imagenode_data alternative if any
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, help="path to imagenode.yaml file")
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

    # first, setup all the cameras in the yaml settings file
    camlist = []  # list to hold all the cameras
    for cam in settings.cameras:  # setup camera from yaml file settings
        print("Camera", cam)
        print("Camera Options Object Type", type(settings.cameras[cam]))
        print("Camera size", settings.cameras[cam].size)
        print("Camera framerate", settings.cameras[cam].framerate)
        detectors = settings.cameras[cam].detectors  # setup detectors
        if isinstance(detectors, list):
            for (
                lst
            ) in detectors:  # List of Detectors if 2 motion detectors, for example
                for detector in lst:
                    print("   in detector list, detector", detector)
                    det_opts = DetectorOptions(
                        **lst[detector]
                    )  # Pydantic detector class
                    print("    in detector", detector, "type is", type(det_opts))
                    print("    in detector, option ROI: ", det_opts.ROI)
                    # in full imagenode cameras setup, it looks like
                    # det = Detector(detector, lst, nodename, viewname)  # create a Detector instance
                    # self.detectors.append(det)  # add to list of detectors for this camera
        else:
            for (
                detector
            ) in detectors:  # all detectors for each camera listed in yaml file
                det_opts = detectors[detector]
                print("    in detector", detector, "type is", type(det_opts))
                print("    in detector, option ROI: ", det_opts.ROI)
                # in full imagenode cameras setup, it looks like
                # det = Detector(detector, detectors, nodename, viewname)  # create a Detector instance
                # self.detectors.append(det)  # add to list of detectors for this camera
        if cam[0].lower() == "p":  # this is a Picamera
            camera = PiCamera2Camera(cam, settings.cameras[cam])
        else:  # not a Picamera, so assume an OpenCV Webcamera
            camera = WebCamera(cam, settings.cameras[cam])
        camlist.append(camera)  # add it to the list of cameras

    # Read images from the cameras in the camlist and display them to screen
    for cam in camlist:  # first start the cameras
        cam.start()
    try:
        while True:
            for cam in camlist:
                frame = cam.read()
                cv2.imshow(cam.name_viewname, frame)  # 1 window for each RPi
                cv2.waitKey(10)
                time.sleep(0.01)

    except (KeyboardInterrupt, SystemExit):
        print("Ctrl-C was pressed.")
    except Exception as ex:  # traceback will appear in log
        print(f"Exception occurred:\n  {ex}")
    finally:
        for cam in camlist:
            cam.close()

    settings.print_settings(raw_yaml=raw_yaml)

    # Print out the entire validated settings object
    # Can be quite long for a large yaml file
    print("The Validated Settings object contents:")
    print_attrs(settings)


except ValidationError as e:
    print(f"Validation failed for imagenode.yaml:\n{e}")

#

print("Reached end of check_cameras.py")
