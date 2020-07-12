"""max_fps_picam.py -- determine maximum FPS for different PiCamera modes

All the imagenode programs that use the PiCamera capture_continuous method.
This test program counts how many frames per second that the camera is able
to capture, using the imutils package.

It computes and prints FPS statistics.
"""

import sys

import time
import cv2
from imutils.video import VideoStream, FPS

SHOW_IMAGES = False  # SHOW_IMAGES will slow down FPS; only use to check PiCamera
NUM_FRAMES = 100  # How many frames to capture for this test

picam = VideoStream(usePiCamera=True,resolution=(320, 240),framerate=32).start()
time.sleep(2.0)  # allow camera sensor to warm up
fps = FPS().start()  # start FPS timer after first image is received
frame_count = 0

while frame_count <= NUM_FRAMES:  # send images as stream until Ctrl-C
    image = picam.read()
    frame_count += 1
    fps.update()
    if SHOW_IMAGES:  # SHOW_IMAGES will slow down FPS
        cv2.imshow('PiCamera', image)  # 1 window for each RPi
        cv2.waitKey(1)

fps.stop()
print('FPS Test Program: ', __file__)
print('Option settings:')
print('    Show Images? ', SHOW_IMAGES)
print('    Number of Frames? ', NUM_FRAMES)
image_size = image.shape
print('Size of last image received: ', image_size)
uncompressed_size = 1
for dimension in image_size:
    uncompressed_size *= dimension
print('    = {:,g} bytes'.format(uncompressed_size))
print('Elasped time: {:,.2f} seconds'.format(fps.elapsed()))
print('Approximate FPS: {:.2f}'.format(fps.fps()))
cv2.destroyAllWindows()  # closes the windows opened by cv2.imshow()
image_hub.close()  # closes ZMQ socket and context
sys.exit()
