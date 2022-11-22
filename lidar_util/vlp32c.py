import struct

from lidar_util.common import PULSE_TIME_US, ROTATION_MAX_UNITS, SEQUENCE_TIME_US, ParsedPacket, calc_point

LASER_ANGLES = [
    -25   , -1    , -1.667, -15.639, -11.31, 0    , -0.667, -8.843, 
    -7.254, 0.333, -0.333, -6.148 , -5.333, 1.333, 0.667 , -4    ,
    -4.667, 1.667, 1     , -3.667 , -3.333, 3.333, 2.333 , -2.667,
    -3    , 7    , 4.667 , -2.333 , -2    , 15   , 10.333, -1.333
]

AZIMUTH_OFFSETS = [
     1.4, -4.2,  1.4, -1.4,  1.4, -1.4,  4.2, -1.4,
     1.4, -4.2,  1.4, -1.4,  4.2, -1.4,  4.2, -1.4,
     1.4, -4.2,  1.4, -4.2,  4.2, -1.4,  1.4, -1.4,
     1.4, -1.4,  1.4, -4.2,  4.2, -1.4,  1.4, -1.4
]

DISTANCE_RESOLUTION = 0.004 # 4 mm


def parse_packet_vlp32c_strongest(timestamp: float, d: bytes, offset: int, last_azimuth=None):
    """
    保存したpacketのdataをパースする

    data     : 1206 byte
        data_block: 100 byte * 12
            flag(0xFFEE)  : 2 byte
            azimuth       : 2 byte
            channel data  : 3 byte * 32
                distance    : 2 byte
                reflectivity: 1 byte
        timestamp : 4 byte
        factory   : 2 byte
    """
    data = d[offset:offset+1206]
    # packet内のtimestampは3600秒しか測れないので捨てる
    timestamp_in_packet, factory = struct.unpack_from("<IH", data, offset=1200)
    assert factory == 0x2837, hex(factory)  # 0x28=VLP-16, 0x37=Strongest Return
    seqence_index = 0
    prev_azimuth = last_azimuth
    cut_point = None
    points = []
    for offset_inside in range(0, 1200, 100):
        # Data Blockの開始フラグと方位角(azimuth)
        flag, azimuth = struct.unpack_from("<HH", data, offset_inside)
        assert flag == 0xEEFF, hex(flag)
        
        seqence_index += 1
        azimuth = azimuth % ROTATION_MAX_UNITS
        if prev_azimuth is not None and azimuth < prev_azimuth:
            # 一周したら切れ目を覚えておく
            cut_point = len(points)
        prev_azimuth = azimuth
        channel_data_list = struct.unpack_from("<" + "HB" * 32, data, offset_inside+4)
        for channel in range(32):
            distance = channel_data_list[channel*2]
            reflectivity = channel_data_list[channel*2+1]
            azimuth_offset = AZIMUTH_OFFSETS[channel] * 100.0
            firing_order = channel // 2
            offset_time_sec = (SEQUENCE_TIME_US * seqence_index + PULSE_TIME_US * firing_order) / 1000000.0
            if distance != 0:
                points.append(calc_point(
                    distance, azimuth + azimuth_offset, channel, timestamp + offset_time_sec, 
                    reflectivity, LASER_ANGLES, DISTANCE_RESOLUTION
                ))

    return ParsedPacket(points, factory, cut_point), prev_azimuth
