import open3d as o3d
import numpy as np
import os
import sys
import glob

from lidar_util.process_base import ProcessBase

TERMINATE_SIGNAL = "TERMINATED"
POINTS_PER_TURN = 54000

class ReadCsvProcess(ProcessBase):
    def __init__(self, dir) -> None:
        super().__init__()
        self.dir = dir

    def run(self, put_queue, _):
        # meter threshold
        x_thresh = [-6.0/2, 6.0/2]
        y_thresh = [-6.0/2, 6.0/2]
        z_thresh = [-2.0, 2.0]
        files = glob.glob(f"{self.dir}/*.csv")
        print(f"{len(files)} files")
        for x in files:
            point_list = []
            with open(x) as f:
                f.readline()
                while True:
                    data = f.readline()
                    if not data:
                        break
                    if not "," in data:
                        continue
                    point_coords = np.float64(data.strip().split(",")[:3])
                    if (point_coords[0] > x_thresh[0]) and (point_coords[0] < x_thresh[1]) and \
                            (point_coords[1] > y_thresh[0]) and (point_coords[1] < y_thresh[1]) and \
                            (point_coords[2] > z_thresh[0]) and (point_coords[2] < z_thresh[1]):
                        point_list.append(point_coords)
            print("read csv")
            put_queue.put(point_list)

        put_queue.put(TERMINATE_SIGNAL)

def o3d_animation(recv_queue):
    vis = o3d.visualization.Visualizer()
    vis.create_window()

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(
        np.random.rand(1000,3) * 3
    )
    vis.add_geometry(pcd)
    points = []
    offset = 0
    while True:
        if len(points) < offset:
            if recv_queue.empty():
                # print("luck of data")
                continue
            received = recv_queue.get()
            if received == TERMINATE_SIGNAL:
                print("TERMINATE")
                break
            print(f"get points: {len(received)}")
            points.extend(received)
            remove_index = max(0,offset - POINTS_PER_TURN)
            points = points[remove_index:]
            offset -= remove_index
        pcd.points = o3d.utility.Vector3dVector(
            points[max(0, offset - POINTS_PER_TURN):offset]
        )
        vis.update_geometry(pcd)
        vis.poll_events()
        vis.update_renderer()
        offset += 1000


def o3d_visualize(point_list: np.ndarray, view_thresh):
    x_thresh = view_thresh[0]
    y_thresh = view_thresh[1]
    z_thresh = view_thresh[2]

    vis = o3d.visualization.Visualizer()
    vis.create_window()

    pcd = o3d.geometry.PointCloud()

    pcd.points = o3d.utility.Vector3dVector(point_list)

    vis.add_geometry(pcd)

    for i in range(0,len(point_list), 100):
        pcd.points = o3d.utility.Vector3dVector(
            point_list[:i,:]
        )
        vis.update_geometry(pcd)
        vis.poll_events()
        vis.update_renderer()

    # o3d.visualization.draw_geometries(
    #     [pcd]
    # )

def load_data(point_cloud_path):
    # meter threshold
    x_thresh = [-6.0/2, 6.0/2]
    y_thresh = [-6.0/2, 6.0/2]
    z_thresh = [-2.0, 2.0]

    file_path = os.path.join(point_cloud_path)
    point_list = []
    all_point_list = []
    with open(file_path) as f:
        f.readline()
        while True:
            data = f.readline()
            if not data:
                break
            if not "," in data:
                continue
            point_coords = np.float64(data.strip().split(",")[:4])
            all_point_list.append(point_coords)
            if (point_coords[0] > x_thresh[0]) and (point_coords[0] < x_thresh[1]) and \
                    (point_coords[1] > y_thresh[0]) and (point_coords[1] < y_thresh[1]) and \
                    (point_coords[2] > z_thresh[0]) and (point_coords[2] < z_thresh[1]):
                point_list.append(point_coords)
    point_list = np.array(point_list)
    all_point_list = np.array(all_point_list)
    thresh = [x_thresh, y_thresh, z_thresh]
    return point_list, all_point_list, thresh

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    # data, all_data, view_thresh = load_data(sys.argv[1])
    # print(data.shape, all_data.shape)
    # o3d_visualize(data, view_thresh)
    p_read = ReadCsvProcess(sys.argv[1])
    queue_read = p_read.put_queue
    p_read.start()
    try:
        o3d_animation(queue_read)
    except KeyboardInterrupt as e:
        print(e)
        p_read.finish()
