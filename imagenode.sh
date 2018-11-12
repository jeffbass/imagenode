#!/bin/bash

# imagenode.sh: a way to start imagenode.py at startup
#   needs to be adapted to use with cron, screen, or systemctl service
source $(which virtualenvwrapper.sh)
workon py3cv3  # replace with your virtualenv name
cd /home/pi/imagenode/imagenode  # on RPi; change for Mac or Linux
nohup python imagenode.py </dev/null >imagenode.stdout 2>&1 &
