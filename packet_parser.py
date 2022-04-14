import glob
import struct
import csv
import os
import sys

from devices.vlp16 import parse_packet_vlp16_strongest
from devices.vlp32c import parse_packet_vlp32c_strongest

def save_csv(path, data):
    with open(path, 'w') as fp:
        wr = csv.writer(fp, delimiter=',')
        wr.writerows(data)

def unpack(dirs):
    files = glob.glob(dirs + "/*.bin")
    export_path = str(os.path.join(dirs, 'csv'))
    try:
        if os.path.exists(export_path) is False:
            os.makedirs(export_path)
    except Exception as e:
        print(e)
    points = []
    scan_index = 0
    for x in files:
        d = open(x, "rb").read()
        n = len(d)
        for offset in range(0,n,1223):
            # パケット: 1223 byte
            #     timestamp: 17 byte
            #     data     : 1206 byte
            last_azimuth = points[-1].azimuth if len(points) > 0 else None
            timestamp = float(d[offset:offset+17])
            mode, device = struct.unpack_from("<BB", d, offset+17+1204)
            if device == 0x22:
                print("VLP-16")
                packet = parse_packet_vlp16_strongest(timestamp, d, offset+17, last_azimuth)
            elif device == 0x28:
                print("VLP-32C")
                packet = parse_packet_vlp32c_strongest(timestamp, d, offset+17, last_azimuth)
            else:
                raise ValueError(f"Unexpected device flag: {hex(device)}")
            if packet.cut_point is not None:
                points.extend(packet.points[:packet.cut_point])
                save_csv(f"{export_path}/i{scan_index:04}.csv", points)
                scan_index += 1
                points = packet.points[packet.cut_point:]
            else:
                points.extend(packet.points)

if __name__ == "__main__":
    unpack(sys.argv[2])
