from datetime import datetime
import os
import struct
import sys
import open3d as o3d
import numpy as np
from make_csv_from_stream import CaptureProcess
from process_base import ProcessBase
from devices.vlp16 import parse_packet_vlp16_strongest
from devices.vlp32c import parse_packet_vlp32c_strongest

def save_pcd(path, data):
    convert = lambda e: [e.x, e.y, e.z]
    data = np.array(list(map(convert, data)))
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(data)

    o3d.io.write_point_cloud(path, pcd)

class SavePcdProcess(ProcessBase):
    def __init__(self, dir) -> None:
        super().__init__()
        self.dir = dir

    def run(self, put_queue, recv_queue):
        export_path = str(os.path.join(self.dir, "pcd"))
        try:
            if os.path.exists(self.dir) is False:
                os.makedirs(self.dir)
            if os.path.exists(export_path) is False:
                os.makedirs(export_path)
            points = [] # 点群データ
            scan_index = 0
            last_azimuth = None
            while True:
                if recv_queue.empty():
                    continue
                received = recv_queue.get()
                # 終了シグナルだったらプロセスを終了
                if received == "TERMINATED":
                    break
                data = received["data"]
                timestamp = received["time"]
                mode, device = struct.unpack_from("<BB", data, 1204)
                if device == 0x22:
                    # print("VLP-16")
                    packet, last_azimuth = parse_packet_vlp16_strongest(timestamp, data, 0, last_azimuth)
                elif device == 0x28:
                    # print("VLP-32C")
                    packet, last_azimuth = parse_packet_vlp32c_strongest(timestamp, data, 0, last_azimuth)
                else:
                    raise ValueError(f"Unexpected device flag: {hex(device)}")
                if packet.cut_point is not None:
                    points.extend(packet.points[:packet.cut_point])
                    # 1周分溜まったらcsvに書き出す
                    save_pcd(f"{export_path}/i{scan_index:04}.pcd", points)
                    print(f"pcd saved: {len(points)}")
                    scan_index += 1
                    points = packet.points[packet.cut_point:]
                else:
                    points.extend(packet.points)
        except KeyboardInterrupt as e:
            print(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    top_dir = datetime.now().strftime('%Y%m%d-%H%M')
    p_capture = CaptureProcess()
    p_save = SavePcdProcess(sys.argv[1] + '/' + top_dir)
    queue_capture = p_capture.put_queue
    queue_save = p_save.recv_queue
    p_capture.start()
    p_save.start()
    while True:
        if queue_capture.empty():
            continue
        captured = queue_capture.get()
        if captured == "TERMINATED":
            print("SIGNAL TERMINATED")
            queue_save.put(captured)
            break
        queue_save.put(captured)