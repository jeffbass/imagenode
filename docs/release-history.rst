=====================================
imagenode Release and Version History
=====================================

.. contents::

Overview
========

**imagenode** is constantly evolving. Release and Version History is tracked
here, with the most recent changes at the top.

0.1.0 (2019-01-30)
------------------
- Added Release and Version History.
- Added Research and Development Roadmap.
- Added ``stall_watcher`` option and functionality to monitor whether main
  **imagenode** process has "stalled". End program if stall detected. Uses
  systemd service unit to restart after exit. Added the ``imagenode.service``
  example systemd service unit file to main repository directory.

0.0.2 (2018-12-15)
------------------
- Added ``exposure_mode`` option to allow choosing PiCamera exposure_mode.
  Very helpful with Infrared PiCamera "Noir" and infrared lights.
- Bug Fixes:

  - Conditionally import GPIO only if needed. Fixes import error when GPIO pins
    not used.
  - Fixed a number of documentation broken links and formatting errors.

0.0.1 (2018-11-15)
------------------
- First commit; major refactor after 18 months of testing previous version.
- Includes motion detector, light detector, temperature sensor, LED light
  control via GPIO pins.

`Return to main documentation page README.rst <../README.rst>`_
