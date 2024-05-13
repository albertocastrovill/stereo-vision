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


# Función para cargar las imágenes
def cargar_imagenes():
    # Cargar las imágenes
    imgL = cv2.imread('rectified-images/left_infrared_image.png', 0)
    imgR = cv2.imread('rectified-images/right_infrared_image.png', 0)
    return imgL, imgR


# Función para mostrar las imagenes
def mostrar_imagenes(imgL, imgR):
    # Mostrar las imágenes
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(imgL, cmap='gray')
    plt.title('Left Image')
    plt.axis('off')
    plt.subplot(1, 2, 2)
    plt.imshow(imgR, cmap='gray')
    plt.title('Right Image')
    plt.axis('off')
    plt.show()

def seleccionar_puntos(imgL, imgR):
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    axs[0].imshow(imgL, cmap='gray')
    axs[0].set_title('Left Image')
    axs[0].axis('off')
    
    axs[1].imshow(imgR, cmap='gray')
    axs[1].set_title('Right Image')
    axs[1].axis('off')

    coords = []  # Lista para almacenar las coordenadas (u,v) de ambos puntos

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

    # Conectar el evento con la función
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    # Filtrar y separar las coordenadas de cada imagen
    left_points = [(x, y) for x, y, img in coords if img == 'left']
    right_points = [(x, y) for x, y, img in coords if img == 'right']
    return left_points, right_points


# Main function
def pipeline():
    # Load images
    imgL, imgR = cargar_imagenes()

    left_points, right_points = seleccionar_puntos(imgL, imgR)

    print("Puntos seleccionados en la imagen izquierda:", left_points)
    print("Puntos seleccionados en la imagen derecha:", right_points)

# Call the main function
if __name__ == '__main__':
    pipeline()