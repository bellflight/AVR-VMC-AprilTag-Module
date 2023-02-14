from pytest_mock.plugin import MockerFixture
from typing import Optional, Literal
from src.python.capture_device import CaptureDevice
import pytest


@pytest.mark.parametrize(
    "protocol, framerate, connection_string",
    [
        (
            "v4l2",
            "60",
            "v4l2src device=/dev/test io-mode=2 ! image/jpeg,width=1280,height=720,framerate=60/1 ! jpegparse ! nvv4l2decoder mjpeg=1 ! nvvidconv ! videorate ! video/x-raw,format=BGRx,framerate=60/1 ! videoconvert ! video/x-raw,width=25,height=35,format=BGRx ! appsink",
        ),
        (
            "v4l2",
            None,
            "v4l2src device=/dev/test io-mode=2 ! image/jpeg,width=1280,height=720,framerate=60/1 ! jpegparse ! nvv4l2decoder mjpeg=1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,width=25,height=35,format=BGRx ! appsink",
        ),
        (
            "argus",
            "60",
            "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720,format=NV12, framerate=60/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! videorate ! video/x-raw,format=BGR,framerate=60/1,width=25,height=35 ! appsink",
        ),
        (
            "argus",
            None,
            "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720,format=NV12, framerate=60/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR,width=25,height=35 ! appsink",
        ),
    ],
)
def test_init(
    mocker: MockerFixture,
    protocol: Literal["v4l2", "argus"],
    framerate: Optional[int],
    connection_string: str,
) -> None:
    # this is certainly not a *good* test, but it helps prevent accidents

    mocker.patch("cv2.VideoCapture")

    CaptureDevice(
        protocol=protocol, framerate=framerate, video_device="/dev/test", res=(25, 35)
    )

    import cv2

    cv2.VideoCapture.assert_called_once_with(connection_string)
