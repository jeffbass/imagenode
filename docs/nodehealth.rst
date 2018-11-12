==============================================
nodehealth: system health and failure recovery
==============================================

.. contents::

Overview
========

**nodehealth.py** contains a HealthMonitor class that continuously monitors the
operational health of the node computer and take steps to recover from failures.
It also contains functions such as ``send_heartbeat`` that allow the hub, the
librarian or other programs to externally monitor system health.

Examples of health monitoring tests that increase reliability
=============================================================

There are a number of tests that can be performed that check on the operational
status of **imagenode** and other parts of the distributed system that it is a
part of:

- Wifi strength & selection of strongest known wifi hub
- Network ping OK
- Communications with imagehub via imagezmq OK
- Before starting imagenode.py, check that no imagenode.py is already running
- Check that some processes take "normal" amount of time; sometimes ssh takes
  45 seconds to respond; indicates issues like marginal SD card
- On RPi, check integrity of SD card occasionally (how?)

**imagenode** Recovery Options
==============================

How a node needs to recover from a problem varies, depending on what type of
system the node is running on (e.g. RPi vs Mac).

Recovery options include:

- restarting the ZMQ connection context to imagezmq and the imagehub
- connecting to an alternate imagehub if the current hub is unresponsive after
  multiple attempts to restart ZMQ connection
- stopping and restarting the system wifi service
- connecting to a different wifi network
- restarting the imagenode.py program
- rebooting the node computer

The current nodehealth.py module is mostly a stub awaiting the results of
ongoing testing of different methods of implementing the above listed
recovery options.

Restarting imagenode.py after rebooting the Rpi
===============================================

There are multiple ways to start programs on the Raspberry Pi (or any other
Linux system). The 3 most common ones include 1) "cron" jobs, 2) using the
"systemd / systemctl" service system and 3) using the GNU screen program.
The systemd method is more complex, but allows more control concerning when a
program such as imagenode.py is started. We are testing all 3 as a way to
reliably restart imagenode.py after a problem recovery that requires rebooting
the RPi computer.

`Return to How imagenode works <imagenode_details.rst>`_.
or
`Return to main documentation page README.rst <../README.rst>`_.
