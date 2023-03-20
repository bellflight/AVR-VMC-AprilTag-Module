import math


CAM_POS = (0, 0, 8.5)
"""
Centimeters from FC forward, right, down
"""

CAM_ATTITUDE = (0, 0, math.pi / 2)
"""
Roll, pitch, yaw in radians
cam x = body -y; cam y = body x, cam z = body z
"""

TAG_TRUTH = {0: {"rpy": (0, 0, 0), "xyz": (0, 0, 0)}}
"""
Truth data about where tags are positioned in the world.
"""
