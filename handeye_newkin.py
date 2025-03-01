import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt
import os

from scipy.spatial.transform import Rotation as R
import pandas as pd
import math

from visual_kinematics.RobotSerial import *


def find_chessboard_corners(images, pattern_size, ShowCorners=False):
    """Finds the chessboard patterns and, if ShowImage is True, shows the images with the corners"""
    chessboard_corners = []
    IndexWithImg = []
    i = 0
    print("Finding corners...")
    for image in images:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, pattern_size)
        if ret:

            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners = cv2.cornerSubPix(gray, corners, (10, 10), (-1, -1), criteria)

            chessboard_corners.append(corners)

            cv2.drawChessboardCorners(image, pattern_size, corners, ret)
            if ShowCorners:
                # plot image using maplotlib. The title should "Detected corner in image: " + i
                plt.imshow(image)
                plt.title("Detected corner in image: " + str(i))
                plt.show()
            # Save the image in a folder Named "DetectedCorners"
            # make folder
            # if not os.path.exists("DetectedCorners"):
            #     os.makedirs("DetectedCorners")

            # cv2.imwrite("DetectedCorners/DetectedCorners" + str(i) + ".png", image)

            IndexWithImg.append(i)
            i = i + 1
        else:
            print("No chessboard found in image: ", i)
            i = i + 1
    return chessboard_corners, IndexWithImg


def calculate_intrinsics(chessboard_corners, IndexWithImg, pattern_size, square_size, ImgSize, ShowProjectError=False):
    """Calculates the intrinc camera parameters fx, fy, cx, cy from the images"""
    # Find the corners of the chessboard in the image
    imgpoints = chessboard_corners
    # Find the corners of the chessboard in the real world
    objpoints = []
    for i in range(len(IndexWithImg)):
        objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size
        objpoints.append(objp)
    # Find the intrinsic matrix
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, ImgSize, None, None)

    print("The projection error from the calibration is: ",
          calculate_reprojection_error(objpoints, imgpoints, rvecs, tvecs, mtx, dist, ShowProjectError))
    return mtx, dist


def calculate_reprojection_error(objpoints, imgpoints, rvecs, tvecs, mtx, dist, ShowPlot=False):
    """Calculates the reprojection error of the camera for each image. The output is the mean reprojection error
    If ShowPlot is True, it will show the reprojection error for each image in a bar graph"""

    total_error = 0
    num_points = 0
    errors = []

    for i in range(len(objpoints)):
        imgpoints_projected, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        imgpoints_projected = imgpoints_projected.reshape(-1, 1, 2)
        error = cv2.norm(imgpoints[i], imgpoints_projected, cv2.NORM_L2) / len(imgpoints_projected)
        errors.append(error)
        total_error += error
        num_points += 1

    mean_error = total_error / num_points


    return mean_error


def compute_camera_poses(chessboard_corners, pattern_size, square_size, intrinsic_matrix, dist, Testing=False):
    """Takes the chessboard corners and computes the camera poses"""
    # Create the object points.Object points are points in the real world that we want to find the pose of.
    object_points = np.zeros((pattern_size[0] * pattern_size[1], 3), dtype=np.float32)
    object_points[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size

    # Estimate the pose of the chessboard corners
    RTarget2Cam = []
    TTarget2Cam = []
    i = 1
    for corners in chessboard_corners:
        _, rvec, tvec = cv2.solvePnP(object_points, corners, intrinsic_matrix, dist)
        # rvec is the rotation vector, tvec is the translation vector
        if Testing == True:
            print("Current iteration: ", i, " out of ", len(chessboard_corners[0]), " iterations.")

            # Convert the rotation vector to a rotation matrix
            print("rvec: ", rvec)
            print("rvec[0]: ", rvec[0])
            print("rvec[1]: ", rvec[1])
            print("rvec[2]: ", rvec[2])
            print("--------------------")
        i = 1 + i
        R, _ = cv2.Rodrigues(rvec)  # R is the rotation matrix from the target frame to the camera frame
        RTarget2Cam.append(R)
        TTarget2Cam.append(tvec)

    return RTarget2Cam, TTarget2Cam


def read_aubo_joints(file):
    endposes = []
    with open(file, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            # line = line.replace(" ", "")

            line_data = line.split(' ')
            point = []
            for data in line_data:
                data = data.replace(",", "")
                point.append(float(data))

            endposes.append(point)

    return endposes

Setup603 = False#False
posefile_path = "./aT3s_opt.npy"


num_group = 6

if Setup603:
    group_lists = ["group1", "group2", "group3", "group4", "group5", "group6"]
    image_folder = "./handeye_data/data_images"
    pose_folder = "./handeye_data/data_robot"
    square_size = 10 / 1000
else:
    group_lists = ["group1", "group2", "group3", "group4", "group5", "group6"]
    image_folder = "./handeye_data/data_photoneo"
    pose_folder = "./handeye_data/data_nachi"
    square_size = 15 / 1000

images = []
for group in group_lists:
    image_files = sorted(glob.glob(f'{image_folder}/{group}/*.png'))
    images_group = [cv2.imread(f) for f in image_files]
    images.extend(images_group)

pattern_size = (11, 8)

ShowProjectError = True
ShowCorners = False

# tracker_T_3 poses
tracker_T_3s = np.load(posefile_path)

# camera calibration
chessboard_corners, IndexWithImg = find_chessboard_corners(images, pattern_size, ShowCorners=ShowCorners)
intrinsic_matrix, dist = calculate_intrinsics(chessboard_corners, IndexWithImg,
                                        pattern_size, square_size,
                                        images[0].shape[:2][::-1], ShowProjectError=ShowProjectError)



# Calculate camera extrinsics
RTarget2Cam, TTarget2Cam = compute_camera_poses(chessboard_corners, pattern_size, square_size, intrinsic_matrix, dist)


REnd2Base = []
TEnd2Base = []

if Setup603:
    dh_params = np.array([[0.1632, 0., 0.5 * pi, 0.],
                        [0., 0.647, pi, 0.5 * pi],
                        [0., 0.6005, pi, 0.],
                        [2.0132992e-01, 1.5028477e-05, -1.5706592e+00, -1.5707269e+00],
                        [1.02672115e-01, 4.72186694e-05, 1.57062984e+00, -2.43247976e-03],
                        [9.4024345e-02, 8.5766565e-05, -7.1511102e-05, -8.5101266e-05]])
else:
    dh_params = np.array([[0.550, 0.170, 0.5*pi, 0.0],
                          [0.0, 0.880, 0.0, 0.5*pi],
                          [0.0, 0.190, 0.5*pi, 0.0],
                          [8.1010062e-01, -3.6424387e-04, -1.5701164e+00, 1.7728833e-05],
                          [1.2373853e-04, 1.2213732e-04, 1.5702524e+00, 5.3631893e-04],               #
                          [1.1499943e-01, -1.5186303e-06, -2.6259433e-05,  7.6398765e-06]])

robot_aubo = RobotSerial(dh_params)
for group, i in zip(group_lists, range(num_group)):
    pose_file = f'{pose_folder}/{group}.txt'
    pose_group = read_aubo_joints(pose_file)

    for pose in pose_group:
        f = robot_aubo.forward(np.array(pose))
        Ts = robot_aubo.ts
        Link3TEnd_i = np.eye(4)
        for j in range(3, 6):
            Link3TEnd_i = Link3TEnd_i.dot(Ts[j].t_4_4)

        T = tracker_T_3s[i].dot(Link3TEnd_i)
        REnd2Base.append(T[:3, :3])
        TEnd2Base.append(T[:3, 3])


REnd2Base = np.array(REnd2Base)
TEnd2Base = np.array(TEnd2Base)

R_cam2gripper, t_cam2gripper = cv2.calibrateHandEye(
    REnd2Base,
    TEnd2Base,
    RTarget2Cam,
    TTarget2Cam,
    method=4
)
end_T_cam = np.eye(4)
end_T_cam[:3, :3] = R_cam2gripper
end_T_cam[:3, 3] = t_cam2gripper[:, 0]

print("end_T_cam: ", end_T_cam)


# end_T_cam = np.array([[0.99999378, 0.00218076, -0.00277091, 0.04262605],
#                      [-0.00216497, 0.99998148, 0.00568824, 0.0067556],
#                      [0.00278326, -0.00568221, 0.99997998, 0.12970971],
#                      [0, 0, 0, 1]])


# 16W
# The projection error from the calibration is:  0.010129184768624419
end_T_cam=np.array([[-1.33946016e-03,  9.99962119e-01, -8.60038500e-03, -3.63372197e-02],
 [-9.65772017e-01,  9.37282195e-04,  2.59390694e-01, -1.12871821e-01],
 [ 2.59388929e-01,  8.65345467e-03,  9.65734177e-01,  1.19948724e-01],
 [ 0.00000000e+00,  0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])