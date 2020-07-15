=================================================================
Testing **imagenode** with various cameras, detectors and sensors
=================================================================

.. contents::

Overview
========

**imagenode** is a part of a distributed computer vision system that runs
on multiple computers. The minimal system is one Raspberry Pi running
**imagenode** and one larger computer (such as a Mac) running **imagehub**.
You can see the overall design of such a system in the yin-yang-ranch
Github repository  `Yin Yang Ranch project <https://github.com/jeffbass/yin-yang-ranch>`_.
**imagenode** is dependent on having working copies of **imageZMQ** on both the
RPi computer and the display computer. Be sure to set up and test **imageZMQ**
BEFORE you try to install and test **imagenode**. The instructions for
installing and testing **imageZMQ** are in the
`imageZMQ GitHub repository <https://github.com/jeffbass/imagezmq.git>`_

Once you have run all the **imageZMQ** test programs, the next step is to
to test **imagenode** by running it on a Mac or other computer with a webcam.
In all of the tests below, **imagenode** will be tested using the
``receive_test.py`` program running on a Mac (or
other display computer). The ``receive_test.py`` program running on
the Mac acts as a test hub. Testing this way tests both **imagenode** and
**imageZMQ** together without the need for using a full image hub at the same
time. It is best to do substantial testing with this combination before adding
**imagehub** to the mix.

Directory Structure for the Tests
=================================
Both **imagenode** and **imageZMQ** should be git-cloned to any computer
that they will be running on. **imageZMQ** is pip installable. See the link
above to **imageZMQ** documentation for details. I have done all testing at the
user home directory of every computer the programs are used on::

  ~  # user home directory
  +--- imagenode.yaml  # copied from test1.yaml file & edited as needed
  |
  +--- imagenode    # the git-cloned directory for imagenode
  |    +--- docs
  |    +--- imagenode
  |    |    +--- imagenode.py
  |    +--- tests
  |    |    +--- test1.yaml
  |    |    +--- test2.yaml
  |    |    +--- test3.yaml
  |    +--- yaml
  |         +--- picam-light-test.yaml
  |         +--- picam-motion-test.yaml
  |         +--- picam-sensor-test.yaml
  |         +--- webcam-light-test.yaml
  |
  +--- imagezmq   # the git-cloned directory for imageZMQ
       +--- docs
       +--- imagezmq
       |    +--- imagezmq.py  # contains the imagezmq classes
       +--- tests


Test 1: Running **imagenode** and a test hub with both running on a Mac
=======================================================================
**The first test** runs both the sending program **imagenode** and the receiving
``receive_test.py`` program (acting as a test hub) on
a Mac (or linux computer) with a webcam. It tests that the imagenode software
is installed correctly and that ``imagenode.yaml`` file has been copied and edited
in a way that works. It uses the webcam on the Mac for testing. The Mac will be
displaying the images received from its webcam as well as various Light Detector
specific testing windows. It tests the Light Detector which detects "lighted"
versus "dark" states in a specified ROI.

1. Make sure **imageZMQ** is installed and tested on your Mac or other
   display computer. The link to the **imageZMQ** GitHub repository is above.
2. Clone the **imagenode** GitHub repository onto your mac in your home
   directory::

     git clone https://github.com/jeffbass/imagenode.git

3. Open 2 terminal windows on your Mac. One will be used for running
   **imagenode** and the other will be used for running ``receive_test.py``.
4. In one terminal window, copy ``imagenode/tests/test1.yaml`` to ``imagenode.yaml``
   in the home directory (~) using the command below. This test1.yaml file
   contains settings that will send a continuous stream of images from the webcam
   on the Mac while detecting "lighted" and "dark" states. You will not need to
   edit the yaml file. The name of the file in the home directory must be
   ``imagenode.yaml`` for these tests::

     cp  ~/imagenode/tests/test1.yaml  ~/imagenode.yaml

   You may want to open the ``imagenode.yaml`` file in your text editor as you
   do the rest of the testing below. You may want to change some of the options
   between test runs of ``imagenode.py`` to see how they affect detection of
   the "lighted" and "dark" states. This test uses the Light Detector, and
   you can see how the Light Detector is specified in the imaganode.yaml file
   (which is the file that you just copied from the ``test1.yaml`` file in the
   ``imagenode/tests`` directory).

5. In the same terminal window, change to the ``~/imagenode/imagenode`` directory.
   You will be running imagenode.py from here in a few more steps::

     cd ~/imagenode/imagenode

6. In the other terminal window, change to the ``tests`` directory in the
   **imagenode** repository: ~/imagenode/tests::

     cd ~/imagenode/tests

7. In this same terminal window, run the program ``receive_test.py``
   and leave it running::

     workon py3cv3  # my virtualenv name; use yours instead
     python receive_test.py

8. In the first terminal window (in directory ~/imagenode/imagenode), run the
   ``imagenode.py`` program::

     workon py3cv3  # my virtualenv name; use yours instead
     python imagenode.py

In about 1 minute, you should see a steam of images from the Mac's webcam appear
in OpenCV display windows on the Mac. There are actually several windows
stacked on top of each other. Drag them to separate areas of the screen. These
windows are::

  WebCamTest: the main image window showing whatever the webcam is aimed at
    (presumably yourself). The ROI for detection will be outlined in a blue
    rectangle in the upper right of the windo.
  ROI: a smaller window showing the area specified in the imagenode.yaml file
    for detecting light. It appears in its own window in natural color.
  Grayscale: a smaller window showing the same area shown by the ROI window,
    but showing in Grayscale.
  Mean Pixel Value: a smaller window showing the average pixel intensity value
    from 0 to 255 computed from all the pixels in the Grayscale ROI.
  State: a smaller window showing the current state calculated by the Light
    Detector. The text inthe window will say "lighted" or "dark" depending on
    the light intensity of the ROI area.

There will also be 1 or 2 other "mini windows", which are really just the name
bars for the windows. The purpose of these "window name bars" is to show what
event messages the **imagehub** would have recorded to the **imagehub** event
log. If you have 2 windows (because you have changed the brightness of the ROI
area), one window bar will say "WebCamTest |light | lighted" and the other
window bar will show "WebCamTest |light | dark".

If you move a darker object into the camera view of the ROI area, you will see
the Mean Pixel Value change and, depending on how light or dark the object is,
the State will change from "Lighted" to "Dark".

You can change the option values of the light detector to run experiments with
the Light Detector.

1. Stop the imagenode.py program running in the imagenode terminal window by
   pressing Ctrl-C. Edit the ``~/imagenode.yaml`` file to change the threshold
   value to a different value.
2. Rerun the imagenode.py program and watch what happens.

You can leave the test hub program ``receive_test.py`` program
running while you stop the ``imagenode.py`` program, change the yaml file,
and restart the ``imagenode.py`` program.

You can experiment with other option setting values as well. You can read about
the option settings and get an explanation of the file and adjusting the settings
in `imagenode Settings and the YAML files <settings-yaml.rst>`_.

All of these windows are used for testing. In a production use of **imagenode**,
and **imagehub**, the event messages and the event related images would be
stored in appropriate directories on the **imagehub** computer. The windows
would not be shown on the hub computer because the send_test_images option
would be set to False in the imagenode.yaml file.

Press Ctrl-C in each window to end both the test programs.

Test 2: Testing **imagenode** running on a RPi with a test hub running on a Mac
===============================================================================

**The second test** runs the sending program **imagenode** on an RPi with a
PiCamera and the program ``receive_test.py`` (acting as
a test hub) on a Mac (or linux computer). The Mac will be displaying the images
received from the RPi PiCamera as well as various detector specific testing
windows. It tests that the imagenode software is installed correctly on the RPi
and that the ``imagenode.yaml`` file has been copied and edited in a way that
works.  It tests the Light Detector which detects "lighted" versus "dark" states
in a specified ROI in the field of view of the PiCamera.

1. Make sure **imageZMQ** is installed and tested on your Mac or other
   display computer. The link to the **imageZMQ** GitHub repository is above.
2. Make sure **imageZMQ** is installed and tested on your RPi that has a
   PiCamera that will be sending images to test the Light Detector. The link to
   the **imageZMQ** GitHub repository is above.
3. Clone the **imagenode** GitHub repository onto your RPi in the home
   directory (typically the "pi" user home directory)::

     git clone https://github.com/jeffbass/imagenode.git

   Your directory structure on your RPi should be like the directory structure
   described above.
4. Open 2 terminal windows on your Mac. One will be used for running
   **imagenode** on RPi and the other will be used for running
   ``receive_test.py`` as a test hub on the Mac.
5. In one terminal window, ssh into the RPi. Copy ``imagenode/tests/test2.yaml``
   to ``imagenode.yaml`` in the home directory (~) using the command below.
   This ``test2.yaml`` file contains settings that will send a continuous stream of
   images from the PiCamera to the Mac while detecting "lighted" and "dark"
   states. The name of the file in the home directory must be ``imagenode.yaml``
   for these tests::

     cp  ~/imagenode/tests/test2.yaml  ~/imagenode.yaml

   Open a text editor in your RPi terminal window. Edit the ``~/imagenode.yaml``
   file to change the H1 hub address to point to the TCP address of you Mac
   that will be acting as a hub.

   While you are editing the H1 hub address in the ``imagenode.yaml`` file, you
   may want set the vflip option to True. I find that in over half of my RPi
   PiCamera setups, the camera is positioned upside down; it has to do with the
   way the PiCamera cable connects to the main board. Setting the vflip option to
   True will cause the image to be vertically flipped.

   You may want to open the ``imagenode.yaml`` file in your RPi text editor as you
   do the rest of the testing below. You may want to change some of the options
   between test runs of ``imagenode.py`` and see how they affect detection of
   the "lighted" and "dark" states. This test uses the Light Detector, and
   you can see how the Light Detector is specified in the imaganode.yaml file
   (that is the file that you just copied from the ``test2.yaml`` file in the
   ``imagenode/tests`` directory).

6. In the same RPi terminal window, change to the ``~/imagenode/imagenode``
   directory. You will be running imagenode.py from here in a few more steps::

     cd ~/imagenode/imagenode

7. In the other terminal window, which is going to be used to run the test hub
   on the Mac, change to the ``tests`` directory in the **imagenode** repository::

     cd ~/imagenode/tests

8. In this same Mac terminal window (in the ``~/imagenode/tests`` directory),
   run the program ``receive_test.py`` and leave it running::

     workon py3cv3  # my virtualenv name; use yours instead
     python receive_test.py

9. In the RPi terminal window (in directory ~/imagenode/imagenode), run the
   ``imagenode.py`` program::

     workon py3cv3  # my virtualenv name; use yours instead
     python imagenode.py

In about 1 minute, you should see a steam of images from the Mac's webcam appear
in OpenCV display windows on the Mac. There are actually several windows
stacked on top of each other. Drag them to separate areas of the screen. These
windows are the same as the windows described above, except that the name of
the main image window will be "PiCameraTest".

There will also be 1 or 2 other "mini windows", which are really just the name
bars for the windows. The purpose of these "window name bars" is to show what
event messages the **imagehub** would have recorded to the **imagehub** event
log. If you have 2 windows (because you have changed the brightness of the ROI
area), one window bar will say "WebCamTest |light | lighted" and the other
window bar will show "WebCamTest |light | dark".

If you move a darker object into the camera view of the ROI area, you will see
the Mean Pixel Value change and, depending on how dark the object is, the State
will change from "Lighted" to "Dark".

You can change the option values of the light detector to run experiments with
the Light Detector.

1. Stop the imagenode.py program running in the RPi imagenode terminal window by
   pressing Ctrl-C. Edit the ``~/imagenode.yaml`` file to change the threshold value
   to a different value.
2. Rerun the ``imagenode.py`` program and watch what happens.

You can experiment with other option setting values as well. You can read about
the option settings with an explanation of the file and adjusting the settings
in `imagenode Settings and the YAML files <settings-yaml.rst>`_.

All of these windows are used for testing. In a production use of **imagenode**,
and **imagehub**, the event messages and the event related images would be
stored in appropriate directories on the **imagehub** computer. The windows
would not be shown on the hub computer because the ``send_test_images`` option
would be set to False in the ``imagenode.yaml`` file.

Press Ctrl-C to end the test programs on both the Mac and the RPi.

Test 3: Testing **imagenode** running a motion detector on the RPi to Mac Hub
=============================================================================

**The third test** runs the sending program **imagenode** on an RPi with a
PiCamera and the ``receive_test.py`` (acting as
a test hub) on a Mac (or linux computer). It is run exactly the same way as
Test 2, above. The Mac will be displaying the images received from the RPi
PiCamera as well as several motion detector specific testing windows. Test 3
tests the Motion Detector which detects "moving" versus "still" states in a
specified ROI in the field of view of the PiCamera.

To run the motion detector test with the RPi PiCamera sending images and events
to the Mac running the test hub, follow all the steps in Test 2, with one
change. In step 5, copy ``imagenode/tests/test3.yaml`` to ``imagenode.yaml`` in
the home directory (~) using the command below. This ``test3.yaml`` file
contains settings that will send a continuous stream of images from the PiCamera
to the Mac while detecting "moving" and "still" states. The name of the file in
the home directory must be ``imagenode.yaml`` for these tests::

  cp  ~/imagenode/tests/test3.yaml  ~/imagenode.yaml

After copying the yaml file, edit the file to have it point to your Mac's hub
address. Also, change the vflip option if you need to. Run the rest of the steps
the same way as Test 2, above. A different set of Motion Detector windows will
appear on the Mac display::

  PiCameraTest: the main image window showing whatever the PiCamera is aimed at.
    The ROI for motion detection will be outlined in a blue rectangle in the
    upper right of the window.
  ROI: a smaller window showing the area specified in the imagenode.yaml file
    for detecting motion. It appears in its own window in natural color.
  Grayscale: a smaller window showing the same area shown by the ROI window,
    but showing in Grayscale.
  frameDelta: a smaller window showing the same area shown by the ROI window,
    but showing the frameDelta difference, pixel by pixel between the most
    recent image and the average of previous images.
  thresholded: a smaller window showing the same area shown by the ROI window,
    but showing the motion areas thresholded so they are all white versus the
    non motion areas being all black.
  Area: a smaller window showing the computed area of the contours around pixels
    thresholded as moving.
  N Contours: The number of contours in the ROI around thresholded pixels.
  State: a smaller window showing the current state calculated by the Light
    Detector. The text in the window will say "moving" or "still" depending on
    the light intensity of the ROI area.

If you wave a hand or an object in the ROI of the PiCamera, you will see it
in the various windows and see the thresholded contours in the threshold window.
You will also see the values of the calculations and the final state of "moving"
or "still". It would be helpful to experiment with different values for the
options in the ``~/imagenode.yaml`` file and see what impact it has on the
various motion detection windows.

Press Ctrl-C to end the test programs on both the Mac and the RPi.

Test 4: Testing **imagenode** temperature sensor on the RPi to Mac Hub
======================================================================

**The fourth test** tests the capability of **imagenode** to capture and send
temperature sensor readings. It also uses the Mac running the program
``receive_test.py`` as a test hub as in the previous tests. To run
this test you will need a DS18B20 temperature sensor appropriately attached
to GPIO pin 4 of the RPi.

Set things up as in Test 2. Then, in the RPi terminal window, copy
``test3.yaml``::

  cp  ~/imagenode/tests/test3.yaml  ~/imagenode.yaml

After copying the yaml file, run the hub and RPi programs the same way as in
Test 2, above. A small window that is only a window title bar will appear on the
Mac display::

  RPi |Temp | 72 F

The ``test4.yaml`` settings file causes the temperature sensor thread to start
and report temperature values once per minute. It will report the temperature
once per minute even if the temperature doesn't change because the
``min_difference`` is set to 0. If the ``min_difference`` had ben set to ``1``,
for example, the temperatures would be reported only if they changed by at
least 1 degree. Press Ctrl-C to end the test programs on both the Mac and the
RPi. Note that because a timer thread is running to read the sensor probe, it
is likely that an exception thread traceback message will be printed to the
console after you press Ctrl-C in the RPi terminal window. That's normal.

Testing **imagenode** running on one or more RPi's using **imagehub**
=====================================================================

After you have tested **imagenode** with ``receive_test.py`` running as a test
hub, the next step would be to add a full
**imagehub** program to the mix. In this arrangement, the **imagehub** program
would be started on a Mac or Linux computer. One or more RPi's would have their
~/imagenode.yaml files changed to assign appropriate detectors and point to
appropriate hub address. In my production use cases, a single **imagehub** is able
to receive detector event messages and detector event images from 8 RPi's at
a time without significantly impacting the framerates of the RPi's. To test
the **imagenode** software with **imagehub**, git clone and then run the test
programs in the **imagehub**
`GitHub repository <https://github.com/jeffbass/imagehub>`_.


`Return to main documentation page README.rst <../README.rst>`_
