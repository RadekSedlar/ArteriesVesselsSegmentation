import numpy as np
import cv2
import matplotlib.pyplot as plt
import DataPaths
import ProfileBenchmark
import math

def image_histogram(image):
    rows, cols = image.shape
    histogram = np.full(shape=256,fill_value=0,dtype=np.int)
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

def image_od_localization(grayScaleImage):
    kernel = np.ones((51,51), dtype=np.int32)
    circleRadius = 25.0
    middlePoint = (26,26)
    
    for x in range(51):
        for y in range(51):
            distanceFromMiddle = math.sqrt(math.pow(x - middlePoint[0],2) + math.pow(y - middlePoint[1],2))
            if distanceFromMiddle > circleRadius:
                kernel[y,x] = -1
            else:
                kernel[y,x] = 1
                
    uint16Image = grayScaleImage.astype("int32")
    result = cv2.filter2D(uint16Image, -1, kernel)
    rows, cols = result.shape
    maxValue = 0
    coordinatesOfMiddle = [0,0]
    for x in range(rows):
        for y in range(cols):
            if result[x][y] > maxValue:
                coordinatesOfMiddle[1] = x
                coordinatesOfMiddle[0] = y
                maxValue = result[x][y]
    return coordinatesOfMiddle
    


path_to_working_dir = "C:\\Users\\GAMEBOX\\Desktop\\BakalarkaPy\\"
original_image_name = "21_training.tif"

if __name__ == "__main__":
    imageNumber = 8
    src = cv2.imread(DataPaths.original_image_path(imageNumber))
    B_channel, G_channel, R_channel = cv2.split(src)

    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(20, 20))
    # using CLAHE
    G_channel_with_CLAHE = clahe.apply(G_channel)
    cv2.imshow("middle", G_channel_with_CLAHE)
    cv2.waitKey(0)

    mask = ProfileBenchmark.read_mask_and_erode_it(imageNumber, erodeIteration=10)
    G_channel = cv2.bitwise_or(G_channel, G_channel, mask=mask)
    (x, y) = image_od_localization(G_channel)
    image = cv2.circle(cv2.merge((G_channel,G_channel,G_channel)), (x, y), 20, (0, 0, 255), 2)
    cv2.imshow("middle", image)
    cv2.waitKey(0)



    