from typing import List
import csv

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
    def __init__(self,
                 intensity: int,
                 laser_id: int,
                 azimuth: int,
                 distance_m: float,
                 timestamp: int,
                 vertical_angle: float,
                 x: float, y: float, z: float):
        self.intensity = intensity
        self.laser_id = laser_id
        self.azimuth = azimuth
        self.distance_m = distance_m
        self.timestamp = timestamp
        self.vertical_angle = vertical_angle
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        yield from [
            self.intensity, self.laser_id, self.azimuth,
            self.distance_m, self.timestamp, self.timestamp, self.vertical_angle,
            self.x,self.y,self.z]

    def __len__(self): return 10

    def __getitem__(self, i):
        return [
            self.intensity, self.laser_id, self.azimuth,
            self.distance_m, self.timestamp, self.timestamp, self.vertical_angle,
            self.x,self.y,self.z][i]

def save_velo_csv(path: str, points: List[SpatialPoint]):
    with open(path, 'w') as fp:
        wr = csv.writer(fp, delimiter=',')
    wr.writerow([
        "intensity","laser_id","azimuth","distance_m","adjustedtime",
        "timestamp","vertical_angle","Points_m_XYZ:0","Points_m_XYZ:1","Points_m_XYZ:2"
    ])
    wr.writerows(points)

def calc_point(
        distance: int, azimuth: int, laser_id: int,
        timestamp: int, intensity: int,
        laser_angles: List[float], distance_resolution: float) -> SpatialPoint:
    """
    パケットとデバイスの情報から点データを構築する
    :param distance: 距離。distance * distance_resolution [m]
    :param azimuth: 方位角。azimuth * ROTATION_RESOLUTION [deg]
    :param laser_id: レーザの発射タイミング
    :param timestamp: 時間 [us]
    :param intensity: 反射率 [0-255]
    :param laser_angles: 垂直角の辞書。laser_idをキーとして垂直角 [deg]を出す
    :param distance_resolution: 距離解像度
    :return:
    """
    r = distance * distance_resolution
    # 垂直方向の角度(rad)
    vertical_angle = laser_angles[laser_id]
    omega = vertical_angle * np.pi / 180.0
    # 水平方向の角度(rad)
    alpha = azimuth * ROTATION_RESOLUTION * np.pi / 180.0
    x = r * np.cos(omega) * np.sin(alpha)
    y = r * np.cos(omega) * np.cos(alpha)
    z = r * np.sin(omega)
    return SpatialPoint(intensity, laser_id, azimuth, r, timestamp,vertical_angle, x,y,z)
