"""FPS_receive_test.py -- receive (text, image) pairs & print FPS stats

A test program to provide FPS statistics as different imagenode algorithms are
being tested. This program receives images OR images that have been jpg
compressed, depending on the setting of the JPG option.

It computes and prints FPS statistics. It is designed to be the receiver for the
imagenode.py program or one of the test programs in the tests/unit_tests folder.

Be sure to run this program and the sending program in virtual environments
using Python 3.6 or newer.

1. Edit the options in this python program, such as the JPG option.
   Save it.

2. Set the yaml options on the imagenode sending RPi in the imagenode.yaml
   file at the home directory. Be sure that the jpg setting on the RPi matches
   the setting of JPG below. (If using one of the test programs, use git
   pull to bring a copy of the test program to the sending RPi)

2. Run this program in its own terminal window on the mac:
   python receive_test.py.

   This 'receive the images' program must be running before starting
   the RPi image sending program.

2. Run the imagenode image sending program on the RPi:
   python imagenode.py  # OR run one of /tests/unit_tests programs on the RPi

A cv2.imshow() window will only appear on the Mac that is receiving the
tramsmitted images if the "SHOW_IMAGES" option below is set to True.

The receiving program will run until the "TEST_DURATION" number of seconds is
reached or until Ctrl-C is pressed. When the receiving program ends, it will
compute and print FPS statistics and it will stop receiving images and sending
ZMQ "REP" replies. That should cause the sending program on the RPi to stall
and stop. Or you can end the sending program running on the RPi by pressing
Ctrl-C.

"""

########################################################################
# EDIT THES OPTIONS BEFORE RUNNING PROGRAM
JPG = True  # or False if receiving images
SHOW_IMAGES = True
TEST_DURATION = 30  # seconds or 0 to keep going until Ctrl-C
########################################################################

import cv2
import sys
import signal
import imagezmq
import traceback
import numpy as np
from time import sleep
from imutils.video import FPS
from threading import Event, Thread
from collections import defaultdict

# instantiate image_hub
image_hub = imagezmq.ImageHub()

def receive_image():
    text, image = image_hub.recv_image()
    return text, image

def receive_jpg():
    text, jpg_buffer = image_hub.recv_jpg()
    image = cv2.imdecode(np.frombuffer(jpg_buffer, dtype='uint8'), -1)
    return text, image

if JPG:
    receive_tuple = receive_jpg
    receive_type = 'jpg'
else:
    receive_tuple = receive_image
    receive_type = 'native OpenCV'

image_count = 0
sender_image_counts = defaultdict(int)  # dict for counts by sender
first_image = True
text = None
image = None
if TEST_DURATION <= 0:
    TEST_DURATION = 999999  # a large number so Ctrl-C is only stopping method

def receive_images_forever():
    global image_count, sender_image_counts, first_image, text, image, fps
    keep_going = Event()
    keep_going.set()

    def timer(duration):
        sleep(duration)
        keep_going.clear()
        sleep(10)  # allow cleanup finally time

    while keep_going.is_set():  # receive images until timer expires or Ctrl-C
        text, image = receive_tuple()
        if first_image:
            print('First Image Received. Starting FPS timer.')
            fps = FPS().start()  # start FPS timer after first image is received
            Thread(target=timer, daemon=True, args=(TEST_DURATION,)).start()
            first_image = False
        fps.update()
        image_count += 1  # global count of all images received
        sender_image_counts[text] += 1  # count images for each RPi name
        if SHOW_IMAGES:
            cv2.imshow(text, image)  # display images 1 window per unique text
            cv2.waitKey(1)
        image_hub.send_reply(b'OK')  # REP reply

try:
    print('FPS Test Program: ', __file__)
    print('Option settings:')
    print('    Receive Image Type:', receive_type)
    print('    Show Images:', SHOW_IMAGES)
    print('    Test Duration:', TEST_DURATION, ' seconds')
    receive_images_forever()
    sys.exit()
except (KeyboardInterrupt, SystemExit):
    pass  # Ctrl-C was pressed to end program; FPS stats computed below
except Exception as ex:
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()
finally:
    # stop the timer and display FPS information
    print()
    print('Total Number of Images received: {:,g}'.format(image_count))
    if first_image:  # never got images from any sender
        print('Never got any images from imagenode. Ending program.')
        sys.exit()
    fps.stop()
    print('Number of Images received for each text message type:')
    for text_message in sender_image_counts:
        print('    ', text_message, ': {:,g}'.format(sender_image_counts[text_message]))
    if JPG:
        compressed_size = len(image)
        print('Size of last jpg buffer received: {:,g} bytes'.format(compressed_size))
    else:
        compressed_size = 1
    image_size = image.shape
    print('Dimensions of last image received: ', image_size)
    uncompressed_size = 1
    for dimension in image_size:
        uncompressed_size *= dimension
    print('    = {:,} bytes'.format(uncompressed_size))
    print('Compressed to Uncompressed ratio: {:.8f}'.format(compressed_size / uncompressed_size))
    print('Elasped time: {:,.2f} seconds'.format(fps.elapsed()))
    print('Approximate FPS: {:,.2f}'.format(fps.fps()))
    cv2.destroyAllWindows()  # closes the windows opened by cv2.imshow()
    image_hub.close()  # closes ZMQ socket and context
    sys.exit()
