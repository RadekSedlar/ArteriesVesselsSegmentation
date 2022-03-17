import math
import cv2
from cv2 import sqrt
import numpy as np
import OdLocalization
import CircleCoordinationFinder
import Main
import skeletonize
import VesselOrientation
import DataPaths



def find_middle(input_list):
    """ Finds element in the middle of @input_list.

    @type input_list: [object]
    @param input_list: list of elements

    @rtype: object
    @returns: Object in middle of @input_list."""
    middle = float(len(input_list))/2
    if middle % 2 != 0:
        return input_list[int(middle - .5)]
    else:
        return input_list[int(middle)]


def start_from_non_vessel(groundTruth, circlePoints):
    """ Finds element in the middle of @input_list.

    @type groundTruth: [[uint8]]
    @param groundTruth: manualy segmented vessels
    @type circlePoints: [[int,int]]
    @param circlePoints: list of points, representing circle

    @rtype: object
    @returns: Object in middle of @input_list."""
    while groundTruth[circlePoints[0][1]][circlePoints[0][0]] == 255:
        #print(f"First point is: {circlePoints[0]} with value: {groundTruth[circlePoints[0][1]][circlePoints[0][0]]}")
        tempPoint = circlePoints[0]
        circlePoints.remove(0)
        circlePoints.append(tempPoint)

def find_middle_pixels_on_circle(groundTruth, circlePoints):
    """ Finds element in the middle of @input_list.

    @type groundTruth: [[uint8]]
    @param groundTruth: manualy segmented vessels
    @type circlePoints: [[int,int]]
    @param circlePoints: list of points, representing circle

    @rtype: [[int,int]]
    @returns: List of vessels middle points"""
    start_from_non_vessel(groundTruth, circlePoints)
    endPoints = []
    
    currentPosition = 0
    numberOfPoints = len(circlePoints)
    while currentPosition < numberOfPoints:
        #print(f"{circlePoints[currentPosition]}: {groundTruth[circlePoints[currentPosition][0]][circlePoints[currentPosition][1]]}")
        if groundTruth[circlePoints[currentPosition][0]][circlePoints[currentPosition][1]] == 255:
            #print(f"Position {circlePoints[currentPosition]} is a vessel")
            vesselPoints = []
            vesselPoints.append(circlePoints[currentPosition])
            currentPosition += 1
            while (currentPosition < numberOfPoints) and (groundTruth[circlePoints[currentPosition][0]][circlePoints[currentPosition][1]] == 255):
                #print(f"Position {circlePoints[currentPosition]} is also a vessel")
                vesselPoints.append(circlePoints[currentPosition])
                currentPosition += 1
            middle_point = find_middle(vesselPoints)
            vesselInfo = skeletonize.get_middle_pixel(groundTruth, middle_point[0], middle_point[1])
            #print(f"Position {middle_point} is middle of the last vessel")
            endPoints.append(swap_point_coordinates(vesselInfo.point))
        else:
            #print(f"Position {circlePoints[currentPosition]} is not a vessel")
            currentPosition += 1
    return endPoints
            
def draw_orientation_line(imageForDrawing, pointsOfOrientation, lineColor=(0, 255, 0)):
    for linePoint in pointsOfOrientation:
        imageForDrawing[linePoint[1]][linePoint[0]] = lineColor
    lastPoint = pointsOfOrientation[len(pointsOfOrientation) -1 ]
    imageForDrawing[lastPoint[1]][lastPoint[0]] = (0, 255, 255)
    

def get_next_point(originalPoint, points):
    for currentPoint in points:
        if currentPoint[0] != originalPoint[0] or currentPoint[1] != originalPoint[1]:
            return currentPoint
    raise Exception("Not enought points")
            

def draw_small_circle(iamgeForDrawing, point):
    return cv2.circle(iamgeForDrawing, point, 0, (255, 0, 0), 2)

def swap_point_coordinates(original):
    return [original[1],original[0]]

def angle_between_middle_and_candidate(middlePoint, candidatePoint):
    print(f"Middle of circle is: {middlePoint}, candidatePoint is: {candidatePoint}")
    x_diff = coordinate_difference(candidatePoint[0], middlePoint[0])
    y_diff = coordinate_difference(candidatePoint[1], middlePoint[1])
    
    rad = math.pi/2 - math.atan2(y_diff, x_diff)
    print(f"rad\t=> {rad}")
    print(f"Triangle \nY: {y_diff}\nX: {x_diff}\n aplha: {math.degrees(rad)}")
    return rad

def quadrant_angle(middleRefencePoint, point, angle):
    if point[0] > middleRefencePoint[0] and point[1] >= middleRefencePoint[1]:
        return angle
    if point[0] <= middleRefencePoint[0] and point[1] > middleRefencePoint[1]:
        return ((math.pi/2)*3) + ((math.pi/2) - angle)
    if point[0] < middleRefencePoint[0] and point[1] <= middleRefencePoint[1]:
        return angle + math.pi
    if point[0] >= middleRefencePoint[0] and point[1] < middleRefencePoint[1]:
        return (math.pi/2) + ((math.pi/2) - angle)

def coordinate_difference(x1, x2):
    if x1>x2:
        return x1-x2
    return x2-x1

if __name__ == "__main__":

    imageNumber = 1
    golden_truth = Main.read_gif_image(DataPaths.original_manual_image_path(imageNumber))
    src = cv2.imread(DataPaths.original_image_path(imageNumber))
    radius = 45

    B_channel, G_channel, R_channel = cv2.split(src)
    (x, y) = OdLocalization.image_od_localization(G_channel)
    image_with_circle = cv2.circle(cv2.merge((golden_truth,golden_truth,golden_truth)), (x, y), radius, (0, 0, 255), 2)

    cv2.imwrite(DataPaths.results_image_path("localizedOD"), image_with_circle)

    circle_coordinates = CircleCoordinationFinder.listOfCoordinates(radius, x_of_middle=x, y_of_middle=y)
    candidatePoints = find_middle_pixels_on_circle(golden_truth, circle_coordinates)
    print("Start original")
    for candidatePoint in candidatePoints:
        (orientation, lenghtOfConformity, pointsOfOrientation) = VesselOrientation.vessel_orientation(golden_truth, candidatePoint, 0, math.pi*2)
        print(f"for point {candidatePoint}: {(orientation, lenghtOfConformity, pointsOfOrientation)}")
        draw_orientation_line(image_with_circle, pointsOfOrientation)
    image_with_circle = draw_small_circle(image_with_circle, candidatePoints[3])
    cv2.imshow("image_with_circle", image_with_circle)
    cv2.waitKey(0)
    #VesselOrientation.get_point_from_angle_and_distance()

    nextPoint = [candidatePoints[3][0], candidatePoints[3][1]]
    (orientation, _, pointsOfOrientation) = VesselOrientation.vessel_orientation(golden_truth, nextPoint, math.pi, math.pi*2)
    #for iteration in range(25):
    #    nextPoint = get_next_point(nextPoint, pointsOfOrientation)
    #    (orientation, lenghtOfConformity, pointsOfOrientation) = VesselOrientation.vessel_orientation(golden_truth, nextPoint, orientation-(angleStep*3), orientation+(angleStep*3))
    #    
    #    print(f"Oriantation: {orientation}, next point:{pointsOfOrientation[1]}")
    #    draw_orientation_line(image_with_circle, pointsOfOrientation)
    #    image_with_circle = draw_small_circle(image_with_circle, pointsOfOrientation[1])
    #    cv2.imshow("image_with_circle", image_with_circle)
    #    cv2.waitKey(0)
    # TADY 
    
    middlePoint = [x,y]

    print("Start")
    for candidatePoint in candidatePoints:
        print("ITARETION")
        print(f"BEFORE middle {middlePoint} dalsi {candidatePoint}")
        angleBetweenMiddleAndCandidate = angle_between_middle_and_candidate(middlePoint,candidatePoint)
        angleBetweenMiddleAndCandidate = quadrant_angle(middlePoint, candidatePoint, angleBetweenMiddleAndCandidate)
        print(f"Quadrant angle => {angleBetweenMiddleAndCandidate} rad => {math.degrees(angleBetweenMiddleAndCandidate)}")
        minLookingAngle = angleBetweenMiddleAndCandidate - math.pi/2
        maxLookingAngle = angleBetweenMiddleAndCandidate + math.pi/2
        print(f"minLookingAngle: {minLookingAngle}, maxLookingAngle: {maxLookingAngle}")
        (orientation, lenghtOfConformity, pointsOfOrientation) = VesselOrientation.vessel_orientation(golden_truth, candidatePoint, minLookingAngle, maxLookingAngle)
        print(f"for point {candidatePoint}: {(orientation, lenghtOfConformity, pointsOfOrientation)}")
        pointsFromMiddleToCandidate = VesselOrientation.get_points_on_line(middlePoint, angleBetweenMiddleAndCandidate, radius)
        draw_orientation_line(image_with_circle, pointsOfOrientation, lineColor=(138,43,226))
        draw_orientation_line(image_with_circle, pointsFromMiddleToCandidate, lineColor=(98,255,88))
    
    cv2.imshow("image_with_circle", image_with_circle)
    cv2.waitKey(0)
    cv2.imwrite(DataPaths.results_image_path("candidatePointsWithOrientations"), image_with_circle)
    exit()

    candidatePoint = candidatePoints[0]
    angleBetweenMiddleAndCandidate = angle_between_middle_and_candidate(middlePoint,candidatePoint)
    angleBetweenMiddleAndCandidate = quadrant_angle(middlePoint, swap_point_coordinates(candidatePoint), angleBetweenMiddleAndCandidate)
    print(f"Quadrant angle => {angleBetweenMiddleAndCandidate} rad => {math.degrees(angleBetweenMiddleAndCandidate)}")
    minLookingAngle = angleBetweenMiddleAndCandidate - math.pi/2
    maxLookingAngle = angleBetweenMiddleAndCandidate + math.pi/2
    print(f"minLookingAngle: {minLookingAngle}, maxLookingAngle: {maxLookingAngle}")
    (orientation, lenghtOfConformity, pointsOfOrientation) = VesselOrientation.vessel_orientation(golden_truth, candidatePoint, minLookingAngle, maxLookingAngle)
    currnetPoint = [candidatePoints[0][1], candidatePoints[0][0]]
    print("SEEKING\n\n")
    
    for iteration in range(15):
        print(f"BEFORE middle {currnetPoint} dalsi {pointsOfOrientation[2]}")
        angleBetweenOldAndNew = angle_between_middle_and_candidate(currnetPoint,pointsOfOrientation[2])
        angleBetweenOldAndNew = quadrant_angle(currnetPoint, swap_point_coordinates(pointsOfOrientation[2]), angleBetweenOldAndNew)
        print(f"Quadrant angle => {angleBetweenMiddleAndCandidate} rad => {math.degrees(angleBetweenMiddleAndCandidate)}")
        minLookingAngle = angleBetweenMiddleAndCandidate - math.pi/2
        maxLookingAngle = angleBetweenMiddleAndCandidate + math.pi/2
        print(f"minLookingAngle: {minLookingAngle}, maxLookingAngle: {maxLookingAngle}")
        (orientation, lenghtOfConformity, pointsOfOrientation) = VesselOrientation.vessel_orientation(golden_truth, swap_point_coordinates(currnetPoint), minLookingAngle, maxLookingAngle)

        image_with_circle[currnetPoint[1], currnetPoint[0]] = (255,0,0)
        currnetPoint = [pointsOfOrientation[2][1], pointsOfOrientation[2][0]]


    cv2.imwrite(DataPaths.results_image_path("candidatePointsWithOrientations"), image_with_circle)
    cv2.imshow("image_with_circle", image_with_circle)
    cv2.waitKey(0)