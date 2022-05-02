from ast import Return
import math
import cv2
import numpy as np
import OdLocalization
import CircleCoordinationFinder
import Main
import skeletonize
import VesselOrientation
import DataPaths
import matplotlib.pyplot as plt



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

def is_point_in_image(point, imageShape):
    if point[1] >= imageShape[0] or point[0] >= imageShape[1]:
        return False
    return True

def start_from_non_vessel(groundTruth, circlePoints):
    """ Finds element in the middle of @input_list.

    @type groundTruth: [[uint8]]
    @param groundTruth: manualy segmented vessels
    @type circlePoints: [[int,int]]
    @param circlePoints: list of points, representing circle

    @rtype: object
    @returns: Object in middle of @input_list."""

    filteredCirclePoints = []
    height, width = groundTruth.shape
    for point in circlePoints:
        if width > point[0] and height > point[1]:
            filteredCirclePoints.append(point)


    while groundTruth[filteredCirclePoints[0][1]][filteredCirclePoints[0][0]] == 255:
        #print(f"First point is: {circlePoints[0]} with value: {groundTruth[circlePoints[0][1]][circlePoints[0][0]]}")
        tempPoint = [filteredCirclePoints[0][0], filteredCirclePoints[0][1]]
        filteredCirclePoints.remove(filteredCirclePoints[0])
        filteredCirclePoints.append(tempPoint)
    circlePoints = filteredCirclePoints

def generate_next_point(vesselMiddlePoint, currentPoint, angle, possibleMaxDistance):
    distance = 2
    while distance <= possibleMaxDistance:
        nextPoint = VesselOrientation.get_point_from_angle_and_distance(vesselMiddlePoint, angle, distance)
        if not VesselOrientation.are_coordinates_same(nextPoint, currentPoint):
            return nextPoint
        distance = distance + 1
    raise Exception(f"Starting at point {currentPoint}, but there is no more available points further than {distance}. {nextPoint} is not satisfactory.")


def track_candidate_point_one_step(lastPoint, currentPoint, goldenTruth, imageForDrawing):
    imageShape = goldenTruth.shape
    angleBetweenLastPointAndNewOne = angle_between_middle_and_candidate(lastPoint,currentPoint)
    angleBetweenLastPointAndNewOne = quadrant_angle(lastPoint, currentPoint, angleBetweenLastPointAndNewOne)
    minAngle = angleBetweenLastPointAndNewOne - (math.pi/4)
    maxAngle = angleBetweenLastPointAndNewOne + (math.pi/4)
    satisfactoryAngles = VesselOrientation.satisfactory_angles(goldenTruth, currentPoint, minAngle, maxAngle)
    filteredAngles = VesselOrientation.filter_angles(satisfactoryAngles, VesselOrientation.vessel_width(goldenTruth, currentPoint))

    if len(filteredAngles) > 0:
        nextPoint = VesselOrientation.get_point_from_angle_and_distance(currentPoint, filteredAngles[0][1], 2)

        if goldenTruth[nextPoint[1]][nextPoint[0]] != 255:
            return [False, [0,0]]

        if not is_point_in_image(nextPoint, imageShape):
            return [False, [0,0]]
        
        if len(filteredAngles) > 1:
            imageForDrawing[nextPoint[1]][nextPoint[0]] = (255,20,147)
        else:
            imageForDrawing[nextPoint[1]][nextPoint[0]] = (255,125,0)
        return [True, nextPoint]
    return [False, [0,0]]
    

def track_candidate_point(middlePoint, originalPoint, goldenTruth, newDrawingImage, wait=False):
    lastPoint = originalPoint
    repeatCondition, currentPoint = track_candidate_point_one_step(middlePoint, originalPoint,goldenTruth, newDrawingImage)
    if wait:
        plt_image = cv2.cvtColor(newDrawingImage, cv2.COLOR_BGR2RGB)
        plt.imshow(plt_image)
        plt.waitforbuttonpress()
    while repeatCondition:
        repeatCondition, nextPoint = track_candidate_point_one_step(lastPoint, currentPoint,goldenTruth, newDrawingImage)
        lastPoint = currentPoint
        currentPoint = nextPoint
        if wait:
            plt_image = cv2.cvtColor(newDrawingImage, cv2.COLOR_BGR2RGB)
            plt.imshow(plt_image)
            plt.waitforbuttonpress()  

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
    #print(f"Middle of circle is: {middlePoint}, candidatePoint is: {candidatePoint}")
    x_diff = coordinate_difference(candidatePoint[0], middlePoint[0])
    y_diff = coordinate_difference(candidatePoint[1], middlePoint[1])
    
    rad = math.pi/2 - math.atan2(y_diff, x_diff)
    #print(f"rad\t=> {rad}")
    #print(f"Triangle \nY: {y_diff}\nX: {x_diff}\n aplha: {math.degrees(rad)}")
    return rad

def quadrant_angle(middleRefencePoint, point, angle):
    if angle == 0.0:
        if middleRefencePoint[1] > point[1]:
            return math.pi
        return 0.0
            
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
    golden_truth = Main.read_mask_image(DataPaths.original_manual_image_path(imageNumber))
    src = cv2.imread(DataPaths.original_image_path(imageNumber))
    radius = 45

    B_channel, G_channel, R_channel = cv2.split(src)
    (x, y) = OdLocalization.image_od_localization(G_channel)
    image_with_circle = cv2.circle(cv2.merge((golden_truth,golden_truth,golden_truth)), (x, y), radius, (0, 0, 255), 2)

    cv2.imwrite(DataPaths.results_image_path("localizedOD"), image_with_circle)
        

    circle_coordinates = CircleCoordinationFinder.listOfCoordinates(radius, x_of_middle=x, y_of_middle=y)
    candidatePoints = find_middle_pixels_on_circle(golden_truth, circle_coordinates)
    #print("Start original")
    pointsImage= cv2.merge((golden_truth,golden_truth,golden_truth))
    for candidatePoint in candidatePoints:
        pointsImage = cv2.circle(pointsImage, candidatePoint, radius=2,color = (0,0,255), thickness=-1)
    cv2.imwrite(DataPaths.results_image_path("localizedOD_with_points"), pointsImage)
    for candidatePoint in candidatePoints:
        (orientation, lenghtOfConformity, pointsOfOrientation) = VesselOrientation.vessel_orientation(golden_truth, candidatePoint, 0, math.pi*2)
        #print(f"for point {candidatePoint}: {(orientation, lenghtOfConformity, pointsOfOrientation)}")
        draw_orientation_line(image_with_circle, pointsOfOrientation)
    image_with_circle = draw_small_circle(image_with_circle, candidatePoints[3])
    cv2.imshow("image_with_circle", image_with_circle)
    cv2.waitKey(0)
    #VesselOrientation.get_point_from_angle_and_distance()

    nextPoint = [candidatePoints[3][0], candidatePoints[3][1]]
    (orientation, _, pointsOfOrientation) = VesselOrientation.vessel_orientation(golden_truth, nextPoint, math.pi, math.pi*2)

    
    middlePoint = [x,y]

    newDrawingImage = cv2.merge((golden_truth,golden_truth,golden_truth))


    
    middlePoint = [x,y]
    track_candidate_point(middlePoint, candidatePoints[1], golden_truth, newDrawingImage)
    track_candidate_point(middlePoint, candidatePoints[2], golden_truth, newDrawingImage)
    #track_candidate_point(middlePoint, candidatePoints[3], golden_truth, newDrawingImage)
    cv2.imwrite(DataPaths.results_image_path("result_of_tracking"), newDrawingImage)
    plt_image = cv2.cvtColor(newDrawingImage, cv2.COLOR_BGR2RGB)
    plot = plt.imshow(plt_image)
    while True:
        plt.waitforbuttonpress()