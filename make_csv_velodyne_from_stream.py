
"""
    read and save Velodyne data to csv
    usage:
        ./make_csv_velodyne_from_stream.py [out_dir]
"""

from datetime import datetime
import struct
import time

from lidar_util.common import save_velo_csv
from lidar_util.vlp16 import parse_packet_vlp16_strongest
from lidar_util.vlp32c import parse_packet_vlp32c_strongest
from lidar_util.process_base import ProcessBase
import os
import sys
import socket

class CaptureProcess(ProcessBase):
    """
    socketでLiDARからのパケットを受け取るプロセス
    """
    def run(self, put_queue, recv_queue):
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.bind(("", 2368))
        count = 0
        prev_time = time.time()
        try:
            while True:
                try:
                    data = my_socket.recv(2000)
                    if len(data) > 0:
                        assert len(data) == 1206, len(data)
                        # print(f"Captured: {count} {time.time() - prev_time}")
                        prev_time = time.time()
                        put_queue.put({"data": data, "time": time.time()})
                        count += 1
                        # 1000パケットで打ち止め
                        if count > 1000:
                            break
                except Exception as e:
                    print(dir(e), e.message, e.__class__.__name__)
        except KeyboardInterrupt as e:
            print(e)

        # パケットの読み取りが終了したら最後に終了シグナルを投げる
        put_queue.put("TERMINATED")

class SaveCsvProcess(ProcessBase):
    def __init__(self, dir) -> None:
        super().__init__()
        self.dir = dir
    def run(self, put_queue, recv_queue):
        export_path = str(os.path.join(self.dir, 'csv'))
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
                    save_velo_csv(f"{export_path}/i{scan_index:04}.csv", points)
                    print(f"csv saved: {len(points)}")
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
    p_save = SaveCsvProcess(sys.argv[1] + '/' + top_dir)
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
