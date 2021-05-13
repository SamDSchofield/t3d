"""
* Converting to and from lines, quaternions, matrices, etc
* Transforming a point or points"""
import cv2
import numpy as np
import transforms3d


def T_from_line(line):
    t = line[1:4]
    quat = line[4:]
    return T_from_quat(t, quat)


def T_to_line(T, stamp):
    t, r, _, _ = transforms3d.affines.decompose(T)
    r_quat = transforms3d.quaternions.mat2quat(r)
    return np.hstack((stamp, t, r_quat))


def T_from_quat(t, quat):
    r_mat = transforms3d.quaternions.quat2mat(quat)
    T = transforms3d.affines.compose(t, r_mat, np.ones(3))
    return T


def T_from_vec(t, vec):
    r_mat, _ = cv2.Rodrigues(vec)
    r_quat = transforms3d.quaternions.mat2quat(r_mat)
    return T_from_quat(t, r_quat)


def T_to_quat(T):
    pass


def T_to_vec(T):
    t, r_mat, _, _ = transforms3d.affines.decompose(T)
    r_vec, _ = cv2.Rodrigues(r_mat)
    return t, r_vec.flatten()


def apply_T(T, points):
    """Convert an array of 3D points into homogeneous coords, left-multiply by T, then convert back."""
    flipped = True
    points = points.T
    points_h = np.vstack((points, np.ones_like(points[0, :])))
    points_transformed_h = np.dot(T, points_h)
    points_transformed = points_transformed_h[:-1]
    if flipped:
        return points_transformed.T
    return points_transformed


def apply_offset_before(trajectory, offset):
    offset_trajectory = []
    for pose in trajectory:
        offset_pose = np.matmul(offset, pose)
        offset_trajectory.append(offset_pose)
    return np.array(offset_trajectory)


def apply_offset(trajectory, offset):
    offset_trajectory = []
    for pose in trajectory:
        offset_pose = np.matmul(pose, offset)
        offset_trajectory.append(offset_pose)
    return np.array(offset_trajectory)


def compose_transform(position, rotation):
    return transforms3d.affines.compose(T=position, R=rotation, Z=np.ones(3))


def traj_quat2euler(trajectory):
    """Take a (N,8) trajectory consisting of stamp, position, quaternion and convert
    to stamp, position, euler.
    """
    converted_trajectory = []
    for stamp, *pose in trajectory:
        quaternion = pose[3:]
        euler = transforms3d.euler.quat2euler(quaternion)
        converted_pose = np.concatenate([[stamp], pose[:3], euler]).T
        converted_trajectory.append(converted_pose)
    return np.array(converted_trajectory)


def traj_array2mat(trajectory):
    """Take a (N,8) trajectory consisting of stamp, position, quaternion and convert it
    to a list of 4x4 pose matrices
    """
    stamps = trajectory[:, 0]
    mats = []
    for pose in trajectory[:, 1:]:
        position = pose[:3]
        quaternion = pose[3:]
        rotation_mat = transforms3d.quaternions.quat2mat(quaternion)
        pose_mat = compose_transform(position, rotation_mat)
        mats.append(pose_mat)
    return stamps, np.array(mats)


def traj_mat2array(stamps, mat_traj):
    flat_traj = []
    for stamp, pose in zip(stamps, mat_traj):
        flat_traj.append(T_to_line(pose, stamp))
    return flat_traj