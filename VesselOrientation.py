from copy import deepcopy
import math
import cv2
import numpy as np;
import Main

def get_point_from_angle_and_distance(originalPoint, angle, distance):
    newX = int(distance * math.cos(angle))
    newY = int(distance * math.sin(angle))
    return [originalPoint[0] + newX, originalPoint[1] + newY]

def get_points_on_line(originalPoint, angle, lenght):
    #print("-+-+-+-+-+-+- get_points_on_line -+-+-+-+-+-+-")
    pointsOnLine = []
    for distance in range(lenght):
        pointsOnLine.append(get_point_from_angle_and_distance(originalPoint, angle, distance))
    #for distance in range(lenght):
    #    pointsOnLine.append(get_point_from_angle_and_distance(originalPoint, angle + math.pi, distance))
    #print(f"returning {pointsOnLine}")
    #print("-+-+-+-+-+-+- END OF get_points_on_line -+-+-+-+-+-+-")
    return pointsOnLine


def is_angle_in_range(angle, minAngle, maxAngle):
    if minAngle < 0:
        minAngle = minAngle + math.pi*2
        if angle > maxAngle and angle < minAngle:
            return False
        return True
            
    if angle <= maxAngle and angle >= minAngle:
        return True
    return False

def vessel_orientation(groundTruth, originalPoint, minAngle, maxAngle):
    # TODO pridat orientation range
    angleOriginal = math.pi / 12
    vesselOrientation = 0
    noOfMostSuitedPixels = 0
    pointsOfBestConformity = []
    currentAngle = minAngle
    #iteration = 1
    #while currentAngle < maxAngle:
    #    #print(f"Iteration number: {iteration}\n Current angle: {currentAngle} < {maxAngle}")
    #    iteration += 1
    #    pointsOnLine = get_points_on_line(originalPoint, currentAngle, 10)
    #    suitedPixels = 0
    #    for point in pointsOnLine:
    #        if groundTruth[point[0]][point[1]] == 255:
    #            suitedPixels += 1
    #    if suitedPixels > noOfMostSuitedPixels:
    #        noOfMostSuitedPixels = suitedPixels
    #        pointsOfBestConformity = pointsOnLine
    #        vesselOrientation = currentAngle
    #    currentAngle = currentAngle + angleOriginal
    for angleMultiplyer in range(24):
        currentAngle = angleOriginal * angleMultiplyer
        if not is_angle_in_range(currentAngle, minAngle, maxAngle):
            continue
            
        pointsOnLine = get_points_on_line(originalPoint, currentAngle, 10)
        suitedPixels = 0
        for point in pointsOnLine:
            if groundTruth[point[0]][point[1]] == 255:
                suitedPixels += 1
        if suitedPixels > noOfMostSuitedPixels:
            noOfMostSuitedPixels = suitedPixels
            pointsOfBestConformity = pointsOnLine
            vesselOrientation = currentAngle
    return (vesselOrientation, noOfMostSuitedPixels, pointsOfBestConformity)
                

if __name__ == "__main__":
    blank_image = np.zeros((100,100,3), np.uint8)
    originalPoint = [50, 20]
    blank_image = cv2.circle(blank_image, (originalPoint[0], originalPoint[1]), radius = 5, color = (255,0,0), thickness=-1)
    angleOriginal = math.pi / 12
    for angleMultiplyer in range(12):
        pointsOnLine = get_points_on_line(originalPoint, angleOriginal * angleMultiplyer, 10)

        for pointOnLine in pointsOnLine:
            blank_image[pointOnLine[1]][pointOnLine[0]] = (0,255,0)
    
    cv2.imshow("result", blank_image)
    cv2.waitKey(0)

