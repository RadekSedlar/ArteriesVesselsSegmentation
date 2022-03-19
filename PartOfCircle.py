import numpy as np
import cv2
import matplotlib.pyplot as plt
import DataPaths
import ProfileBenchmark
import math
import CircleCoordinationFinder



if __name__ == "__main__":
    blankImage = np.ones((100,100), dtype=np.uint8)
    cicleCoordinates = CircleCoordinationFinder.listOfCoordinates(20,30,60)

    for point in cicleCoordinates:
        blankImage[point[0],point[1]] = 255
    cv2.imshow("middle", blankImage)
    cv2.waitKey(0)