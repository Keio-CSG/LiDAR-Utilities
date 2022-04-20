import os
from ouster import client
from contextlib import closing
from datetime import datetime
from more_itertools import nth
import sys
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
HOST_NAME = "os-122201001516.local"

def save_pcd(path, data):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(data)

    o3d.io.write_point_cloud(path, pcd)

def capture(hostname, count):
    config = client.SensorConfig()
    config.udp_port_lidar = 7502
    config.udp_port_imu = 7503
    config.operating_mode = client.OperatingMode.OPERATING_NORMAL
    client.set_config(hostname, config, persist=True, udp_dest_auto = True)
    source = client.Sensor(hostname)
    info = source.metadata
    xyzlut = client.XYZLut(info)
    with closing(client.Scans(source)) as scans:
        scans_iter = iter(scans)
        for i in range(count):
            scan = next(scans_iter)
            xyz = xyzlut(scan)
            yield xyz

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    top_dir = datetime.now().strftime('%Y%m%d-%H%M')
    scan_index = 0
    dir = f"{sys.argv[1]}/{top_dir}"
    export_path = str(os.path.join(dir, "pcd"))
    if os.path.exists(export_path) is False:
        os.makedirs(export_path)
    for data in capture(HOST_NAME, 10):
        save_pcd(f"{export_path}/i{scan_index:04}.pcd", data.reshape(-1, 3))
        print(f"pcd saved: {data.size / 3}")
        scan_index += 1
    