"""
    convert pcap files into pcd files
"""


import velodyne_decoder as vd
import numpy as np
import open3d as o3d
from ouster.sdk.examples.pcap import pcap_to_pcd
from ouster.client import SensorInfo
from ouster.pcap import Pcap
import json
import argparse

from ouster import client


def save_pcd(path, data_p, data_i):
    device = o3d.core.Device("CPU:0")
    dtype = o3d.core.float32
    #convert = lambda e: [e.x, e.y, e.z]
    #data = np.array(list(map(convert, data)))
    pcd = o3d.t.geometry.PointCloud(device)
    pcd.point["positions"] = o3d.core.Tensor(data_p, dtype, device)
    pcd.point["intensity"] = o3d.core.Tensor(data_i.reshape(-1, 1), dtype, device)

    o3d.t.io.write_point_cloud(path, pcd)


def pcap2pcd_velodyne(pcap_file, model, out_dir, rpm=600, dual=False):
    config = vd.Config(model=model, rpm=rpm)
    cloud_arrays = []
    for stamp, points in vd.read_pcap(pcap_file, config):
        cloud_arrays.append(points)

    cloud_arrays_np = np.array(cloud_arrays)

    print(cloud_arrays_np.shape[0])

    if dual == True:
        for i in range(0, cloud_arrays_np.shape[0], 2):
            array1 = cloud_arrays_np[i]
            array2 = cloud_arrays_np[i+1]
            array1_positions = array1[:, 0:3]
            array1_intensity = array1[:, 3]
            array2_positions = array2[:, 0:3]
            array2_intensity = array2[:, 3]
            array_positions = np.concatenate([array1_positions, array2_positions], 0)
            array_intensity = np.concatenate([array1_intensity, array2_intensity], 0)
            print(array_positions.shape, array_intensity.shape)
            save_pcd(out_dir + str(i//2) + ".pcd", array_positions, array_intensity)
    else:
        for i in range(cloud_arrays_np.shape[0]):
            array = cloud_arrays_np[i]
            array_positions = array[:, 0:3]
            array_intensity = array[:, 3]
            print(array_positions.shape, array_intensity.shape)
            save_pcd(out_dir + str(i) + ".pcd", array_positions, array_intensity)


def pcap2pcd_ouster(pcap_file, metadata, out_dir):
    with open(metadata, "r") as f:
        metadata = SensorInfo(f.read())
    source = Pcap(pcap_file, metadata)
    pcap_to_pcd(source, metadata, pcd_dir=out_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert .pcap into .pcd")

    parser.add_argument("device", choices=["ouster", "velodyne", "o", "v"])
    parser.add_argument("--rpm", "-r", help="rpm setting",
                        type=int, default=600)
    parser.add_argument("--dual", "-d", help="dual setting",
                        action="store_true")
    parser.add_argument("inputs", help='arguments for functions',
                        nargs='+', type=str)
    args = parser.parse_args()

    if args.device == "velodyne" or args.device == "v":
        pcap2pcd_velodyne(args.inputs[0], args.inputs[1],
                          args.inputs[2], args.rpm, args.dual)

    if args.device == "ouster" or args.device == "o":
        pcap2pcd_ouster(args.inputs[0], args.inputs[1], args.inputs[2])
