from __future__ import annotations

import numpy as np
from typing import TYPE_CHECKING, Tuple, Optional
import pytest
from nptyping import Float, NDArray, Shape
from bell.avr.mqtt.payloads import (
    AvrApriltagsRawPayload,
    AvrApriltagsSelectedPayload,
    AvrApriltagsVisiblePayload,
    AvrApriltagsRawTags,
    AvrApriltagsRawTagsPos,
    AvrApriltagsSelectedPos,
    AvrApriltagsVisibleTags,
    AvrApriltagsVisibleTagsPosRel,
    AvrApriltagsVisibleTagsPosWorld,
)

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
            AvrApriltagsRawPayload(
                tags=[
                    AvrApriltagsRawTags(
                        id=0,
                        pos=AvrApriltagsRawTagsPos(x=1, y=2, z=3),
                        rotation=((4, 5, 6), (7, 8, 9), (10, 11, 12)),
                    )
                ]
            ),
            AvrApriltagsVisiblePayload(
                tags=[
                    AvrApriltagsVisibleTags(
                        id=0,
                        horizontal_dist=215.23243250030885,
                        vertical_dist=310.0,
                        angle_to_tag=179.00939359502212,
                        heading=209.7448812969422,
                        pos_rel=AvrApriltagsVisibleTagsPosRel(
                            x=-215.20026451227668, y=3.721042037676277, z=-310.0
                        ),
                        pos_world=AvrApriltagsVisibleTagsPosWorld(
                            x=-215.20026451227668, y=3.721042037676277, z=-310.0
                        ),
                    )
                ]
            ),
            AvrApriltagsSelectedPayload(
                heading=209.7448812969422,
                pos=AvrApriltagsSelectedPos(
                    n=-215.20026451227668, e=3.721042037676277, d=-310.0
                ),
                tag_id=0,
            ),
        ),
        (
            AvrApriltagsRawPayload(
                tags=[
                    AvrApriltagsRawTags(
                        id=2,
                        pos=AvrApriltagsRawTagsPos(x=1, y=2, z=3),
                        rotation=((4, 5, 6), (7, 8, 9), (10, 11, 12)),
                    )
                ]
            ),
            AvrApriltagsVisiblePayload(
                tags=[
                    AvrApriltagsVisibleTags(
                        id=2,
                        horizontal_dist=215.23243250030885,
                        vertical_dist=310.0,
                        angle_to_tag=179.00939359502212,
                        heading=209.7448812969422,
                        pos_rel=AvrApriltagsVisibleTagsPosRel(
                            x=-215.20026451227668, y=3.721042037676277, z=-310.0
                        ),
                        pos_world=AvrApriltagsVisibleTagsPosWorld(
                            x=None, y=None, z=None
                        ),
                    )
                ]
            ),
            None,
        ),
    ],
)
def test_on_apriltag_message(
    apriltag_module: AprilTagModule,
    payload: AvrApriltagsRawPayload,
    expected_visible: AvrApriltagsVisiblePayload,
    expected_selected: Optional[AvrApriltagsSelectedPayload],
) -> None:
    apriltag_module.on_apriltag_message(payload)
    apriltag_module.send_message.assert_any_call(
        "avr/apriltags/visible", expected_visible
    )

    if expected_selected is not None:
        apriltag_module.send_message.assert_any_call(
            "avr/apriltags/selected", expected_selected
        )


@pytest.mark.parametrize(
    "pos, expected", [((1, 2, 3), 63.43494882292201), ((5, 6, 7), 50.19442890773481)]
)
def test_angle_to_tag(
    apriltag_module: AprilTagModule, pos: Tuple[float, float, float], expected: float
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
    pos: Tuple[float, float, float],
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
            AvrApriltagsRawTags(
                id=0,
                pos=AvrApriltagsRawTagsPos(x=1, y=2, z=3),
                rotation=((4, 5, 6), (7, 8, 9), (10, 11, 12)),
            ),
            (
                0,
                215.23243250030885,
                310.0,
                179.00939359502212,
                np.array([-215.20026451, 3.72104204, -310.0]),
                (-215.20026451227668, 3.721042037676277, -310.0),
                209.7448812969422,
            ),
        ),
        (
            AvrApriltagsRawTags(
                id=2,
                pos=AvrApriltagsRawTagsPos(x=1, y=2, z=3),
                rotation=((4, 5, 6), (7, 8, 9), (10, 11, 12)),
            ),
            (
                2,
                215.23243250030885,
                310.0,
                179.00939359502212,
                None,
                (-215.20026451227668, 3.721042037676277, -310.0),
                209.7448812969422,
            ),
        ),
    ],
)
def test_handle_tag(
    apriltag_module: AprilTagModule, tag: AvrApriltagsRawTags, expected: tuple
) -> None:
    result = apriltag_module.handle_tag(tag)
    for r_i, ex_i in zip(result, expected):
        if isinstance(ex_i, np.ndarray):
            np.allclose(r_i, ex_i)  # type: ignore
        else:
            assert r_i == ex_i
