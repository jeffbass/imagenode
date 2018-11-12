==============================================================
How **imagenode** works: pseudo code and data structure design
==============================================================

Here's what **imagenode** does::

  # stuff done one time at program startup
  Read a YAML file into Settings (e.g. cameras, ROIs, detector settings)
  Instantiate a Node using Settings:
    Instantiate Cameras
    For each Camera:
      Instantiate one or more Detectors (e.g. motion detector) with ROI etc.
    Instantiate Sensors
    Instantiate Lights (and turn them on as specified)
    Read one test frame from camera to set actual frame size

  # stuff done to read and process each frame
  Loop forever:
    For each Camera:
      Read a Camera image into image_queue
      For each Detector:
        Detect current_state using images in image_queue
        If current_state has changed (e.g. motion started or motion stopped)
          Send event_message and image_queue to hub

Here are the classes and data structures::

  Class Settings (filled once by reading from the YAML file)
  Class Node (instantiated once using Settings)
    Class Camera (can instantiate zero or more cameras)
      Class Detector (instantiate one or more per camera)
        Attributes: Detector_type, ROI_corners, parameters (threshold values, etc.)
    Class Sensor (can instantiate zero or more sensors, e.g. temperaure probe)
    Class Light (can instantiate setup of one or more LED lights)

  Class HealthMonitor (methods for helping monitory system and network health)

The Cameras, Detectors and Detector Attributes are all specified in the YAML
file. It details the (many!) settings needed to completely specify a Node.
You can read more about the YAML file and get examples of settings at
`imagenode Settings and the imagenode.yaml file <settings-yaml.rst>`_.

The ``HealthMonitor`` class is pretty simple so far. It determines what
kind of computer **imagenode** is running on so that the right camera, sensor
and light control libraries can be imported. It also holds the methods to
implement ``heartbeat`` messages to help maintain network reliablity. You can
read more about the ``HealthMonitor`` class in the
`HealthMonitor documentation <nodehealth.rst>`_.

In essence, the **imagenode** program runs one or more cameras and sends a
highly selective stream of images and status messages to the **imagehub**.
The **imagehub** stores the messages in event logs and stores the images in
image history directories.

Messaging protocol for images and status messages
=================================================

By design, every message passed by **imagenode** to the **imagehub** (or to a
test hub) has a specific format. Every message is sent using **imagezmq** and
is a tuple::

  (text, image)

There are 2 categories of messages: (1) event messages that are text (with no
image from a camera), and (2) images from a camera.

**Event messages** are about detected events, such as "lighted" or "dark". For
event messages, the image portion of the tuple is a tiny black image. This
allows all messages to have the same tuple layout.

**Image messages** have identifying information (like node name, view name, etc.)
in the text portion of the tuple, and the image itself (or jpeg version of the
image) in the image portion of the tuple.

In both message types, the "|" character is used as a field delimiter. If there
is only one camera, then the view name could be absent.

Event messages look like this (there is also a small black image as 2nd part of
each message tuple, not shown here)::
  WaterMeter|startup|
  WaterMeter|OK|                 # If Heartbeat message option chosen
  WaterMeter|motion|moving
  WaterMeter|motion|still
  Garage|light|lighted
  Garage|light|dark
  JeffOffice window|light|lighted
  JeffOffice door|motion|still

The template for **event** messages is::
  node name and view name|information|detected state

Image messages look like this (the image itself is the 2nd part of each
message tuple, not shown here)::
  WaterMeter|jpg|moving
  WaterMeter|image|moving
  Garage|jpg|lighted
  Garage|image|lighted

The template for **image** messages is::
    node name and view name|send_type|detector state

When running tests, such as when using the **imagezmq** ``timing_receive_jpg_buf``
program as a "test hub", the messages text portion will be displayed as the window
label bar by the cv2.show() function.

The node name and view name must be unique, because the node name and view name
define the sorting criteria for how the messages and images are filed and stored.

((TODO put more details here, including stuff about testing with status messages))

Some Overall Design Choices (that may or may not be obvious)
============================================================

A YAML file was chosen for setting the **many** options needed to define what
images to select and send. This seems more readable, especially for the nested
options that are necessary to set up a motion detector, for example. Choices
that were possible but rejected include using command line arguments, using a
json configuration file and using a config.ini file (Python module is?)

Every message from **imagenode** to the **imagehub** is a tuple::

  (text, image)

This allows **imagezmq** and **imagehub** to transfer and receive every message
packet the same way, without any "what kind of packet is this?" if statements.
Even when an event message has no image to send, a blank 1 pixel image is sent
so that all ZMQ messages can have exactly the same tuple structure.

Images can be sent in OpenCV / Numpy image format or in jpeg compressed form.
The transmission type defaults to jpeg, but can be set to "image" in the YAML
settings file. Once set, all images will be sent in the same format thereafter.
This means that no "image or jpg?" if statement is needed in the image sending
loop. This means that **imagehub** has a similar option that is set to image or
jpg at startup.

To allow the highest frame rate possible, several design choices were made
to make the event loop as fast as possible. This makes the initialization code
much longer but enables far fewer if statements and fewer dictionary gets in the
event loop. The result is that the __init__() functions for the Settings,
Camera, and Detector classes are long sequences of if statements, but there are
relatively few if statements in the event loop. These design choices were
the most helpful in speeding up the event loop:

1. Using multiple if statements in Settings.__init__ to parse nested yaml
  dictionary to a flat set of node Attributes.
2. Using function templates to set up functions that are specific to an option
  choice. For example, the ``send_frame function`` is set to either the
  ``send_jpg_frame`` function or ``send_image_frame`` function during __init__,
  so that there does not to be an if statement about image type in the event
  loop itself.

An example of design choice 1: camera-->event loop-->frames-to-send becomes
camera.frames instead of camera['send_amount']['event']. This makes the
Settings.__init__ a bit hard to read, but makes the event loop only reference
first level attributes.  That means that this nested dictionary get::

  send_multiple(camera['send_amount']['event'])

becomes a first level attribute of camera object::

  send_multiple(camera.frames)

An example for design choice 2 is the choice of jpg vs image execution. Instead of
(use python code rst display here)::

  # inside event loop there is if statement about jpg vs. image choice
  # design choice is to NOT to do it this way!
  for image in send_q:
    if settings.send_type == 'jpg':
        send_jpg(image)
    else:
        send_image(image)

Instead, the choice of frame type is moved to a one-time function choice in
Settings.__init__. That way, there is no if statement needed in the event
loop::

  # make the jpg vs. image choice one time only in Settings.__init__
  if settings.jpg:
      send_frame = send_jpg  # send_jpg is a jpg specific frame sending function
  else:
      send_frame = send_image  # send_image is image specific send function

  # inside event loop, there are no if statements about jpg vs. image choice
  for image in send_q:
      send_frame()  # now there is no if statement in frame send loop

These design choices make the Settings.__init__ code longer and more convoluted,
but make the actual event loop faster and more readable. There is more
refactoring to be done in this regard.

The overall design of **imagenode** is around the image capture and detection
event loop. Other sensors, e.g. temperature sensors, are managed from threads,
one per sensor. These threads check the sensor at selectable time intervals,
report a value, then sleep until the next time interval. The image capture
and detection loop is the main thread and gets most of the cpu resources.

`Return to main documentation page README.rst <../README.rst>`_
