==========================================
imagenode Research and Development Roadmap
==========================================

.. contents::

Overview
========

**imagenode** is constantly evolving. It is a "science project" that is part of
a larger system to observe, monitor and optimize a small permaculture farm. It
is part of a distributed computer vision and sensor network. Here is where I
keep the list of the stuff I'm experimenting with but haven't pushed to GitHub
yet. Feel free to open an issue and make suggestions or start a discussion
about a potential change or new feature. The list below is not in any particular
order; all of these are ongoing experiments on differing timelines

Receive and act on commands or requests from imagehub
-----------------------------------------------------
Right now, the imagehub returns "OK" after every message tuple is sent. The
imagehub reply can be a "command word" instead that would cause imaghub to take
an action such as change the exposure_mode of the PiCamera. Or send a dozen
"live frames" from the camera (even though no detector has activated). Command
words look like this:
- OK  # that is the only one now and is sent back for every reply
- ReloadYaml  # reload the yaml file to get a change in one of the options.
- SendFrames 10  # Send some frames now, even if no detector is activated.

Add an option to send message tuples (text, image) in a thread
--------------------------------------------------------------
Currently, all message tuples are sent in main event loop. Performance may be
better (better speed, etc.) by putting the send message function in a separate
thread. Early experiments show an increase in FPS speed.

`Return to main documentation page README.rst <../README.rst>`_
