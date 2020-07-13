"""max_fps_picam.py -- determine maximum FPS for different PiCamera framerates

Framerate settings don't seem to affect PiCamera capture_continuous method.
This test program counts how many frames per second that the camera is able
to capture.

It computes and prints FPS statistics.
"""

import sys

import time
import cv2
from datetime import datetime
from imutils.video import VideoStream

SHOW_IMAGES = False  # SHOW_IMAGES will slow down FPS; only use to check PiCamera
NUM_FRAMES = 10000  # How many frames to capture for this test

picam = VideoStream(usePiCamera=False,resolution=(320, 240),framerate=1).start()
time.sleep(2.0)  # allow camera sensor to warm up
image = picam.read()  # read one image before loop to trap potential errors
start = datetime.now()
frame_count = 0

while frame_count < NUM_FRAMES:  # send images as stream until Ctrl-C
    image = picam.read()
    frame_count += 1
    if SHOW_IMAGES:  # SHOW_IMAGES will slow down FPS
        cv2.imshow('PiCamera', image)  # 1 window for each RPi
        cv2.waitKey(1)

stop = datetime.now()
print('FPS Test Program: ', __file__)
print('Option settings:')
print('    Show Images? {}'.format(SHOW_IMAGES))
print('    Requested Frames: {:,}'.format(NUM_FRAMES))
print('    Actual Frames Read:  {:,}'.format(frame_count))
print('Dimensions of last image received: ', image.shape)
size = 1
for dimension in image.shape:
    size *= dimension
print('    = {:,} bytes'.format(size))
elapsed = stop - start  # elapsed time datetime.timedelta() format
seconds = elapsed.total_seconds()
print('Elasped time:', seconds, 'seconds')
fps = frame_count / seconds
print('Approximate FPS: {:,.2f}'.format(fps))
cv2.destroyAllWindows()  # closes the windows opened by cv2.imshow()
sys.exit()
