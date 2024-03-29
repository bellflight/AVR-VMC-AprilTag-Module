from __future__ import annotations

import math
import sys
from typing import TYPE_CHECKING

import pytest
from bell.avr.utils.testing import dont_run_forever
from pytest_mock.plugin import MockerFixture

if TYPE_CHECKING:
    from src.python.apriltag_processor import AprilTagModule


@pytest.fixture
def config(mocker: MockerFixture) -> None:
    # make these constant
    sys.path.append("src.python")

    mocker.patch("src.python.config.CAM_POS", [15, 10, 10])
    mocker.patch("src.python.config.CAM_ATTITUDE", [0, 0, math.pi / 2])
    mocker.patch(
        "src.python.config.TAG_TRUTH", {0: {"rpy": (0, 0, 0), "xyz": (0, 0, 0)}}
    )


@pytest.fixture
def apriltag_module(config: None, mocker: MockerFixture) -> AprilTagModule:
    # patch the run_forever decorator
    mocker.patch("bell.avr.utils.decorators.run_forever", dont_run_forever)

    # patch the send message function
    from src.python.apriltag_processor import AprilTagModule

    mocker.patch.object(AprilTagModule, "send_message")

    # create module object
    return AprilTagModule()
