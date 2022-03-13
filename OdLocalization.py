import numpy as np
import cv2
import matplotlib.pyplot as plt

def image_histogram(image):
    rows, cols = image.shape
    histogram = np.full(shape=256,fill_value=0,dtype=np.int)
    print("Puvodni histogram")
    print(histogram)
    for x in range(rows):
        for y in range(cols):
            histogram[image[x][y]] += 1
    return histogram

def histogram_threshold(histogram, five_percent):
    index = 255
    counted = 0
    while index > 0:
        counted = counted + histogram[index]
        if counted >= five_percent:
            break
        index -= 1
    return index

def image_od_localization(image):
    histogram = image_histogram(image)
    # print("Vyplneny histogram")
    # print(histogram)

    rows, cols = image.shape
    # print(f"Shape je: {rows} x {cols}")
    amountOfPixels = rows * cols
    # print(f"Pocet pixelu je: {amountOfPixels}")
    five_percent = amountOfPixels // 100
    # print(f"5 procent z toho je: {five_percent}")
    max_value = histogram_threshold(histogram, five_percent)
    # print(f"Max hodnota tedy je: {max_value}")

    all_x = 0
    all_y = 0
    satisfactory_pixel_count = 0
    for x in range(rows):
        for y in range(cols):
            if image[x][y] >= max_value:
                satisfactory_pixel_count += 1
                all_x += x
                all_y += y
    
    od_coordinates = (all_y // satisfactory_pixel_count, all_x // satisfactory_pixel_count)
    return od_coordinates


path_to_working_dir = "C:\\Users\\GAMEBOX\\Desktop\\BakalarkaPy\\"
original_image_name = "21_training.tif"

if __name__ == "__main__":
    src = cv2.imread((path_to_working_dir + original_image_name))
    B_channel, G_channel, R_channel = cv2.split(src)

    (x, y) = image_od_localization(G_channel)
    image = cv2.circle(cv2.merge((G_channel,G_channel,G_channel)), (x, y), 20, (0, 0, 255), 2)
    cv2.imshow("middle", image)
    cv2.waitKey(0)

    