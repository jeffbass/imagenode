==========================================
imagenode Research and Development Roadmap
==========================================

.. contents::

Overview
========

**imagenode** is constantly evolving. It is a "science project" that is part of
a larger system to observe, monitor and optimize a small permaculture farm. It
is part of a distributed computer vision and sensor network. Here is where I
keep the list of the stuff I'm experimenting with but haven't pushed to GitHub
yet. Feel free to open an issue and make suggestions or start a discussion
about a potential change or new feature. The list below is not in any particular
order; all of these are ongoing experiments on differing timelines

Receive and act on commands or requests from imagehub
-----------------------------------------------------
Right now, the imagehub returns "OK" after every message tuple is sent. The
imagehub reply can be a "command word" instead that would cause imaghub to take
an action such as change the exposure_mode of the PiCamera. Or send a dozen
"live frames" from the camera (even though no detector has activated). Command
words look like this:
- OK  # that is the only one now and is sent back for every reply
- ReloadYaml  # reload the yaml file to get a change in one of the options.
- SendFrames 10  # Send some frames now, even if no detector is activated.
- Set Resolution (640,480)  # set a new resolution value for the camera

Add an option to send message tuples (text, image) in a thread
--------------------------------------------------------------
Currently, all message tuples are sent in main event loop. Performance may be
better (better speed, etc.) by putting the send message function in a separate
thread. Early experiments show an increase in FPS speed.

Add a "color" detector to detect changes in sky color
-----------------------------------------------------
For tracking photosynthesis hours and general weather tracking, it is helpful
to know how "blue" the sky is. Hazy blue sky with some humidity is different than
the more saturated blue of a dry air clear day. I am working on a study of sky
color / cloud density with multiple RPi cameras aimed skyward. Using a change
in HSV "Hue" value as the detector threshold, much the way the light detector
uses the light threshold. Some experiments are ongoing.

Add "timing" to LED lighting commands and to exposure_mode
----------------------------------------------------------
Time of day sub option could allow lighting or exposure_mode to change by
time in the daylight cycle. Or perhaps, an average light value below a threshold
could turn on the light and/or change the exposure_mode to "night", for example.

Use the GPU on the Raspberry Pi to do some of the morphological stuff
---------------------------------------------------------------------
Right now, OpenCV functions are being used to flip images (vflip option),
resize images, etc. The Raspberry Pi GPU and the PiCamera library can perform
many of these function. It may be much faster to let the RPi GPU / camera
hardware do these. Need to do some actual timing tests to see. It may not
make enough of a difference to make all the if statements worth while, since
non-PiCameras and Webcams don't have those GPU functions available.

Add a "transmit only the Grayscale ROI" instead of entire image
---------------------------------------------------------------
In my current configuration, bandwidth is a limiting factor on performance. For
some imagenode such as the water meter, the Grayscale ROI (of just the digits)
has all the information needed. Perhaps add an option to transmit only the
Grayscale ROI? Also, if that is an option, it would be possible to take higher
resolution images and then the cropped ROI would have more pixel level detail,
without the bandwidth of sending the entire higher resolution image. The RPi
PiCamera is capable of 3280 x 2464 pixels. Taking a high resolution image and
then sending only the cropped smaller ROI is effectively "zooming in" on the
ROI.








`Return to main documentation page README.rst <../README.rst>`_
