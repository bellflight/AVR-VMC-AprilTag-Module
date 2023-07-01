from typing import Literal, Optional

import cv2
from bell.avr.utils.decorators import run_forever
from loguru import logger


class CaptureDevice:
    def __init__(
        self,
        protocol: Literal["v4l2", "argus"],
        video_device: str,
        res: tuple[int, int],
        framerate: Optional[int] = None,
    ):  # sourcery skip: introduce-default-else
        video_format = "BGR"
        if protocol == "v4l2":
            video_format = "BGRx"

        # if the framerate argument is supplied, we will modify the connection
        # string to provide a rate limiter to the incoming string at virtually
        # no performance penalty
        if framerate is None:
            frame_string = f"video/x-raw,format={video_format}"
        else:
            frame_string = (
                f"videorate ! video/x-raw,format={video_format},framerate={framerate}/1"
            )

        if protocol == "v4l2":
            # this is the inefficient way of capturing, using the software decoder running on CPU
            connection_string = f"v4l2src device={video_device} io-mode=2 ! image/jpeg,width=1280,height=720,framerate=60/1 ! jpegparse ! nvv4l2decoder mjpeg=1 ! nvvidconv ! {frame_string} ! videoconvert ! video/x-raw,width={res[0]},height={res[1]},format=BGRx ! appsink"

        elif protocol == "argus":
            # this is the efficient way of capturing, leveraging the hardware
            # JPEG decoder on the jetson
            connection_string = f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720,format=NV12, framerate=60/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! {frame_string},width={res[0]},height={res[1]} ! appsink"

        else:
            raise ValueError(f"Unknown protocol: {protocol}")

        # create the gstreamer pipeline
        self.cv = cv2.VideoCapture(connection_string)

    def read(self) -> tuple[bool, Optional[cv2.Mat]]:
        return self.cv.read()

    def read_gray(self) -> tuple[bool, Optional[cv2.Mat]]:
        ret, img = self.cv.read()
        if ret:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return ret, img

    @run_forever(frequency=100)
    def run(self) -> None:
        # try to read frame
        ret, _ = self.read()

        if not ret:
            logger.warning("cv2.VideoCapture read failed")


if __name__ == "__main__":
    cam = CaptureDevice(
        protocol="argus", video_device="/dev/video0", res=(1280, 720), framerate=30
    )
    cam.run()
