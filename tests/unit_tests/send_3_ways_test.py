"""send_3_ways_test.py -- send PiCamera jpg stream 3 ways for relatving timing

Intended to be run on a Raspberry Pi. It uses imagezmq to send image frames from
the PiCamera continuously to a receiving program on a Mac that will display the
images as a video stream. Images are converted to jpg format before sending.

The receiving program run on the Mac is called FPS_receive_test.py.

This program requires that the image receiving program be running first.

There are 3 ways to send images: no-stall-test, signal.alrm stall test and
watch_queue stall test.

By running each of these while keeping the other settings the saem, it is
possible to determine the relative time performance of each.

The purpose is to decide which method to use to detect a failure in the ZMQ
network connection. All of the tests send jpg compressed images since that is
what I'm using in production.
"""

import sys
import time
import cv2
from imutils.video import VideoStream
import imagezmq

################################################################################
# EDIT THES OPTIONS BEFORE RUNNING PROGRAM
SEND_METHOD_CHECKING = None  # None or SIGALRM or watch_queue
# connect_to='tcp://jeff-macbook:5555'      # pick and edit one of these
# connect_to='tcp://192.168.1.190:5555'
connect_to='tcp://127.0.0.1:5555'
usePiCamera = False   # True if using PiCamera on RPi; False if webcam
################################################################################

def send_method():  # this will be replaced by send_method chosen above
    pass

def send_with_no_checking(picam, sender, jpeg_quality):
    while True:  # send images as stream until Ctrl-C
        image = picam.read()
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
        reply = sender.send_jpg("no_checking", jpg_buffer)

sender = imagezmq.ImageSender(connect_to=connect_to)
picam = VideoStream(usePiCamera=usePiCamera,
                    resolution=(640, 480),framerate=32).start()
time.sleep(2.0)  # allow camera sensor to warm up
jpeg_quality = 95  # 0 to 100, higher is better quality, 95 is cv2 default
if not SEND_METHOD_CHECKING:  # No stall checking
    send_method = send_with_no_checking
elif SEND_METHOD_CHECKING == 'SIGALRM':
    send_method = send_with_sigalrm
elif SEND_METHOD_CHECKING == 'watch_queue':
    send_method = send_with_watch_queue
else:
    print("No valid send method. Ending program.")
    sys.exit()
send_method()
sys.exit()
