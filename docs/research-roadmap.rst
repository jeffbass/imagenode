==========================================
imagenode Research and Development Roadmap
==========================================

Overview
--------

**imagenode** is constantly evolving. It is a "science project" that is part of
a larger system to observe, monitor and optimize a small permaculture farm. It
is part of a distributed computer vision and sensor network. Here is where I
keep the list of the stuff I'm experimenting with but haven't pushed to GitHub
yet. Feel free to open an issue and make suggestions or start a discussion
about a potential change or new feature. The list below is not in any particular
order; all of these are ongoing experiments on differing timelines.

.. contents::

Add ability to capture images from image files rather than from a camera
------------------------------------------------------------------------
For tracking photosynthesis hours and general weather tracking, it is helpful

Adding the ability to capture images from files in an image directory as a
substitute for capturing images from a camera will allow testing and tuning
of options from real world images gathered by imagenodes scattered around the
farm. The existing stored image library is large and could potentially be used
for adding machine learning capability to the RPi imagenodes.

Develop a "large memory buffer" using new Python 3.8 SharedMemory class
-----------------------------------------------------------------------
The idea: have the camera capture main thread put images in a very
large (up to available memory; could be 3GB on RPi 4 models). Then the sending
of images could occur in a separate process that empties the buffer by
sending images via **imageZMQ**. The advantage of this over the existing
``send_threading`` option would be using a 2nd process (and a different
RPi core) rather than a 2nd thread running on the same core.

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

Add a "transmit only the Grayscale ROI" instead of entire image option
----------------------------------------------------------------------
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
