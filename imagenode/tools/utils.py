"""utils: various utility functions used by imagenode and imagehub

Copyright (c) 2017 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import os
import sys
import time
import signal
import logging

def versionCompare(v1, v2):
    """Method to compare two version number
    Return 1 if v2 is smaller,
    -1 if v1 is smaller,,
    0 if equal

    This code is contributed by Nikhil Kumar Singh(nickzuck_007)
    and improved by Tuhin Das (tuhindas221b)
    """

    # This will split both the versions by '.'
    arr1 = v1.split(".")
    arr2 = v2.split(".")
    n = len(arr1)
    m = len(arr2)

    # converts to integer from string
    arr1 = [int(i) for i in arr1]
    arr2 = [int(i) for i in arr2]

    # compares which list is bigger and fills
    # smaller list with zero (for unequal delimeters)
    if n>m:
    	for i in range(m, n):
    		arr2.append(0)
    elif m>n:
    	for i in range(n, m):
    		arr1.append(0)

    # returns 1 if version 1 is bigger and -1 if
    # version 2 is bigger and 0 if equal
    for i in range(len(arr1)):
    	if arr1[i]>arr2[i]:
    		return 1
    	elif arr2[i]>arr1[i]:
    		return -1
    return 0

def clean_shutdown_when_killed(signum=signal.SIGTERM, *args):
    """Close all connections cleanly and log shutdown
    """
    logging.warning('SIGTERM detected, shutting down')
    sys.exit()

def interval_timer(interval, action):
    """ Call the function 'action' every 'interval' seconds

    This is typically used in a thread, since it blocks while it is sleeping
    between action calls. For example, when a check_temperature sensor is
    instantiated, this timer is started in a thread to call the
    check_temperature function at specified intervals.

    Parameters:
        interval (int): How often to call the function 'action' in seconds
        action (function): Function to call
    """
    next_time = time.time() + interval
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            action()
        except (KeyboardInterrupt, SystemExit):
            logging.warning('Ctrl-C was pressed or SIGTERM was received.')
            raise
        except Exception:
            logging.exception('Error in interval_timer')
        next_time += (time.time() - next_time) // interval * interval + interval
