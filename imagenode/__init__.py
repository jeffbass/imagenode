"""imagenode: capture, transform and transfer images to imagehub

Enables Raspberry Pi computers to capture images with the PiCamera, perform
image transformations and send the images to a central imagehub for further
processing. Can send other sensor data such as temperature data and GPIO data.
Works on other types of (non Raspberry Pi) computers with webcams.

Typically run as a service or background process. See README.rst for details.

Copyright (c) 2018 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""
# populate fields for >>>help(imagezmq)
from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__
