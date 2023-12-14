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


def save_pcd(path, data):
    #convert = lambda e: [e.x, e.y, e.z]
    #data = np.array(list(map(convert, data)))
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(data)

    o3d.io.write_point_cloud(path, pcd)


def pcap2pcd_velodyne(pcap_file, model, out_dir, rpm=600, dual=True):
    config = vd.Config(model=model, rpm=rpm)
    cloud_arrays = []
    for stamp, points in vd.read_pcap(pcap_file, config):

        cloud_arrays.append(points.tolist())

    if dual == True:
        for i in range(0, len(cloud_arrays), 2):
            array1 = np.array(cloud_arrays[i])
            array2 = np.array(cloud_arrays[i+1])
            array1 = array1[:, 0:3]
            array2 = array2[:, 0:3]
            array = np.concatenate([array1, array2], 0)
            print(array.shape)
            save_pcd(out_dir + str(i//2) + ".pcd", array)
    else:
        for i in range(len(cloud_arrays)):
            array = np.array(cloud_arrays[i])
            array = array[:, 0:3]
            print(array.shape)
            save_pcd(out_dir + str(i) + ".pcd", array)


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
