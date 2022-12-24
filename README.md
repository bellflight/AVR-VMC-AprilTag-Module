# AVR-VMC-AprilTag-Module

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The AprilTag module is responsible for using the images pulled from the C
SI camera to scan for visible AprilTags.

A low-level C++ program captures the images and hands them off to the
Jetson’s GPU for processing and publishes the raw detections to the
"avr/apriltags/raw" topic.

From here, a second Python program inside the module subscribes to this topic,
and upon new detections, uses linear algebra to perform a coordinate
transformation in order to get several pieces of data. These detections
include the tags ID, as well as the drone’s absolute location in the court
(pos_world), and the drones relative location to the tag itself (pos_rel).

This data is then broadcast out over MQTT for other modules,
such as the Fusion and Sandbox modules to consume.

This is the only module with C++ code, for performance reasons.

## Developer Notes

`/tmp/argus_socket` needs to be bind-mounted into the container.

### Windows Development

If you have trouble installing the `pupil-apriltags` package on Windows,
try installing
[https://aka.ms/vs/15/release/vs_buildtools.exe](https://aka.ms/vs/15/release/vs_buildtools.exe)
or the `visualstudio2017buildtools` Chocolately package.
You may need to add the VS 2017 Desktop Development C++ tools.
