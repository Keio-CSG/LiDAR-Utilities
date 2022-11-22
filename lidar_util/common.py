
import numpy as np

ROTATION_MAX_UNITS = 36000
SEQUENCE_TIME_US = 55.296
PULSE_TIME_US = 2.304
ROTATION_RESOLUTION = 0.01

class ParsedPacket:
    def __init__(self, points, factory, cut_point=None):
        self.points = points
        self.factory = factory
        self.cut_point = cut_point

class SpatialPoint:
    def __init__(self, x, y, z, azimuth, timestamp):
        self.x = x
        self.y = y
        self.z = z
        self.azimuth = azimuth
        self.timestamp = timestamp

    def __iter__(self):
        yield from [self.x,self.y,self.z,self.azimuth,self.timestamp]

    def __len__(self): return 5

    def __getitem__(self, i):
        return [self.x,self.y,self.z,self.azimuth,self.timestamp][i]

def calc_point(distance, azimuth, laser_id, timestamp, laser_angles, distance_resolution) -> SpatialPoint:
    R = distance * distance_resolution
    # 垂直方向の角度(rad)
    omega = laser_angles[laser_id] * np.pi / 180.0
    # 水平方向の角度(rad)
    alpha = azimuth * ROTATION_RESOLUTION * np.pi / 180.0
    X = R * np.cos(omega) * np.sin(alpha)
    Y = R * np.cos(omega) * np.cos(alpha)
    Z = R * np.sin(omega)
    return SpatialPoint(X,Y,Z, azimuth, timestamp)
