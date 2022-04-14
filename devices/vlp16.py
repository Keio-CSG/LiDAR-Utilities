import struct

from devices.common import PULSE_TIME_US, ROTATION_MAX_UNITS, SEQUENCE_TIME_US, ParsedPacket, calc_point

LASER_ANGLES = [-15, 1, -13, 3, -11, 5, -9, 7, -7, 9, -5, 11, -3, 13, -1, 15]

def parse_packet_vlp16_strongest(timestamp: float, d: bytes, offset: int, last_azimuth=None):
    """
    保存したpacketのdataをパースする

    data     : 1206 byte
        data_block: 100 byte * 12
            flag(0xFFEE)  : 2 byte
            azimuth       : 2 byte
            channel data A: 3 byte * 16
            channel data B: 3 byte * 16
                distance    : 2 byte
                reflectivity: 1 byte
        timestamp : 4 byte
        factory   : 2 byte

    - channel data Aにazimuthの角度のデータが入っている
    - channel data Bにazimuth+1の角度のデータが入っている
    """
    data = d[offset:offset+1206]
    # packet内のtimestampは3600秒しか測れないので捨てる
    timestamp_in_packet, factory = struct.unpack_from("<IH", data, offset=1200)
    assert factory == 0x2237, hex(factory)  # 0x22=VLP-16, 0x37=Strongest Return
    seqence_index = 0
    prev_azimuth = last_azimuth
    cut_point = None
    points = []
    for offset_inside in range(0, 1200, 100):
        # Data Blockの開始フラグと方位角(azimuth)
        flag, block_azimuth = struct.unpack_from("<HH", data, offset_inside)
        assert flag == 0xEEFF, hex(flag)
        # Data Blockには2つの方位角のデータが48 byteずれて入っている
        for step in range(2):
            seqence_index += 1
            azimuth = (block_azimuth + step) % ROTATION_MAX_UNITS
            if prev_azimuth is not None and azimuth < prev_azimuth:
                # 一周したら切れ目を覚えておく
                cut_point = len(points)
            prev_azimuth = azimuth
            channel_data_list = struct.unpack_from("<" + "HB" * 16, data, offset_inside+4 + step*48)
            for channel in range(16):
                distance = channel_data_list[channel*2]
                reflectivity = channel_data_list[channel*2+1]
                offset_time_sec = (SEQUENCE_TIME_US * seqence_index + PULSE_TIME_US * channel) / 1000000.0
                if distance != 0:
                    points.append(calc_point(distance, azimuth, channel, timestamp + offset_time_sec, LASER_ANGLES))

    return ParsedPacket(points, factory, cut_point), prev_azimuth