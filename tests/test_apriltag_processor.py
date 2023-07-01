from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import numpy as np
import pytest
from bell.avr.mqtt.payloads import (
    AVRAprilTagsRaw,
    AVRAprilTagsRawApriltags,
    AVRAprilTagsVehiclePosition,
    AVRAprilTagsVisible,
    AVRAprilTagsVisibleApriltags,
    AVRAprilTagsVisibleApriltagsAbsolutePosition,
    AVRAprilTagsVisibleApriltagsRelativePosition,
)
from nptyping import Float, NDArray, Shape

if TYPE_CHECKING:
    from src.python.apriltag_processor import AprilTagModule


def test_setup_transforms(apriltag_module: AprilTagModule) -> None:
    expected = {
        "H_aeroBody_cam": np.array(
            [
                [6.123234e-17, 1.000000e00, 0.000000e00, -1.000000e01],
                [-1.000000e00, 6.123234e-17, -0.000000e00, 1.500000e01],
                [0.000000e00, 0.000000e00, 1.000000e00, -1.000000e01],
                [0.000000e00, 0.000000e00, 0.000000e00, 1.000000e00],
            ]
        ),
        "H_tag_0_aeroRef": np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        ),
        "H_tag_0_cam": np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        ),
    }

    apriltag_module.setup_transforms()
    for k, v in expected.items():
        assert np.allclose(apriltag_module.tm[k], v)


@pytest.mark.parametrize(
    "payload, expected_visible, expected_selected",
    [
        (
            AVRAprilTagsRaw(
                apriltags=[
                    AVRAprilTagsRawApriltags(
                        tag_id=0,
                        x=1,
                        y=2,
                        z=3,
                        rotation=((-1, 0, 1), (0, 1, -1), (1, -1, 0)),
                    )
                ]
            ),
            AVRAprilTagsVisible(
                apriltags=[
                    AVRAprilTagsVisibleApriltags(
                        tag_id=0,
                        horizontal_distance=215.23243250030882,
                        vertical_distance=310.0,
                        angle=59.264512298079914,
                        hdg=90.00000000000001,
                        relative_position=AVRAprilTagsVisibleApriltagsRelativePosition(
                            x=109.99999999999997, y=185.0, z=-310.0
                        ),
                        absolute_position=AVRAprilTagsVisibleApriltagsAbsolutePosition(
                            x=109.99999999999997, y=185.0, z=-310.0
                        ),
                    )
                ]
            ),
            AVRAprilTagsVehiclePosition(
                tag_id=0, x=109.99999999999997, y=185.0, z=-310.0, hdg=90.00000000000001
            ),
        ),
        (
            AVRAprilTagsRaw(
                apriltags=[
                    AVRAprilTagsRawApriltags(
                        tag_id=2,
                        x=1,
                        y=2,
                        z=3,
                        rotation=((-1, 0, 1), (0, 1, -1), (1, -1, 0)),
                    )
                ]
            ),
            AVRAprilTagsVisible(
                apriltags=[
                    AVRAprilTagsVisibleApriltags(
                        tag_id=2,
                        horizontal_distance=215.23243250030882,
                        vertical_distance=310.0,
                        angle=59.264512298079914,
                        hdg=90.00000000000001,
                        relative_position=AVRAprilTagsVisibleApriltagsRelativePosition(
                            x=109.99999999999997, y=185.0, z=-310.0
                        ),
                        absolute_position=None,
                    )
                ]
            ),
            None,
        ),
    ],
)
def test_on_apriltag_message(
    apriltag_module: AprilTagModule,
    payload: AVRAprilTagsRaw,
    expected_visible: AVRAprilTagsVisible,
    expected_selected: Optional[AVRAprilTagsVehiclePosition],
) -> None:
    apriltag_module.on_apriltag_message(payload)

    apriltag_module.send_message.assert_any_call(
        "avr/apriltags/visible", expected_visible
    )

    if expected_selected is not None:
        apriltag_module.send_message.assert_any_call(
            "avr/apriltags/vehicle_position", expected_selected
        )


@pytest.mark.parametrize(
    "pos, expected", [((1, 2, 3), 63.43494882292201), ((5, 6, 7), 50.19442890773481)]
)
def test_angle_to_tag(
    apriltag_module: AprilTagModule, pos: tuple[float, float, float], expected: float
) -> None:
    assert pytest.approx(apriltag_module.angle_to_tag(pos)) == expected


@pytest.mark.parametrize(
    "tag_id, pos, expected",
    [
        (0, (1, 2, 3), 243.43494882292202),
        (0, (5, 6, 7), 230.1944289077348),
        (0, (-1, 20, 45), 272.8624052261117),
        (5, (0, 0, 0), None),
    ],
)
def test_world_angle_to_tag(
    apriltag_module: AprilTagModule,
    tag_id: int,
    pos: tuple[float, float, float],
    expected: Optional[float],
) -> None:
    assert pytest.approx(apriltag_module.world_angle_to_tag(pos, tag_id)) == expected


@pytest.mark.parametrize(
    "H, expected",
    [
        (
            np.array(
                [
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            ),
            np.array(
                [
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            ),
        ),
        (
            np.array(
                [
                    [1.0, 2.0, 3.0, 4.0],
                    [5.0, 6.0, 7.0, 8.0],
                    [9.0, 10.0, 11.0, 12.0],
                    [13.0, 14.0, 15.0, 16.0],
                ]
            ),
            np.array(
                [
                    [0.09667365, 0.48336824, 0.87006284, -14.69439463],
                    [0.90773759, 0.31573482, -0.27626796, -2.84161334],
                    [-0.9166199, -0.34045882, 0.20951312, 3.87599273],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            ),
        ),
    ],
)
def test_H_inv(
    apriltag_module: AprilTagModule,
    H: NDArray[Shape["4, 4"], Float],
    expected: NDArray[Shape["4, 4"], Float],
) -> None:
    assert np.allclose(apriltag_module.H_inv(H), expected)


@pytest.mark.parametrize(
    "tag, expected",
    [
        (
            AVRAprilTagsRawApriltags(
                tag_id=0,
                x=1,
                y=2,
                z=3,
                rotation=((-1, 0, 1), (0, 1, -1), (1, -1, 0)),
            ),
            (
                0,
                pytest.approx(215.23243250030885),
                310.0,
                pytest.approx(59.264512298079914),
                np.array([-215.20026451, 3.72104204, -310.0]),
                pytest.approx((110.0, 185.0, -310.0)),
                pytest.approx(90.0),
            ),
        ),
        (
            AVRAprilTagsRawApriltags(
                tag_id=2,
                x=1,
                y=2,
                z=3,
                rotation=((-1, 0, 1), (0, 1, -1), (1, -1, 0)),
            ),
            (
                2,
                pytest.approx(215.23243250030885),
                310.0,
                pytest.approx(59.264512298079914),
                None,
                pytest.approx((110.0, 185.0, -310.0)),
                pytest.approx(90.0),
            ),
        ),
    ],
)
def test_handle_tag(
    apriltag_module: AprilTagModule, tag: AVRAprilTagsRawApriltags, expected: tuple
) -> None:
    result = apriltag_module.handle_tag(tag)
    for r_i, ex_i in zip(result, expected):
        if isinstance(ex_i, np.ndarray):
            np.allclose(r_i, ex_i)  # type: ignore
        else:
            assert r_i == ex_i
