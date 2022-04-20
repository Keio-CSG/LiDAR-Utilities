import open3d as o3d
import numpy as np
import os
import sys
import glob

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    pcd = o3d.io.read_point_cloud(sys.argv[1])

    o3d.visualization.draw_geometries([pcd])