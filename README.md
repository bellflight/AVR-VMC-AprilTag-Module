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

## Development

It's assumed you have a version of Python installed from
[python.org](https://python.org) that is the same or newer as
defined in the [`Dockerfile`](Dockerfile).

First, install [Poetry](https://python-poetry.org/) and
[VS Code Task Runner](https://pypi.org/project/vscode-task-runner/):

```bash
python -m pip install pipx --upgrade
pipx ensurepath
pipx install poetry
pipx install vscode-task-runner
# (Optionally) Add pre-commit plugin
poetry self add poetry-pre-commit-plugin
```

Now, you can clone the repo and install dependencies:

```bash
git clone https://github.com/bellflight/AVR-VMC-AprilTag-Module
cd AVR-VMC-AprilTag-Module
vtr install
```

Run

```bash
poetry shell
```

to activate the virtual environment.

### Windows Development

If you have trouble installing the `pupil-apriltags` package on Windows,
try installing
[https://aka.ms/vs/15/release/vs_buildtools.exe](https://aka.ms/vs/15/release/vs_buildtools.exe)
or the `visualstudio2017buildtools` Chocolately package.
You may need to add the VS 2017 Desktop Development C++ tools.

### Notes

`/tmp/argus_socket` needs to be bind-mounted into the container.
