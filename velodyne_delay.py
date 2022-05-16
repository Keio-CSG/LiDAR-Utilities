import math
import random

angle_lazer_id = {
    -15: 0,
    -13: 2,
    -11: 4,
    -9: 6,
    -7: 8,
    -5: 10,
    -3: 12,
    -1: 14,
    1: 1,
    3: 3,
    5: 5,
    7: 7,
    9: 9,
    11: 11,
    13: 13,
    15: 15
}

SPEED_OF_LIGHT = 299792458 # m/s
FIRING_INTERVAL = 2.304e-6 # s
AZIMUTH_INTERVAL = 55.296e-6 # s
AZIMUTH_PER_ANGLE = 0.1 # degree

def calc_delay_point(
    received_azimuth: float,
    received_vertical_angle: int,
    received_distance: float,
    laser_distance: float,
    delay: float,
):
    """
    装置で特定の遅延を追加した場合のSpoofingポイントを計算する
    """
    delay_firing = angle_lazer_id[received_vertical_angle] * FIRING_INTERVAL
    delay_received = received_distance / SPEED_OF_LIGHT + delay_firing
    delay_laser_send = laser_distance / SPEED_OF_LIGHT

    delay_spoofer = delay_received + delay_laser_send + delay

    go_azimuth_count = math.floor(delay_spoofer / AZIMUTH_INTERVAL)
    go_azimuth = (go_azimuth_count * AZIMUTH_PER_ANGLE + received_azimuth) % 360
    rem = delay_spoofer - go_azimuth_count * AZIMUTH_INTERVAL
    go_firing_timing = math.floor(rem / FIRING_INTERVAL)
    if go_firing_timing > 15:
        return go_azimuth, None, None
    go_firing_angle = list(angle_lazer_id.keys())[list(angle_lazer_id.values()).index(go_firing_timing)]

    rem = rem - go_firing_timing * FIRING_INTERVAL
    go_distance = rem / 2 * SPEED_OF_LIGHT

    return go_azimuth, go_firing_angle, go_distance

def calc_point_delay(
    received_azimuth: float,
    received_vertical_angle: int,
    received_distance: float,
    laser_distance: float,
    go_azimuth: float,
    go_firing_angle: int,
    go_distance: float,
):
    """
    特定のSpoofingポイントから装置で追加するべき遅延を計算する
    """
    delay_firing = angle_lazer_id[received_vertical_angle] * FIRING_INTERVAL
    delay_received = received_distance / SPEED_OF_LIGHT + delay_firing
    delay_laser_send = laser_distance / SPEED_OF_LIGHT

    go_azimuth_time = (go_azimuth - received_azimuth) % 360 / AZIMUTH_PER_ANGLE * AZIMUTH_INTERVAL
    go_firing_time = angle_lazer_id[go_firing_angle] * FIRING_INTERVAL
    go_distance_time = go_distance * 2 / SPEED_OF_LIGHT

    delay_victim = go_azimuth_time + go_firing_time + go_distance_time

    return delay_victim - delay_received - delay_laser_send
