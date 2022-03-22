import math
import cv2
import numpy as np

def get_point_from_angle_and_distance(originalPoint, angle, distance):
    newY = int(distance * math.cos(angle))
    newX = int(distance * math.sin(angle))
    return [originalPoint[0] + newX, originalPoint[1] + newY]

def get_points_on_line(originalPoint, angle, lenght):
    pointsOnLine = []
    for distance in range(lenght):
        pointsOnLine.append(get_point_from_angle_and_distance(originalPoint, angle, distance))
    return pointsOnLine

def get_max_points_on_line(groundTruth, originalPoint, angle):
    vesselPointsOnLine = []
    distanceFromOrigin = 0
    while True:
        nextPoint = get_point_from_angle_and_distance(originalPoint, angle, distanceFromOrigin)
        if groundTruth[nextPoint[1]][nextPoint[0]] != 255:
            break
        vesselPointsOnLine.append(nextPoint)
        distanceFromOrigin += 1
    return vesselPointsOnLine

def find_middle_element(input_list):
    #print(f"vessel_middle => {input_list}")
    middle = float(len(input_list))/2
    if middle % 2 != 0:
        return input_list[int(middle - .5)]
    else:
        return input_list[int(middle)]

def vessel_middle(groundTruth, originalPoint):
    #print(f"vessel_middle => {originalPoint}")
    angleOriginal = math.pi / 12
    smallestWidth = 30000 # nonsence value
    bestMiddlePoint = [originalPoint[0], originalPoint[1]]
    for angleMultiplyer in range(12):
        currentAngle = angleOriginal * angleMultiplyer
        currentAngleOpposite = (angleOriginal * angleMultiplyer) + math.pi
        pointsOnLineCurrentAngle = get_max_points_on_line(groundTruth, originalPoint, currentAngle)
        pointsOnLineCurrentAngleOpposite = get_max_points_on_line(groundTruth, originalPoint, currentAngleOpposite)

        if len(pointsOnLineCurrentAngle) > 0 and len(pointsOnLineCurrentAngleOpposite) > 0:
            if are_coordinates_same(pointsOnLineCurrentAngle[0], pointsOnLineCurrentAngleOpposite[0]):
                del pointsOnLineCurrentAngleOpposite[0]
        pointsOnLineCurrentAngleOpposite.reverse()
        allPointOnLine = pointsOnLineCurrentAngleOpposite + pointsOnLineCurrentAngle
        currentWidth = len(allPointOnLine)
        if currentWidth < smallestWidth and currentWidth > 0:
            smallestWidth = smallestWidth
            bestMiddlePoint = find_middle_element(allPointOnLine)
    #print(f"returning => {bestMiddlePoint}")
    return bestMiddlePoint

def vessel_width(groundTruth, originalPoint):
    angleOriginal = math.pi / 12
    smallestWidth = 30000 # nonsence value
    for angleMultiplyer in range(12):
        currentAngle = angleOriginal * angleMultiplyer
        currentAngleOpposite = (angleOriginal * angleMultiplyer) + math.pi
        pointsOnLineCurrentAngle = get_max_points_on_line(groundTruth, originalPoint, currentAngle)
        pointsOnLineCurrentAngleOpposite = get_max_points_on_line(groundTruth, originalPoint, currentAngleOpposite)

        if len(pointsOnLineCurrentAngle) > 0 and len(pointsOnLineCurrentAngleOpposite) > 0:
            if are_coordinates_same(pointsOnLineCurrentAngle[0], pointsOnLineCurrentAngleOpposite[0]):
                del pointsOnLineCurrentAngleOpposite[0]
        pointsOnLineCurrentAngleOpposite.reverse()
        allPointOnLine = pointsOnLineCurrentAngleOpposite + pointsOnLineCurrentAngle
        currentWidth = len(allPointOnLine)
        if currentWidth < smallestWidth:
            smallestWidth = currentWidth
    return smallestWidth

def satisfactory_angles(groundTruth, originalPoint, minAngle, maxAngle):
    angleOriginal = math.pi / 12
    angles = []
    currentAngle = math.pi / 12
    for angleMultiplyer in range(24):
        currentAngle = angleOriginal * angleMultiplyer
        if not is_angle_in_range(currentAngle, minAngle, maxAngle):
            continue
            
        pointsOnLine = get_max_points_on_line(groundTruth, originalPoint, currentAngle)
        noOfSuitedPixels = len(pointsOnLine)
        angles.append([noOfSuitedPixels, currentAngle])
    return angles

def filter_angles(anglesWithLenght, width):
    satisfactoryAngles = []
    for lenght, angle in anglesWithLenght:
        
        widthDouble = width*2
        print(f"lenght <> widthDouble | {lenght} <> {widthDouble}")
        if lenght >= widthDouble:
            satisfactoryAngles.append([lenght, angle])
    
    if len(satisfactoryAngles) == 0:
        for lenght, angle in anglesWithLenght:
            
            print(f"lenght <> width | {lenght} <> {width}")
            if lenght >= width:
                satisfactoryAngles.append([lenght, angle])
        longestLineLenght = max([sublist[0] for sublist in satisfactoryAngles])
        bestConformity = [ [l,a] for l,a in satisfactoryAngles if l == longestLineLenght][0]
        return [bestConformity]

    if len(satisfactoryAngles) == 0:
        return []
    if len(satisfactoryAngles) == 1:
        return satisfactoryAngles
    # more angles
    # find longest line in angles
    print(f"satisfactoryAngles => {satisfactoryAngles}")
    longestLineLenght = max([sublist[0] for sublist in satisfactoryAngles])
    print(f"longest line lenght => {longestLineLenght}")
    # filter only angles that are more than 30% from longestLineLenght
    bestConformity = [ [l,a] for l,a in satisfactoryAngles if l == longestLineLenght][0]
    print(f"bestConformity => {bestConformity}")
    filtered = [bestConformity]
    for currentLenghtWithAngle in satisfactoryAngles:
        if angle_diff(bestConformity[1], currentLenghtWithAngle[1]) > (math.pi/6):
            filtered.append(currentLenghtWithAngle)
    return filtered

def angle_diff(angle1, angle2):
    bigger = 0
    smaller = 0
    if angle1 > angle2:
        bigger = angle1
        smaller = angle2
    else:
        bigger = angle2
        smaller = angle1
    return bigger - smaller

def are_coordinates_same(point1, point2):
    if point1[0] == point2[0] and point1[1] == point2[1]:
        return True
    return False

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
    angleOriginal = math.pi / 12
    vesselOrientation = 0
    noOfMostSuitedPixels = 0
    pointsOfBestConformity = []
    currentAngle = math.pi / 12
    for angleMultiplyer in range(24):
        currentAngle = angleOriginal * angleMultiplyer
        if not is_angle_in_range(currentAngle, minAngle, maxAngle):
            continue
            
        pointsOnLine = get_max_points_on_line(groundTruth, originalPoint, currentAngle)
        suitedPixels = len(pointsOnLine)
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