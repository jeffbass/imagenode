"""max_fps_picam.py -- determine maximum FPS for different PiCamera modes

All the imagenode programs that use the PiCamera capture_continuous method.
This test program counts how many frames per second that the camera is able
to capture, using the imutils package.

It computes and prints FPS statistics.
"""

import sys

import time
import cv2
from datetime import datetime
from imutils.video import VideoStream

SHOW_IMAGES = True  # SHOW_IMAGES will slow down FPS; only use to check PiCamera
NUM_FRAMES = 1000  # How many frames to capture for this test

picam = VideoStream(usePiCamera=True,resolution=(320, 240),framerate=32).start()
time.sleep(2.0)  # allow camera sensor to warm up
start = datetime.now()
frame_count = 0

while frame_count <= NUM_FRAMES:  # send images as stream until Ctrl-C
    image = picam.read()
    frame_count += 1
    if SHOW_IMAGES:  # SHOW_IMAGES will slow down FPS
        cv2.imshow('PiCamera', image)  # 1 window for each RPi
        cv2.waitKey(1)

stop = datetime.now()
print('FPS Test Program: ', __file__)
print('Option settings:')
print('    Show Images?', SHOW_IMAGES)
print('    Requested Frames?', NUM_FRAMES)
print('    Actual Frames Read:', frame_count)
image_size = image.shape  # want size expressed numpy dimentions
print('Size of last image received: ', image_size)
uncompressed_size = 1
for dimension in image_size:
    uncompressed_size *= dimension
print('    = {:,}'.format(uncompressed_size))
elapsed = stop - start  # elapsed time datetime.timedelta() format
seconds = elapsed.total_seconds()
print('Elasped time:', seconds)
fps = frame_count / seconds
print('Approximate FPS: {:.2f}'.format(fps))
cv2.destroyAllWindows()  # closes the windows opened by cv2.imshow()
sys.exit()
