import velodyne_decoder as vd
import numpy as np
import open3d as o3d
from ouster.sdk.examples.pcap import pcap_to_pcd
from ouster.client import SensorInfo
from ouster.pcap import Pcap
import json

from ouster import client

def pcap2pcd_velodyne(pcap_file, model, rpm=600, dual=False):
    config = vd.Config(model=model, rpm=rpm)
    cloud_arrays = []
    for stamp, points in vd.read_pcap(pcap_file, config):
        cloud_arrays.append(points)

    cloud_arrays_np = np.array(cloud_arrays)

    print(cloud_arrays_np.shape[0])

    if dual == True:
        for i in range(0,cloud_arrays_np.shape[0],2):
            array1 = cloud_arrays_np[i]
            array2 = cloud_arrays_np[i+1]
            array1 = array1[:,0:3]
            array2 = array2[:,0:3]
            array = np.concatenate([array1,array2],0)
            print(array.shape)
            save_pcd(f"./data/save_pcd{i//2}.pcd", array)
    else:
        for i in range(cloud_arrays_np.shape[0]):
            array = cloud_arrays_np[i]
            array = array[:,0:3]
            print(array.shape)
            save_pcd(f"./data/save_pcd{i}.pcd", array)

def pcap2pcd_ouster(pcap_file, metadata, out_dir):
    with open(metadata, "r") as f:
        metadata = SensorInfo(f.read())
    source = Pcap(pcap_file, metadata)
    pcap_to_pcd(source, metadata, pcd_dir=out_dir)
