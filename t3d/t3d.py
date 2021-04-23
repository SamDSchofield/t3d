"""Main module."""
import numpy as np


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


