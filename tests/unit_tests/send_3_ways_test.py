"""send_3_ways_test.py -- send PiCamera jpg stream 3 ways for relatving timing

Intended to be run on a Raspberry Pi. It uses imagezmq to send image frames from
the PiCamera continuously to a receiving program on a Mac that will display the
images as a video stream. Images are converted to jpg format before sending.

The purpose of this progam is to understand how much time it adds to the
imagezmq.ImageSender send_jpg method to wrap the send in either the operating
system SIGALRM timer or a threading.Timer. After multiple experiments,
neither one adds a significant amount of time. The operating system SIGALRM can
only be used in the main Python thread (or a separate process? Not sure.),
while the threading.Timer can be used in threads that are not the main thread.
The downside is that it adds another running thread.

The receiving program run on the Mac is called FPS_receive_test.py.

This program requires that the image receiving program be running first.

There are 3 ways to send images: no-stall-test, signal.alrm stall test and
threaded_timer stall test.

By running each of these while keeping the other settings the same, it is
possible to determine the relative time performance of each.

The purpose is to decide which method to use to detect a failure in the ZMQ
network connection. All of the tests send jpg compressed images since that is
what I'm using in production.

Quick Summary of results.
1. SIGALRM reacts correctly and raises Exception and does NOT add significantly
   to send_jpg() sending time.
2. Could never get the ThreadedTimer to time_out. It sent images, but just
   hung until interrrupted when it did not get a REP. Won't be using it.

"""

import sys
import cv2
import time
import signal
import imagezmq
import traceback
from imutils.video import VideoStream
from threading import Timer

SIGALRM = 'SIGALRM'
threaded_timer = 'threaded_timer'

################################################################################
# EDIT THES OPTIONS BEFORE RUNNING PROGRAM
SEND_METHOD_CHECKING = threaded_timer  # None or SIGALRM or threaded_timer
# connect_to='tcp://jeff-macbook:5555'      # pick and edit one of these
# connect_to='tcp://192.168.1.190:5555'
connect_to='tcp://127.0.0.1:5555'
usePiCamera = False   # True if using PiCamera on RPi; False if webcam
patience_seconds = 5  # how many seconds to wait for REP before giving up
################################################################################

class Patience:
    """Timing class using operating system SIGALRM signal.

    When instantiated, starts a timer using the system SIGALRM signal.
    If the timer expires before __exit__ is called, raises Timeout exception.

    Caveats:
    1. There can be only 1 active SIGALRM timer running per program. If a
       second SIGALRM timer is started, it replaces and nullifies the first one.
    2. This class can only be used in the main thread. Python only allows the
       use of SIGALRM in the main thread (or also in the main thread of a separate
       process? Don't know. Need to run the experiment.)

    Parameters:
        seconds (int): number of seconds to wait before raising exception
    """
    class Timeout(Exception):
        pass

    def __init__(self, seconds):
        self.seconds = seconds

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Patience.Timeout()

class ThreadedTimer:
    """Timing class using threading.

    When instantiated, starts a thread that watches for REQ and REP events.

    Parameters:
        seconds (int): number of seconds to wait before raising exception
    """
    class Timeout(Exception):
        pass

    def __init__(self, seconds):
        self.seconds = float(seconds)

    def __enter__(self):
        self.timer = Timer(self.seconds, self.raise_timeout)  # how long before raising Timeout

    def __exit__(self, *args):
        self.timer.cancel()  # we got a REP, cancel timer
        del self.timer       # this didn't help, either?

    def raise_timeout():
        print('Got to raise_timeout.')
        time.sleep(self.seconds)  # sleeping an additional time helps?
        self.timer.cancel()
        raise ThreadedTimer.Timeout()

def send_method():  # this will be replaced by send_method chosen above
    pass

def send_with_no_checking(picam, sender, jpeg_quality, patience_seconds):
    while True:  # send images as stream until Ctrl-C
        image = picam.read()
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
        reply = sender.send_jpg("no_checking", jpg_buffer)

def send_with_sigalrm(picam, sender, jpeg_quality, patience_seconds):
    while True:  # send images as stream until Ctrl-C or until stall out
        image = picam.read()
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
        try:
            with Patience(patience_seconds):
                reply = sender.send_jpg(SIGALRM, jpg_buffer)
        except Patience.Timeout:  # if no timely response from hub
            print('During image send in SIGALRM test,')
            print('No REP received back for', patience_seconds, 'seconds.')
            print('Ending sending program.')
            sys.exit()

def send_with_timer(picam, sender, jpeg_quality, patience_seconds):
    while True:  # send images as stream until Ctrl-C or until stall out
        image = picam.read()
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])
        try:
            with ThreadedTimer(patience_seconds):
                reply = sender.send_jpg(threaded_timer, jpg_buffer)
        except ThreadedTimer.Timeout:  # if no timely response from hub
            print('During image send in threaded_timer test,')
            print('No REP received back for', patience_seconds, 'seconds.')
            print('Ending sending program.')
            sys.exit()

sender = imagezmq.ImageSender(connect_to=connect_to)
picam = VideoStream(usePiCamera=usePiCamera,
                    resolution=(640, 480),framerate=32).start()
time.sleep(2.0)  # allow camera sensor to warm up
jpeg_quality = 95  # 0 to 100, higher is better quality, 95 is cv2 default
if not SEND_METHOD_CHECKING:  # No stall checking
    send_method = send_with_no_checking
    print("Sending with no stall checking.")
    print("...therefore MUST end by Ctrl-C.")
elif SEND_METHOD_CHECKING == 'SIGALRM':
    send_method = send_with_sigalrm
    print("Sending with SIGALRM checking.")
elif SEND_METHOD_CHECKING == 'threaded_timer':
    send_method = send_with_timer
    print("Sending with threaded_timer checking.")
else:
    print("No valid send method. Ending program.")
    sys.exit()

try:
    send_method(picam, sender, jpeg_quality, patience_seconds)
except (KeyboardInterrupt, SystemExit, ZeroDivisionError):
    sys.exit()
except Exception as ex:
    print('Python error with no Exception handler:')
    print('Traceback error:', ex)
    traceback.print_exc()
finally:
    sys.exit()
