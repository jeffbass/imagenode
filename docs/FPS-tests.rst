=============================
Frames Per Second (FPS) tests
=============================

.. contents::

========
Overview
========

**imagenode** is can send images in 3 different ways:
1. No threading or multi-processing: Cameras grab images & images are sent in a
   single forever loop. If the network is slow and the REP from the hub via
   imageZMQ is slow, then the next camera frame grab is delayed. No threading
   or multiprocessing is the default.
2. "send_threading" option: the read camera & detection loop places images in
   in the send_q, then grabs the next images. Images are sent from send_q in a
   separate thread. See the class SendQueue for more details. But the camera-
   detection loop and the SendQueue thread are still running on the same core.
3. "send_process" option: The read camera & detection loop places images in a
   large "SharedMemory" numpy array buffer (a new feature in Python 3.8). A
   separate process, potentially running on a different core, empties the
   numpy array buffer by sending the images via imageZMQ. Since RPi's have 4
   cores, running the camera-detection loop and the send_frames loop in
   different processes could speed things up. Sharing images between processes
   needs to use SharedMemory to avoid "pickling" images as they would be if they
   were passed in a multiprocessing.Queue.

The third "send_process" option is still in development. The first step is to
develop repeatable test programs and protocols to compare the 3 different ways
of sending images.

.. code-block:: yaml

  # Settings file imagenode.yaml -- example with lots of settings
  ---
  node:
    name: JeffOffice
    queuemax: 50
    patience: 10
    stall_watcher: False
    send_threading: False  # or True
    send_process: False  # or True
    heartbeat: 10
    send_type: jpg
    print_settings: False
  hub_address:
    H1: tcp://jeff-macbook:5555
    H2: tcp://192.168.1.155:5555


The above example has more options specified than is typical. But it does
show an actual yaml file that has been successfully used for testing
an RPi set up with a PiCamera, a USB webcam, a DS18B20 temperature sensor
and an LED light controlled by GPIO pin 18.

==================================================
Other things to think about related to FPS testing
==================================================

The **imagenode** program expects its settings to be in a file named
``imagenode.yaml`` in the home directory.

This code repository comes with an ``yaml`` folder that contains multiple examples
for many settings. It is best not to change the example yaml files so that they
can be used as reference files. Copy a suitable yaml file to "imagenode.yaml"
in the home directory. On a Raspberry Pi computer, this is typically the "pi"
username's home directory. Edit the ``imagenode.yaml`` file to specify the
address of your hub computer and set other required and optional settings.

There is also a ``test.yaml`` file in the ``yaml`` folder. When doing the suggested
tests (see installation and testing section) this yaml settings file allows
the **imagenode** program imagenode.py to run on a Raspberry Pi computer while
a simple **imagezmq** test hub program runs on the Mac or other Linux computer.
It must be copied to ``imagenode.yaml`` in the home directory when being
used for testing. Be sure to edit the ``imagenode.yaml`` file to specify the
address of your hub computer. The other settings should be OK as is for testing.


`Return to main documentation page README.rst <../README.rst>`_