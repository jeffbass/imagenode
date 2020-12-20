# Version History and Changelog

All notable changes the **imagenode** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Ongoing Development

- Improving documentation content, layout, arrangement and flow.
- Developing a "large image buffer" using the new Python 3.8 SharedMemory
  class. The idea: have the camera capture main thread put images in a very
  large (up to available memory; could be 3GB on RPi 4 models). Allow sending
  of images in a separate `multiprocessing` process that empties the buffer by
  sending images via **imageZMQ**. The advantage over the existing
  `send_threading` option would be using a 2nd process (and a different
  RPi core) rather than a 2nd thread running on the same core to send images.
- Adding the ability to capture images from stored image files as a
  substitute for capturing images from a camera. Will allow testing and tuning
  of options from real world images gathered by imagenodes scattered around the
  farm. The existing stored image library is large and could potentially be used
  for adding machine learning capability to the RPi imagenodes.

## 0.3.0 - 2020-12-19

### Improvements

- Added a `REP_watcher` yaml option which tests for REP-sent-but-no-timely-REQ
  received. This eliminated the need for `signal.SIGALRM`, which does not work
  in Python threads, such as when the `send_threading` yaml option is used. The
  new `REP_watcher` option defaults to `True`.
- Added the sending of a startup event message that is sent each time the
  imagenode is restarted.
- Added code and docs to support DHT11 & DHT22 temperature / humidity sensors
  (Thanks to @sbkirby.)
- Added yaml options, code and docs for the full range of PiCamera settings
  (Thanks to @sbkirby.)
- Added a `receive_test.py` program to enable FPS timed testing of different
  SendQueue alternatives. Made the `receive_test.py` Windows friendly by
  eliminating dependence on Linux signal SIGALRM.

### Changes and Bugfixes

- Made the detect_motion method work with both OpenCV v3.x and v4.x
  `findContours()` method. This method returns tuples of 2 or 3 values
  depending on the openCV version. The imagenode detect_motion method now works
  correctly with both OpenCV versions.

## 0.2.1 - 2020-07-10

### Improvements

- Added `send_threading` option to allow image sending to hub to happen in a
  separate thread. When this option is specified in the yaml settings file,
  camera capture and detection take place in the main thread and sending images
  via **imageZMQ** happens in a separate thread.
- Reorganized previous docs/release-history.rst into this more standardized
  HISTORY.md file.
- Updated Research and Development Roadmap.

### Changes and Bugfixes

- Fixed broken cv2.findCountours() when upgrading to OpenCV 4.x
- Multiple fixes to all documentation files.

## 0.1.0 - 2019-01-30

### Improvements

- Added `stall_watcher` option and functionality to monitor whether main
  **imagenode** process has "stalled". End program if stall detected. Uses
  systemd service unit to restart after exit. Added the `imagenode.service`
  example systemd service unit file to main repository directory.
- Added Release and Version History.
- Added Research and Development Roadmap.

### Changes and Bugfixes

- Multiple fixes to all documentation files.

## 0.0.2 - 2018-12-15

### Improvements

- Added `exposure_mode` option to allow choosing PiCamera exposure_mode.
  Very helpful with Infrared PiCamera "Noir" and infrared lights.

### Changes and Bugfixes

- Conditionally import GPIO only if needed. Fixes import error when GPIO pins
  not used, or when running NOT on a Raspberry Pi.
- Fixed a number of documentation broken links and formatting errors.
- Multiple fixes to all documentation files.
- Restructured test files & testing documentation to make them consistent.

## 0.0.1 - 2018-11-15

- First commit to GitHub
- Major refactoring after 13 months of testing previous version.
- Includes motion detector, light detector, temperature sensor, LED light
  control via GPIO pins.

## 0.0.0 - 2017-10-09

- First early prototype of `imagenode` running on 2 RPi's with 1 imagehub.

[Return to main documentation page README](README.rst)
