"""imaging: imagenode, camera, sensor and image processing classes
Also reads settings from imagenode.yaml file.

Copyright (c) 2017 by Jeff Bass.
License: MIT, see LICENSE for more details.
"""

import os
import sys
import yaml
import pprint
import signal
import logging
import itertools
import threading
from time import sleep
from ast import literal_eval
from collections import deque
import numpy as np
import cv2
import imutils
from imutils.video import VideoStream
sys.path.insert(0, '../../imagezmq/imagezmq') # for testing
import imagezmq
from tools.utils import interval_timer
from tools.nodehealth import HealthMonitor

class ImageNode:
    """ Contains all the attributes and methods of this imagenode

    One ImageNode is instantiated during the startup of the imagenode.py
    program. It takes the settings loaded from the YAML file and sets all
    the operational parameters of the imagenode, including the hub address that
    images and messages will be sent to, camera settings, sensors, etc. as
    attributes of the ImageNode.

    The ImageNode also contains all the methods to gather, process and send
    images, event detection messages and sensor data to the ImageHub.

    Parameters:
        settings (Settings object): settings object created from YAML file
    """

    def __init__(self, settings):
        # set various node attributes; also check that numpy and OpenCV are OK
        self.tiny_image = np.zeros((3,3), dtype="uint8")  # tiny blank image
        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", self.tiny_image, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        self.tiny_jpg = jpg_buffer # matching tiny blank jpeg
        self.jpeg_quality = 95

        # set up message queue to hold (text, image) messages to be sent to hub
        self.send_q = deque(maxlen=settings.queuemax)
        # start system health monitoring & get system type (RPi vs Mac etc)
        self.health = HealthMonitor(settings, self.send_q)

        self.sensors = []  # need an empty list even if no sensors
        self.lights = []
        if self.health.sys_type == 'RPi':  # set up GPIO & sensors
            global GPIO
            import RPi.GPIO as GPIO
            if settings.sensors or settings.lights:
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
            if settings.sensors:   # is there at least one sensor in yaml file
                global W1ThermSensor  # for DS18B20 temperature sensor
                from w1thermsensor import W1ThermSensor
                self.setup_sensors(settings)
            if settings.lights:   # is there at least one light in yaml file
                self.setup_lights(settings)

        self.send_frame = self.send_jpg_frame # default send function is jpg
        if settings.send_type == 'image':
            self.send_frame = self.send_image_frame # set send function to image
        else: # anything not spelled 'image' is set to jpg
            self.send_frame = self.send_jpg_frame # set send function to jpg

        # set up and start camera(s)
        self.camlist = []  # need an empty list if there are no cameras
        if settings.cameras:  # is there at least one camera in yaml file
            self.setup_cameras(settings)

        # open ZMQ link to imagehub
        # use either of the formats below to specifiy address of display computer
        # sender = imagezmq.ImageSender(connect_to='tcp://jeff-macbook:5555')
        # self.sender = imagezmq.ImageSender(connect_to='tcp://192.168.1.190:5555')
        self.sender = imagezmq.ImageSender(connect_to=settings.hub_address)

        # Read a test image from each camera to check and verify:
        # 1. test that all cameras can successfully read an image
        # 2. determine actual camera resolution from returned image size
        # 3. if resize_width has been set, test that it works without error
        # 4. for each detector, convert roi_pct to roi_pixels
        # Note that image size returned from reading the camera can vary from
        # requested resolution size, especially in webcams
        for camera in self.camlist:
            testimage = camera.cam.read()
            image_size = testimage.shape  # actual image_size from this camera
            width, height = image_size[1], image_size[0]
            camera.res_actual = (width, height)
            if camera.resize_width:
                camera.width_pixels = (width * camera.resize_width) // 100
                testimage = imutils.resize(testimage, width=camera.width_pixels)
                image_size = testimage.shape
                width, height = image_size[1], image_size[0]
            else:
                camera.width_pixels = width
            camera.res_resized = (width, height)
            # compute ROI in pixels using roi_pct and current image size
            for detector in camera.detectors:
                top_left_x = detector.roi_pct[0][0] * width // 100
                top_left_y = detector.roi_pct[0][1] * height // 100
                bottom_right_x = detector.roi_pct[1][0] * width // 100
                bottom_right_y = detector.roi_pct[1][1] * height // 100
                detector.top_left = (top_left_x, top_left_y)
                detector.bottom_right = (bottom_right_x, bottom_right_y)
                detector.roi_pixels = (detector.top_left, detector.bottom_right)
                detector.roi_area = ((bottom_right_x - top_left_x)
                                    * (bottom_right_y - top_left_y))
                if detector.detector_type == 'motion':
                    detector.min_area_pixels = (detector.roi_area
                                                * detector.min_area) // 100

        if settings.print_node:
            self.print_node_details(settings)

    def print_node_details(self, settings):
        print('Node details after setup and camera test read:')
        print('  Node name:', settings.nodename)
        print('  System Type:', self.health.sys_type)
        for cam in self.camlist:
            print('  Camera:', cam.cam_type)
            print('    Resolution requested:', cam.resolution)
            print('    Resolution actual after cam read:', cam.res_actual)
            print('    Resize_width setting:', cam.resize_width)
            print('    Resolution after resizing:', cam.res_resized)
            for detector in cam.detectors:
                print('    Detector:', detector.detector_type)
                print('      ROI:', detector.roi_pct, '(in percents)')
                print('      ROI:', detector.roi_pixels, '(in pixels)')
                print('      ROI area:', detector.roi_area, '(in pixels)')
                print('      send_test_images:', detector.send_test_images)
                print('      send_count:', detector.send_count)
                if detector.detector_type == 'light':
                    print('      threshhold:', detector.threshold)
                    print('      min_frames:', detector.min_frames)
                elif detector.detector_type == 'motion':
                    print('      delta_threshhold:', detector.delta_threshold)
                    print('      min_motion_frames:', detector.min_motion_frames)
                    print('      min_still_frames:', detector.min_still_frames)
                    print('      min_area:', detector.min_area, '(in percent)')
                    print('      min_area:', detector.min_area_pixels, '(in pixels)')
                    print('      blur_kernel_size:', detector.blur_kernel_size)
        print()

    def setup_sensors(self, settings):
        """ Create a list of sensors from the sensors section of the yaml file

        Typical sensors include temperature and humidity, but PIR motion
        detectors, light meters and other are possible

        Parameters:
            settings (Settings object): settings object created from YAML file
        """

        for sensor in settings.sensors:  # for each sensor listed in yaml file
            s = Sensor(sensor, settings.sensors, settings, self.tiny_image,
                        self.send_q)
            self.sensors.append(s)  # add it to the list of sensors

    def setup_lights(self, settings):
        """ Create a list of lights from the lights section of the yaml file

        Lights are controlled by the RPI GPIO pins. The light settings name
        each light and assign it a GPIO pin

        Parameters:
            settings (Settings object): settings object created from YAML file
        """

        for light in settings.lights:  # for each light listed in yaml file
            l = Light(light, settings.lights, settings)  # create a Light instance with settings
            self.lights.append(l)  # add it to the list of lights

    def setup_cameras(self, settings):
        """ Create a list of cameras from the cameras section of the yaml file

        Often, the list will contain a single PiCamera, but it could be a
        PiCamera with one or more webcams. Or one or more webcams with no
        PiCamera.

        Parameters:
            settings (Settings object): settings object created from YAML file
        """
        for camera in settings.cameras:  # for each camera listed in yaml file
            cam = Camera(camera, settings.cameras, settings)  # create a Camera instance
            self.camlist.append(cam)  # add it to the list of cameras

    def send_jpg_frame(self, text, image):
        """ Compresses image as jpg before sending

        Function self.send_frame() is set to this function if jpg option chosen
        """

        ret_code, jpg_buffer = cv2.imencode(
            ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY),
            self.jpeg_quality])
        hub_reply = self.sender.send_jpg(text, jpg_buffer)
        return hub_reply

    def send_image_frame(self, text, image):
        """ Sends image as unchanged OpenCV image; no compression

        Function self.send_frame() is set to this function if image option chosen
        """

        hub_reply = self.sender.send_image(text, image)
        return hub_reply

    def read_cameras(self):
        """ Read one image from each camera and run detectors.

        Perform vflip and image resizing if requested in YAML setttings file.
        Append transformed image to cam_q queue.
        """
        for camera in self.camlist:
            image = camera.cam.read()
            if camera.vflip:
                image = cv2.flip(image, -1)
            if camera.resize_width:
                image = imutils.resize(image, width=camera.width_pixels)
            camera.cam_q.append(image)
            for detector in camera.detectors:
                self.run_detector(camera, image, detector)

    def run_detector(self, camera, image, detector):
        """ run detector on newest image and detector queue; perform detection

        For each detector, add most recently acquired image to detector queue.
        Apply detector critera to detector queue of images to evaluate events.
        Append messages about events detected, if any, to send_q queue. Also,
        append any images relevant to a detected event to send_q queue.

        Parameters:
            camera (Camera object): current camera
            image (openCV image): most recently acquired camera image
            detector (Detector object): current detector to apply to image
                queue (e.g. motion)
        """

        if detector.draw_roi:
            cv2.rectangle(image,
                detector.top_left,
                detector.bottom_right,
                detector.draw_color,
                detector.draw_line_width)
        # detect state (light, etc.) and put images and events into send_q
        detector.detect_state(camera, image, self.send_q)

    def fix_comm_link(self):
        """ Evaluate, repair and restart communications link with hub.

        Restart link if possible, else restart program or reboot computer.
        """
        # TODO add some of the ongoing experiments to this code when
        #      have progressed in development and testing
        # Currently in testing:
        #     1. Just wait longer one time and try sending again:
        #        hub_reply = node.send_frame(text, image) # again
        #     2. Doing 1 repeatedly with exponential time increases
        #     3. Stopping and closing ZMQ context; restarting and sending
        #            last message
        #     4. Check WiFi ping; stop and restart WiFi service
        #     5. Reboot RPi; allow startup to restart imagenode.py
        #
        print('Fixing broken comm link...')
        print('....by ending the program.')
        raise KeyboardInterrupt
        return 'hub_reply'
        pass

    def process_hub_reply(self, hub_reply):
        """ Process hub reply if it is other than "OK".

        A hub reply is normally "OK", but could be "send 10 images" or
        "set resolution: (320, 240)". This method processes hub requests.
        This may involve sending a requested image sequence, changing a setting,
        or restarting the computer.
        """

        # Typical response from hub is "OK" if there are no user or
        #    automated librian requests. Almost all responses are just "OK"
        #    therefore the default process_hub_reply is "pass"
        # TODO Respond to hub repies if they are other than 'OK'
        # for example, push "send 10 frames" request onto deque
        #     and then add "do requested extra frames" to detectors loop
        #     so that images get sent even though there is no routine reason
        pass

    def closeall(self, settings):
        """ Close all resources, including cameras, lights, GPIO.

        Parameters:
            settings (Settings object): settings object created from YAML file
        """

        for camera in self.camlist:
            camera.cam.stop()
        for light in self.lights:
            light.turn_off()
        if settings.sensors or settings.lights:
            GPIO.cleanup()

class Sensor:
    """ Methods and attributes of a sensor, such as a temperature sensor

    Each sensor is setup and started using the settings in the yaml file.
    Includes methods for reading, and closing the sensor and GPIO pins.

    Parameters:
        sensor (text): dictionary key of current sensor being instantiated
        sensors (dict): dictionary of all the sensors in the YAML file
        settings (Settings object): settings object created from YAML file

    TODO Make imports of GPIO and W1ThermSensor conditional on actual need for
    them. For now, they are imported every time whether needed or not.

    TODO This is coded for a single DS18B20 temperature sensor. Add
    code for DHT22 sensors and for multiple DS18B20 sensors.
    """

    def __init__(self, sensor, sensors, settings, tiny_image, send_q):
        """ Initializes a specific sensor using settings in the YAML file.
        """

        self.tiny_image = tiny_image
        self.send_q = send_q
        if 'name' in sensors[sensor]:
            self.name = sensors[sensor]['name']
        else:
            self.name = sensor
        if 'gpio' in sensors[sensor]:
            self.gpio = sensors[sensor]['gpio']
        else:
            self.gpio = 4   # GPIO pin 4 is the default for testing
        if 'type' in sensors[sensor]:
            self.type = sensors[sensor]['type']
        else:
            self.type = 'Unknown'
        if 'read_interval_minutes' in sensors[sensor]:
            self.interval = sensors[sensor]['read_interval_minutes']
        else:
            self.interval = 10  # how often to read sensor in minutes
        if 'min_difference' in sensors[sensor]:
            self.min_difference = sensors[sensor]['min_difference']
        else:
            self.min_difference = 1  # minimum difference to count as reportable
        self.interval *= 60.0 # convert often to check sensor to seconds

        # self.event_text is the text message for this sensor that is
        #   sent when the sensor value changes
        # example: Barn|Temperaure|85 F
        # example: Garage|Temperature|71 F
        # example: Compost|Moisture|95 %
        # self.event_text will have self.current_reading appended when events are sent
        self.event_text = ' |'.join([settings.nodename, self.name])

        # TODO add other sensor types as testing is completed for each sensor type
        if self.type == 'DS18B20':
            self.temp_sensor = W1ThermSensor()
            self.last_reading = -999  # will ensure first reading is a change
            self.check_temperature() # check one time, then start interval_timer
            threading.Thread(
                target=lambda: interval_timer(
                    self.interval, self.check_temperature)).start()

    def check_temperature(self):
        """ adds temperature value from a sensor to senq_q message queue
        """
        temperature = int(self.temp_sensor.get_temperature(W1ThermSensor.DEGREES_F))
        if abs(temperature - self.last_reading) >= self.min_difference:
            # temperature has changed from last reported temperature, therefore
            # send an event message reporting temperature by appending to send_q
            temp_text = str(temperature) + " F"
            text = ' |'.join([self.event_text, temp_text])
            text_and_image = (text, self.tiny_image)
            self.send_q.append(text_and_image)
            self.last_reading = temperature

class Light:
    """ Methods and attributes of a light controlled by an RPi GPIO pin

    Each light is setup and started using the settings in the yaml file.
    Includes methods for turning the light on and off using the GPIO pins.

    Parameters:
        light (text): dictionary key of the current light being instantiated
        lights (dict): dictionary of all the lights in the YAML file
        settings (Settings object): settings object created from YAML file
    """

    def __init__(self, light, lights, settings):
        """ Initializes a specific light using settings in the YAML file.
        """

        if 'name' in lights[light]:
            self.name = lights[light]['name']
        else:
            self.name = light
        if 'gpio' in lights[light]:
            self.gpio = lights[light]['gpio']
        else:
            self.gpio = 18   # GPIO pin 18 is the default for testing
        if 'on' in lights[light]:
            self.on = lights[light]['on']
        else:
            self.on = 'continuous'

        GPIO.setup(self.gpio, GPIO.OUT)
        if self.on == 'continuous':
            self.turn_on()
        else:  # set up light on/off cyclying other than continuous
            pass  # for example, during certain hours

    def turn_on(self):
        """ Turns on the light using the GPIO pins
        """
        GPIO.output(self.gpio, True)  # turn on light

    def turn_off(self):
        """ Turns off the light using the GPIO pins
        """
        GPIO.output(self.gpio, False)  # turn off light

class Camera:
    """ Methods and attributes of a camera

    Each camera is setup and started using the settings in the yaml file.
    Includes setup of detectors, e.g., detector for motion

    Parameters:
        camera (text): dict key of current camera being instantiated
        cameras (dict): dictionary of all cameras named in YAML file
        settings (Settings object): settings object created from YAML file
    """

    def __init__(self, camera, cameras, settings):
        """ Initializes all the camera settings from settings in the YAML file.
        """

        self.cam = None
        self.jpeg_quality = 95  # 0 to 100, higher is better quality, 95 is cv2 default
        if 'resolution' in cameras[camera]:
            self.resolution = literal_eval(cameras[camera]['resolution'])
        else:
            self.resolution = (320, 240)
        if 'framerate' in cameras[camera]:
            self.framerate = cameras[camera]['framerate']
        else:
            self.framerate = 32
        if 'vflip' in cameras[camera]:
            self.vflip = cameras[camera]['vflip']
        else:
            self.vflip = False
        if 'resize_width' in cameras[camera]:
            # resize_width is a percentage value
            # width in pixels will be computed later after reading a test image
            self.resize_width = cameras[camera]['resize_width']
        else:
            self.resize_width = None
        if 'viewname' in cameras[camera]:
            self.viewname = cameras[camera]['viewname']
        else:
            self.viewname = ' '
        if 'src' in cameras[camera]:
            self.src = cameras[camera]['src']
        else:
            self.src = 0
        self.detectors = []
        if 'detectors' in cameras[camera]:  # is there at least one detector
            self.setup_detectors(cameras[camera]['detectors'],
            settings.nodename, self.viewname)

        if camera[0].lower() == 'p':  # this is a picam
            # start PiCamera and warm up; inherits methods from VideoStream
            self.cam = VideoStream(usePiCamera=True,
                resolution=self.resolution,
                framerate=self.framerate).start()
            self.cam_type = 'PiCamera'
        else:  # this is a webcam (not a picam)
            self.cam = VideoStream(src=0).start()
            self.cam_type = 'webcam'
        sleep(2.0)  # allow camera sensor to warm up

        # self.text is the text label for images from this camera.
        # Each image that is sent is sent with a text label so the hub can
        # file them by nodename, viewname, and send_type
        # example: JeffOffice Window|jpg
        # Nodename and View name are in one field, separated by a space.
        # send_type is in the next field
        # The 2 field names are separaged by the | character
        node_and_view = ' '.join([settings.nodename, self.viewname])
        self.text = ' |'.join([node_and_view, settings.send_type])

        # set up camera image queue
        self.cam_q = deque(maxlen=settings.queuemax)

    def setup_detectors(self, detectors, nodename, viewname):
        """ Create a list of detectors for this camera

        Parameters:
            detectors (dict): detectors for this camera from YAML file
            nodename (str): nodename to identify event messages and images sent
            viewnane (str): viewname to identify event messages and images sent
        """

        for detector in detectors:  # for each camera listed in yaml file
            det = Detector(detector, detectors, nodename, viewname)  # create a Detector instance
            self.detectors.append(det)  # add to list of detectors for this camera

class Detector:
    """ Methods and attributes of a detector for motion, light, etc.

    Each detector is setup with ROI tuples and various parameters.
    Detector options that are common to all detectors are set up here.
    Detector options that are specific to individual detector types (like
    'light', are set up in detector specific sections here).

    Parameters:
        detector (text): dict key for a specific detector for this camera
        detectors (dict): dictionary of all detectors for this camera
        nodename (str): nodename to identify event messages and images sent
        viewnane (str): viewname to identify event messages and images sent
    """

    def __init__(self, detector, detectors, nodename, viewname):
        """ Initializes all the detector using settings from the YAML file.
        """

        self.detector_type = detector
        # set detect_state function to detector_type (e.g., light or motion)
        if detector == 'light':
            self.detect_state = self.detect_light
            if 'threshold' in detectors[detector]:
                self.threshold = detectors[detector]['threshold']
            else:
                self.threshold = 100  # 100 is a default for testing
            if 'min_frames' in detectors[detector]:
                self.min_frames = detectors[detector]['min_frames']
            else:
                self.min_frames = 5  # 5 is default
            # need to remember min_frames of state history to calculate state
            self.state_history_q  = deque(maxlen=self.min_frames)

        elif detector == 'motion':
            self.detect_state = self.detect_motion
            self.moving_frames = 0
            self.still_frames = 0
            self.total_frames = 0
            if 'delta_threshold' in detectors[detector]:
                self.delta_threshold = detectors[detector]['delta_threshold']
            else:
                self.delta_threshold = 5  # 5 is a default for testing
            if 'min_area' in detectors[detector]:
                self.min_area = detectors[detector]['min_area']
            else:
                self.min_area = 3 # 3 is default percent of ROI
            if 'min_motion_frames' in detectors[detector]:
                self.min_motion_frames = detectors[detector]['min_motion_frames']
            else:
                self.min_motion_frames = 3 # 3 is default
            if 'min_still_frames' in detectors[detector]:
                self.min_still_frames = detectors[detector]['min_still_frames']
            else:
                self.min_still_frames = 3 # 3 is default
            self.min_frames = max(self.min_motion_frames, self.min_still_frames)
            if 'blur_kernel_size' in detectors[detector]:
                self.blur_kernel_size = detectors[detector]['blur_kernel_size']
            else:
                self.blur_kernel_size = 15 # 15 is default blur_kernel_size

        if 'ROI' in detectors[detector]:
            self.roi_pct = literal_eval(detectors[detector]['ROI'])
        else:
            self.roi_pct = ((0,0),(100,100))
        if 'draw_roi' in detectors[detector]:
            self.draw_roi = literal_eval(detectors[detector]['draw_roi'])
            self.draw_color = self.draw_roi[0]
            self.draw_line_width = self.draw_roi[1]
        else:
            self.draw_roi = None
        send_frames = 'None Set'
        self.frame_count = 0
        # send_frames option can be 'continuous', 'detected event', 'none'
        if 'send_frames' in detectors[detector]:
            send_frames = detectors[detector]['send_frames']
            if not send_frames:  # None was specified; send 0 frames
                self.frame_count = 0
            if 'detect' in send_frames:
                self.frame_count = 10  # detected events default; adjusted later
            elif 'continuous' in send_frames:
                self.frame_count = -1  # send continuous flag
            elif 'none' in send_frames:  # don't send any frames
                self.frame_count = 0
        else:
            self.frame_count = -1  # send continuous flag
        # send_count option is an integer of how many frames to send if event
        if 'send_count' in detectors[detector]:
            self.send_count = detectors[detector]['send_count']
        else:
            self.send_count = 5  # default number of frames to send per event
        # send_test_images option: if True, send test images like ROI, Gray
        if 'send_test_images' in detectors[detector]:
            self.send_test_images = detectors[detector]['send_test_images']
        else:
            self.send_test_images = False  # default is NOT to send test images

        # self.event_text is the text message for this detector that is
        # sent when the detector state changes
        # example: JeffOffice Window|light|dark
        # example: JeffOffice Window|light|lighted
        # self.event_text will have self.current_state appended when events are sent
        node_and_view = ' '.join([nodename, viewname])
        self.event_text = ' |'.join([node_and_view, self.detector_type])

        # An event is a change of state (e.g., 'dark' to 'lighted')
        # Every detector is instantiated with all states = 'unknown'
        self.current_state = 'unknown'
        self.last_state = 'unknown'

        self.msg_image = np.zeros((2,2), dtype="uint8")  # blank image tiny
        if self.send_test_images:
            # set the blank image wide enough to hold message of send_test_images
            self.msg_image = np.zeros((5,320), dtype="uint8")  # blank image wide

    def detect_state(self, camera, image, send_q):
        """ Placeholder function will be set to specific detection function

        For example, detect_state() will be set to detect_light() during
        detector.__init__()
        """
        print('Therefore, should never get to this print statement')
        pass

    def detect_light(self, camera, image, send_q):
        """ Detect if ROI is 'lighted' or 'dark'; send event message and images

        After adding current image to 'event state' history queue, detect if the
        ROI state has changed (e.g., has state changed to 'lighted' from 'dark'.)

        If the state has changed, send an event message and the event images.
        (However, if send_frames option is 'continuous', images have already
        been sent, so there is no need to send the event images.)

        If state has not changed, just store the image state into 'event state'
        history queue for later comparison and return.

        Parameters:
            camera (Camera object): current camera
            image (OpenCV image): current image
            send_q (Deque): where (text, image) tuples are appended to be sent
        """

        # if we are sending images continuously, append current image to send_q
        if self.frame_count == -1:  # -1 code to send all frames continuously
            text_and_image = (camera.text, image)
            send_q.append(text_and_image)

        # crop ROI & convert to grayscale
        x1, y1 = self.top_left
        x2, y2 = self.bottom_right
        ROI = image[y1:y2, x1:x2]
        gray = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
        # calculate current_state of ROI
        gray_mean = int(np.mean(gray))
        if gray_mean > self.threshold:
            state = 'lighted'
            state_num = 1
        else:
            state = 'dark'
            state_num = -1
        if self.send_test_images:
            images = []
            images.append(('ROI', ROI,))
            images.append(('Grayscale', gray,))
            state_values =[]
            state_values.append(('State', state,))
            state_values.append(('Mean Pixel Value', str(gray_mean),))
            self.send_test_data(images, state_values, send_q)
        self.state_history_q.append(state_num)
        if len(self.state_history_q) < self.min_frames:
            return  # not enough history to check for a state change

        # have enough history now, so...
        #   determine if there has been a change in state
        if self.state_history_q.count(-1) == self.min_frames:
            self.current_state = 'dark'
        elif self.state_history_q.count(1) == self.min_frames:
            self.current_state = 'lighted'
        else:
            return  # state has not stayed the same for self.min_frames
        if self.current_state == self.last_state:
            return  # there has been no state change and hence no event yet

        # state has changed from last reported state, therefore
        # send event message, reporting current_state, by appending it to send_q
        text = ' |'.join([self.event_text, self.current_state])
        text_and_image = (text, self.msg_image)
        send_q.append(text_and_image)

        # if frame_count = -1, then already sending images continuously...
        #   so no need to send the images of this detected event
        # if frame_count > 0, need to send send_count images from the cam_q
        #   by appending them to send_q
        if self.frame_count > 0:  # then need to send images of this event
            send_count = min(len(camera.cam_q), self.send_count)
            for i in range(-send_count,-1):
                text_and_image = (camera.text, camera.cam_q[i])
                send_q.append(text_and_image)

        # Now that current state has been sent, it becomes the last_state
        self.last_state = self.current_state

    def detect_motion(self, camera, image, send_q):
        """ Detect if ROI is 'moving' or 'still'; send event message and images

        After adding current image to 'event state' history queue, detect if the
        ROI state has changed (e.g., has state changed to 'moving' from 'still'.)

        If the state has changed, send an event message and the event images.
        (However, if send_frames option is 'continuous', images have already
        been sent, so there is no need to send the event images.)

        If state has not changed, just store the image into 'event state'
        history queue for later comparison and return.

        Parameters:
            camera (Camera object): current camera
            image (OpenCV image): current image
            send_q (Deque): where (text, image) tuples are appended to be sent

        This function borrowed a lot from a motion detector tutorial post by
        Adrian Rosebrock on PyImageSearch.com. See README.rst for details.
        """

        # if we are sending images continuously, append current image to send_q
        if self.frame_count == -1:  # -1 code ==> send all frames continuously
            text_and_image = (camera.text, image)
            send_q.append(text_and_image)  # send current image

        # crop ROI & convert to grayscale & apply GaussianBlur
        x1, y1 = self.top_left
        x2, y2 = self.bottom_right
        ROI = image[y1:y2, x1:x2]
        gray = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray,
                        (self.blur_kernel_size, self.blur_kernel_size), 0)

        # If no history yet, save the first image as the  average image
        if self.total_frames < 1:
            self.average = gray.copy().astype('float')
        else:
            # add gray image to weighted average image
            cv2.accumulateWeighted(gray, self.average, 0.5)
        # frame delta is the absolute difference between gray and self.average
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.average))
    	# threshold the frame delta image and dilate the thresholded image
        thresholded = cv2.threshold(frameDelta, self.delta_threshold,
                                    255,cv2.THRESH_BINARY)[1]
        thresholded = cv2.dilate(thresholded, None, iterations=2)
        # find contours in thresholded image
        (_, contours, __) = cv2.findContours(thresholded.copy(),
                            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        state = 'still'
        area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area_pixels:
                continue
            state = 'moving'
        if state == 'moving':
            self.moving_frames += 1
        else:
            self.moving_frames = 0
            self.still_frames += 1
        # Optionally, send various test images to visually tune settings
        if self.send_test_images:  # send some intermediate test images
            images = []
            images.append(('ROI', ROI,))
            images.append(('Grayscale', gray,))
            images.append(('frameDelta', frameDelta,))
            images.append(('thresholded', thresholded,))
            state_values =[]
            state_values.append(('State', self.current_state,))
            state_values.append(('N Contours', str(len(contours)),))
            state_values.append(('Area', str(area),))
            self.send_test_data(images, state_values, send_q)
        else:
            sleep(0.02)  # for testing
            pass

        self.total_frames += 1
        if self.total_frames < self.min_frames:
            return  # not enough history to check for a state change

        # have enough history now, so...
        #   determine if there has been a change in state
        if self.moving_frames >= self.min_motion_frames:
            self.current_state = 'moving'
            self.still_frames = 0
        elif self.still_frames >= self.min_still_frames:
            self.current_state = 'still'
        else:
            return  # not enought frames of either state; return for more
        if self.current_state == self.last_state:
            return  # there has been no state change and hence no event yet

        # state has changed from last reported state, so...
        # send event message reporting current_state by appending it to send_q
        text = ' |'.join([self.event_text, self.current_state])
        text_and_image = (text, self.msg_image)
        send_q.append(text_and_image)

        # if frame_count = -1, then already sending images continuously...
        #   so no need to send the images of this detected event
        # if frame_count > 0, need to send send_count images from the cam_q
        #   by appending them to send_q
        if self.frame_count > 0:  # then need to send images of this event
            send_count = min(len(camera.cam_q), self.send_count)
            for i in range(-send_count,-1):
                text_and_image = (camera.text, camera.cam_q[i])
                send_q.append(text_and_image)

        # Now that current state has been sent, it becomes the last_state
        self.last_state = self.current_state

    def send_test_data(self, images, state_values, send_q):
        """ Sends various test data, images, computed state values via send_q

        Used for testing, this function takes a set of images and computed
        values such as number of contours, averge light intensity value,
        and computed state, such as "moving" and "still" and puts these values
        into small images that can be displayed in a simple test hub for
        tuning the settings parameters of a detector.

        Parameters:
            images (list): test images to send for display, e.g., ROI, grayscale
            state_values (list): the name and value of tuning parameters, such
                as state, area, N_contours, Mean Pixel Value, etc.
        """
        for text_and_image in images:
            send_q.append(text_and_image)
        font = cv2.FONT_HERSHEY_SIMPLEX
        for text_and_value in state_values:
            text, value = text_and_value
            state_image = np.zeros((50,200), dtype="uint8")  # blank image
            cv2.putText(state_image,value,(10,35), font,
                        1,(255,255,255),2,cv2.LINE_AA)
            text_and_image = (text, state_image)
            send_q.append(text_and_image)

class Settings:
    """Load settings from YAML file

    Note that there is currently almost NO error checking for the YAML
    settings file. Therefore, by design, an exception will be raised
    when a required setting is missing or misspelled in the YAML file.
    This stops the program with a Traceback which will indicate which
    setting below caused the error. Reading the Traceback will indicate
    which line below caused the error. Fix the YAML file and rerun the
    program until the YAML settings file is read correctly.

    There is a "print_settings" option that can be set to TRUE to print
    the dictionary that results from reading the YAML file. Note that the
    order of the items in the dictionary will not necessarily be the order
    of the items in the YAML file (this is a property of Python dictionaries).
    """

    def __init__(self):
        userdir = os.path.expanduser("~")
        with open(os.path.join(userdir,"imagenode.yaml")) as f:
            self.config = yaml.safe_load(f)
        self.print_node = False
        if 'node' in self.config:
            if 'print_settings' in self.config['node']:
                if self.config['node']['print_settings']:
                    self.print_settings()
                    self.print_node = True
                else:
                    self.print_node = False
        else:
            self.print_settings('"node" is a required settings section but not present.')
            raise KeyboardInterrupt
        if 'hub_address' in self.config:
            self.hub_address = self.config['hub_address']['H1']
            # TODO add read and store H2 and H3 hub addresses
        else:
            self.print_settings('"hub_address" is a required settings section but not present.')
            raise KeyboardInterrupt

        if 'name' in self.config['node']:
            self.nodename = self.config['node']['name']
        else:
            self.print_settings('"name" is a required setting in the "node" section but not present.')
            raise KeyboardInterrupt
        if 'patience' in self.config['node']:
            self.patience = self.config['node']['patience']
        else:
            self.patience = 10  # default is to wait 10 seconds for hub reply
        if 'queuemax' in self.config['node']:
            self.queuemax = self.config['node']['queuemax']
        else:
            self.queuemax = 50
        if 'heartbeat' in self.config['node']:
            self.heartbeat = self.config['node']['heartbeat']
        else:
            self.heartbeat = 0
        if 'send_type' in self.config['node']:
            self.send_type = self.config['node']['send_type']
        else:
            self.send_type = 'jpg'  # default send type is jpg
        if 'cameras' in self.config:
            self.cameras = self.config['cameras']
        else:
            self.cameras = None
        if 'sensors' in self.config:
            self.sensors = self.config['sensors']
        else:
            self.sensors = None
        if 'lights' in self.config:
            self.lights = self.config['lights']
        else:
            self.lights = None

    def print_settings(self, title=None):
        """ prints the settings in the yaml file using pprint()
        """
        if title:
            print(title)
        print('Contents of imagenode.yaml:')
        pprint.pprint(self.config)
        print()
