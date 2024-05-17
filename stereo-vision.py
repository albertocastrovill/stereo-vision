"""
This code will be used to develop a Python programming software to obtain the 3D reconstruction of various 
pixels representing the same object or objects in the rectified images.

Author: Alberto Castro
Date: 2024-05-12
"""

# Import libraries
import cv2
import numpy as np
import matplotlib.pyplot as plt
import re
import matplotlib
import argparse

# Use TkAgg backend for matplotlib
matplotlib.use('TkAgg')

# Funcion args parse para adquirir las dos imagenes de entrada
def get_args():
    """
    Get command line arguments.

    Returns:
        args (argparse.Namespace): Command line arguments.
    """
    parser = argparse.ArgumentParser(description='3D Reconstruction using Stereo Vision')
    parser.add_argument('--l_img', type=str, help='Path to the left rectified image')
    parser.add_argument('--r_img', type=str, help='Path to the right rectified image')
    args = parser.parse_args()
    return args

def load_images():
    """
    Load the rectified stereo images.

    Returns:
        imgL (numpy.ndarray): Left rectified image in grayscale.
        imgR (numpy.ndarray): Right rectified image in grayscale.
    """
    imgL = cv2.imread('rectified-images/left_infrared_image.png', 0)
    imgR = cv2.imread('rectified-images/right_infrared_image.png', 0)
    return imgL, imgR

def read_calibration_params(filepath):
    """
    Read the camera calibration parameters from a file.

    Args:
        filepath (str): Path to the calibration parameters file.

    Returns:
        calibration (dict): Dictionary containing calibration parameters.
    """
    params = {}
    pattern = re.compile(r'"(\w+)":\s*"(-?\d+\.?\d*)"')
    with open(filepath, 'r') as file:
        content = file.read()
        matches = pattern.findall(content)
        for key, value in matches:
            params[key] = float(value)
    calibration = {
        'cx': params.get('rectified_cx'),
        'cy': params.get('rectified_cy'),
        'f': params.get('rectified_fx'),
        'B': abs(params.get('baseline'))  # Use the absolute value for baseline
    }
    return calibration

def display_images(imgL, imgR):
    """
    Display the left and right rectified images.

    Args:
        imgL (numpy.ndarray): Left rectified image.
        imgR (numpy.ndarray): Right rectified image.
    """
    fig, axs = plt.subplots(1, 2, figsize=(20, 10))
    axs[0].imshow(imgL, cmap='gray')
    axs[0].set_title('Left Image')
    axs[0].axis('off')
    
    axs[1].imshow(imgR, cmap='gray')
    axs[1].set_title('Right Image')
    axs[1].axis('off')

    plt.tight_layout()
    plt.show()

def select_points(imgL, imgR):
    """
    Allow the user to select corresponding points in the left and right images.

    Args:
        imgL (numpy.ndarray): Left rectified image.
        imgR (numpy.ndarray): Right rectified image.

    Returns:
        left_points (list of tuples): List of selected points in the left image.
        right_points (list of tuples): List of selected points in the right image.
    """
    fig, axs = plt.subplots(1, 2, figsize=(20, 10))
    axs[0].imshow(imgL, cmap='gray')
    axs[0].set_title('Left Image')
    axs[0].axis('off')
    
    axs[1].imshow(imgR, cmap='gray')
    axs[1].set_title('Right Image')
    axs[1].axis('off')

    coords = []

    def onclick(event):
        if event.inaxes is axs[0]:
            x, y = int(event.xdata), int(event.ydata)
            axs[0].scatter(x, y, c='r')
            coords.append((x, y, 'left'))
        elif event.inaxes is axs[1]:
            x, y = int(event.xdata), int(event.ydata)
            axs[1].scatter(x, y, c='b')
            coords.append((x, y, 'right'))
        fig.canvas.draw()

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.tight_layout()
    plt.show()

    left_points = [(x, y) for x, y, img in coords if img == 'left']
    right_points = [(x, y) for x, y, img in coords if img == 'right']
    return left_points, right_points

def calculate_disparity(uL, uR):
    """
    Calculate the disparity between corresponding points.

    Args:
        uL (int): X-coordinate of the point in the left image.
        uR (int): X-coordinate of the point in the right image.

    Returns:
        disparity (int): Disparity between the points.
    """
    return uL - uR

def calculate_3D_coordinates(uL, vL, disparity, f, B):
    """
    Calculate the 3D coordinates of a point using disparity and calibration parameters.

    Args:
        uL (int): X-coordinate of the point in the left image.
        vL (int): Y-coordinate of the point in the left image.
        disparity (int): Disparity between corresponding points.
        f (float): Focal length of the camera.
        B (float): Baseline distance between the two cameras.

    Returns:
        X (float): X-coordinate in 3D space.
        Y (float): Y-coordinate in 3D space.
        Z (float): Z-coordinate in 3D space.
    """
    Z = (f * B) / disparity
    X = (uL * B) / disparity
    Y = (vL * B) / disparity
    return X, Y, Z

def visualize_3D(points_3D):
    """
    Visualize the 3D points.

    Args:
        points_3D (list of tuples): List of 3D points to visualize.
    """
    try:
        from mpl_toolkits.mplot3d import Axes3D
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter([p[0] for p in points_3D], [p[1] for p in points_3D], [p[2] for p in points_3D])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_box_aspect([1,1,1])  # Equal aspect ratio
        ax.set_xlim(-200, 200)  # Set X axis limits
        ax.set_ylim(-200, 400)  # Set Y axis limits
        ax.set_zlim(0, 1000)  # Set Z axis limits
        plt.show()
    except ImportError:
        print("3D projection is unavailable. Displaying in 2D.")
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.scatter([p[0] for p in points_3D], [p[1] for p in points_3D])
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()

def pipeline():
    """
    Main pipeline to load images, read calibration parameters, select points, 
    calculate 3D coordinates, and visualize the points.
    """
    imgL, imgR = load_images()

    params = read_calibration_params('calibration-parameters.txt')
    print("Camera Calibration Parameters:", params)

    left_points, right_points = select_points(imgL, imgR)
    print("Left Image Points:", left_points)
    print("Right Image Points:", right_points)

    if len(left_points) != len(right_points):
        print("The number of points selected in both images do not match.")
        return

    cx = params['cx']
    cy = params['cy']
    f = params['f']
    B = params['B']

    points_3D = []

    for (uL, vL), (uR, vR) in zip(left_points, right_points):
        uL_c = uL - cx
        vL_c = vL - cy
        uR_c = uR - cx
        
        disparity = calculate_disparity(uL_c, uR_c)
        
        if disparity == 0:
            print(f"Disparity is zero for point ({uL}, {vL}). Skipping this point.")
            continue
        
        X, Y, Z = calculate_3D_coordinates(uL_c, vL_c, disparity, f, B)
        points_3D.append((X, Y, Z))

    visualize_3D(points_3D)

if __name__ == '__main__':
    pipeline()
