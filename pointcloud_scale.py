# the point cloud from the cameara in 16W need to be scaled 1000 in millimeter unit
import open3d as o3d
import numpy as np
import glob

# Define a scaling factor
scaling_factor = 1000.0
image_folder = "./test_data/16w_data/image_data"
ply_files = sorted(glob.glob(f'{image_folder}/*_textured.ply'))
idx=0
for ply_file in ply_files:
    pointcloud_2 = o3d.io.read_point_cloud(ply_file)
    # Scale the point cloud from the origin
    pointcloud_2.scale(scaling_factor, center=[0, 0, 0])
    new_ply_file = ply_file.replace(".ply", "_scaled.ply")
    o3d.io.write_point_cloud(new_ply_file, pointcloud_2)
    idx+=1
 