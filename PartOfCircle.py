import numpy as np
import cv2
import matplotlib.pyplot as plt
import DataPaths
import ProfileBenchmark
import math
import CircleCoordinationFinder
import os
import CandidatePoints
import VesselOrientation

def filter_points_on_circle_by_angle(currentPoint, pointsOnCircle, middleAngle):
    finalPoints = []
    minAngle = middleAngle - (math.pi/4)
    maxAngle = middleAngle + (math.pi/4)
    for pointFromCircle in pointsOnCircle:
        angleBetweenLastPointAndNewOne = CandidatePoints.angle_between_middle_and_candidate(currentPoint,pointFromCircle)
        angleBetweenLastPointAndNewOne = CandidatePoints.quadrant_angle(currentPoint, pointFromCircle, angleBetweenLastPointAndNewOne)
        if VesselOrientation.is_angle_in_range(angleBetweenLastPointAndNewOne, minAngle, maxAngle):
            finalPoints.append(pointFromCircle)
    
    return finalPoints

if __name__ == "__main__":

    middlePoint = [11,8]
    startPoint = [13,9]

    goldenTruth = cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Seeking", "SeekingTraining.bmp"), cv2.IMREAD_GRAYSCALE)
    pictureForDrawing = cv2.merge((goldenTruth,goldenTruth,goldenTruth))

    angleBetweeenStartAndCurrentPoint = CandidatePoints.angle_between_middle_and_candidate(middlePoint,startPoint)
    angleBetweeenStartAndCurrentPoint = CandidatePoints.quadrant_angle(middlePoint, startPoint, angleBetweeenStartAndCurrentPoint)

    cicleCoordinates1 = CircleCoordinationFinder.listOfCoordinates(1,startPoint[0],startPoint[1])
    cicleCoordinates1 = filter_points_on_circle_by_angle([startPoint[1], startPoint[0]], cicleCoordinates1, angleBetweeenStartAndCurrentPoint)
    cicleCoordinates2 = CircleCoordinationFinder.listOfCoordinates(2,startPoint[0],startPoint[1])
    cicleCoordinates2 = filter_points_on_circle_by_angle(startPoint, cicleCoordinates2, angleBetweeenStartAndCurrentPoint)
    cicleCoordinates3 = CircleCoordinationFinder.listOfCoordinates(3,startPoint[0],startPoint[1])
    cicleCoordinates3 = filter_points_on_circle_by_angle(startPoint, cicleCoordinates3, angleBetweeenStartAndCurrentPoint)




    for point in cicleCoordinates1:
        pictureForDrawing[point[0],point[1]] = (255,0,0)
    for point in cicleCoordinates2:
        pictureForDrawing[point[0],point[1]] = (0,255,0)
    for point in cicleCoordinates3:
        pictureForDrawing[point[0],point[1]] = (0,0,255)
    cv2.imshow("middle", pictureForDrawing)
    cv2.imwrite(DataPaths.results_image_path("partOfCircle"), pictureForDrawing)
    cv2.waitKey(0)