import math

from numpy import ufunc
import Main
import copy
import cv2
import DataPaths
from skimage.morphology import skeletonize
import OdLocalization
import CircleCoordinationFinder
import CandidatePoints
import VesselOrientation

def save_and_show_progress(imageForDrawing):
    cv2.imshow("test",imageForDrawing)
    cv2.imwrite(DataPaths.results_image_path("SkeletonizeCandidatePoints"),imageForDrawing)
    cv2.waitKey(0)

def find_vessels_in_neighborhood(skeletonizedImage, currentLocation, neighborhoodSize, minAngle, maxAngle):
    neighborhood = get_neighborhood_coordinates(currentLocation, neighborhoodSize, minAngle, maxAngle)
    vesselPixels = []

    for coordinateIndex in range(0, len(neighborhood)):
        if skeletonizedImage[neighborhood[coordinateIndex][1], neighborhood[coordinateIndex][0]] == 255:
            if is_index_background_or_out_of_array(skeletonizedImage, neighborhood, coordinateIndex+1):
                vesselPixels.append(neighborhood[coordinateIndex])

    return vesselPixels

def is_index_background_or_out_of_array(skeletonizedImage, neighborhood, nextIndex):
    if nextIndex >= len(neighborhood):
        return True
    if skeletonizedImage[neighborhood[nextIndex][1], neighborhood[nextIndex][0]] == 0:
        return True
    return False 

def get_neighborhood_coordinates(middlePoint, neighborhoodSize, minAngle, maxAngle):
    if neighborhoodSize % 2 != 1:
        raise Exception(f"Neighborhood invalid size => {neighborhoodSize}")

    halfOfSize = neighborhoodSize // 2

    returnedCoordinates = []
    for rowAdditon in range(0-halfOfSize,halfOfSize+1):
        addedPoint = [middlePoint[0]+rowAdditon, middlePoint[1]+(0-halfOfSize)]
        #print(f"Adding {addedPoint}")
        returnedCoordinates.append(addedPoint)

    for columnAdditon in range(1-halfOfSize,halfOfSize):
        addedPoint = [middlePoint[0]+halfOfSize, middlePoint[1]+columnAdditon]
        #print(f"Adding {addedPoint}")
        returnedCoordinates.append(addedPoint)
    
    for rowAdditon in range(halfOfSize,0-halfOfSize-1, -1):
        addedPoint = [middlePoint[0]+rowAdditon, middlePoint[1]+halfOfSize]
        #print(f"Adding {addedPoint}")
        returnedCoordinates.append(addedPoint)
        
    for columnAdditon in range(halfOfSize - 1,0-halfOfSize, -1):
        addedPoint = [middlePoint[0]-halfOfSize, middlePoint[1]+columnAdditon]
        #print(f"Adding {addedPoint}")
        returnedCoordinates.append(addedPoint)
           
                
    

    finalPoints = []

    for point in returnedCoordinates:
        angleBetweenLastPointAndNewOne = CandidatePoints.angle_between_middle_and_candidate(middlePoint, point)
        angleBetweenLastPointAndNewOne = CandidatePoints.quadrant_angle(middlePoint, point, angleBetweenLastPointAndNewOne)
        if VesselOrientation.is_angle_in_range(angleBetweenLastPointAndNewOne, minAngle, maxAngle):
            finalPoints.append(point)


    return finalPoints
    

def are_colors_same(color1,color2):
    if color1[0] != color2[0]:
        return False
    if color1[1] != color2[1]:
        return False
    if color1[2] != color2[2]:
        return False
    return True
    

def find_next_points(skeletonizedImage, previousPoint, currentPoint, imageForDrawing, neighborhoodSize):

    tempAngle = CandidatePoints.angle_between_middle_and_candidate(previousPoint,currentPoint)
    startingAngle = CandidatePoints.quadrant_angle(previousPoint, currentPoint, tempAngle)

    minAngle = startingAngle - math.pi/2
    maxAngle = startingAngle + math.pi/2

    vesselsInNeighborhood = find_vessels_in_neighborhood(skeletonizedImage, currentPoint, neighborhoodSize, minAngle, maxAngle)

    nonGreenPixels = []

    for pixel in vesselsInNeighborhood:
        pixelValue = imageForDrawing[pixel[1], pixel[0]]
        if not are_colors_same(pixelValue, greenPixel):
            nonGreenPixels.append(pixel)

    for vesselPixelCoordinates in nonGreenPixels:
        imageForDrawing[vesselPixelCoordinates[1], vesselPixelCoordinates[0]] = (255, 0, 0)
    if len(nonGreenPixels) > 0:
        #print(f"found next point {vesselsInNeighborhood[0]}")
        return nonGreenPixels
    print("No new points found")
    return []

def find_next_points_in_both_areas(skeletonizedImage, previousPoint, currentPoint, imageForDrawing):
    nextCurrentPoints = find_next_points(skeletonizedImage, previousPoint, currentPoint, imageForDrawing, 3)
    if not nextCurrentPoints:
        nextCurrentPoints = find_next_points(skeletonizedImage, previousPoint, currentPoint, imageForDrawing, 5)
    return nextCurrentPoints
        
    

def try_path(lastMainVesselPoint, startingPoint, originalAngle, skeletonizedImage, imageForDrawing):

    lastPoint = [startingPoint[0],startingPoint[1]]
    nextPoints = find_next_points(skeletonizedImage, lastMainVesselPoint, lastPoint, imageForDrawing, 3)
    minAllowedAngle = originalAngle - math.pi/4
    maxAllowedAngle = originalAngle + math.pi/4

    for _ in range(5):
        if len(nextPoints) < 1:
            return True
        
        if len(nextPoints) > 1:
            return True
        
        imageForDrawing[nextPoints[0][1], nextPoints[0][0]] = redPixel

        tempCurrentPoint = [nextPoints[0][0], nextPoints[0][1]]
        tempAngle = CandidatePoints.angle_between_middle_and_candidate(lastPoint,tempCurrentPoint)
        lastAngle = CandidatePoints.quadrant_angle(lastPoint, tempCurrentPoint, tempAngle)

        if not VesselOrientation.is_angle_in_range(lastAngle, minAllowedAngle, maxAllowedAngle):
            return False
        
        nextPointsTemp = find_next_points_in_both_areas(skeletonizedImage, lastPoint, tempCurrentPoint, imageForDrawing)
        lastPoint = [nextPoints[0][0], nextPoints[0][1]]
        nextPoints = nextPointsTemp
        
            
        
    return True
    

def find_end_of_candidate_point(odMiddlePoint, startingPoint, skeletonizedImage, imageForDrawing):
    tempAngle = CandidatePoints.angle_between_middle_and_candidate(odMiddlePoint,startingPoint)
    startingAngle = CandidatePoints.quadrant_angle(odMiddlePoint, startingPoint, tempAngle)

    minAngle = startingAngle - math.pi/2
    maxAngle = startingAngle + math.pi/2

    vesselsInNeighborhood = find_vessels_in_neighborhood(skeletonizedImage, startingPoint, neighborhoodSize, minAngle, maxAngle)
    lastVesselPointFound = [startingPoint[0], startingPoint[1]]

    for vesselPixelCoordinates in vesselsInNeighborhood:
        imageForDrawing[vesselPixelCoordinates[1], vesselPixelCoordinates[0]] = bluePixel
    
    
    for vesselPixelCoordinates in vesselsInNeighborhood:
        currentPoint = [vesselPixelCoordinates[0], vesselPixelCoordinates[1]]
        print(f"currentPoint: {currentPoint}")
        while currentPoint:
            nextCurrentPoints = find_next_points_in_both_areas(skeletonizedImage, lastVesselPointFound, currentPoint, imageForDrawing)
            
            if len(nextCurrentPoints) > 1:
                for nextPathPoint in nextCurrentPoints:
                    tempAngle = CandidatePoints.angle_between_middle_and_candidate(currentPoint,nextPathPoint)
                    allowedAngle = CandidatePoints.quadrant_angle(currentPoint, nextPathPoint, tempAngle)
                    if try_path(lastVesselPointFound, nextPathPoint, allowedAngle, skeletonizedImage, imageForDrawing):
                        find_end_of_candidate_point(lastVesselPointFound, nextPathPoint, skeletonizedImage, imageForDrawing)
                    else:
                        print("Path bad")
                break
            
            if not nextCurrentPoints:
                print("No more points")
                break
            
            imageForDrawing[nextCurrentPoints[0][1], nextCurrentPoints[0][0]] = greenPixel

            lastVesselPointFound = [currentPoint[0], currentPoint[1]]
            currentPoint = [nextCurrentPoints[0][0], nextCurrentPoints[0][1]]

        save_and_show_progress(imageForDrawing)

    return
    
    

if __name__ == "__main__":
    greenPixel = (0,255,0)
    bluePixel = (255,0,0)
    redPixel = (0,0,255)
    imageNumber = 1
    golden_truth = Main.read_mask_image(DataPaths.original_manual_image_path(), "DRIVE")
    skepetonizeInput = copy.deepcopy(golden_truth)

    src = cv2.imread(DataPaths.original_image_path(imageNumber))
    radius = 45

    _, G_channel, _ = cv2.split(src)
    odMiddlePoint = OdLocalization.image_od_localization(G_channel)
    circle_coordinates = CircleCoordinationFinder.listOfCoordinates(radius, x_of_middle=odMiddlePoint[0], y_of_middle=odMiddlePoint[1])
    candidatePoints = CandidatePoints.find_middle_pixels_on_circle(golden_truth, circle_coordinates)




    (columns, rows) = skepetonizeInput.shape
    for x in range(columns):
        for y in range(rows):
            if skepetonizeInput[x ,y] != 0:
                skepetonizeInput[x ,y] = 1
    skeletonized = skeletonize(skepetonizeInput)
    skeletonized = skeletonized.astype("uint8")
    for x in range(columns):
        for y in range(rows):
            if skeletonized[x ,y] != 0:
                skeletonized[x ,y] = 255

    imageForDrawing = cv2.merge((skeletonized,skeletonized,skeletonized))
    neighborhoodSize = 3
    lastVesselPointFound = []

    startingPoints = []
    
    for candidatePoint in candidatePoints:
        surrounding = get_neighborhood_coordinates(candidatePoint, neighborhoodSize, 0, math.pi*2)
        for pointCoordinate in surrounding:
            imageForDrawing[pointCoordinate[1], pointCoordinate[0]] = redPixel
        print(f"Hledame pro point {candidatePoint}")
        vesselsInNeighborhood = find_vessels_in_neighborhood(skeletonized, candidatePoint,neighborhoodSize, 0, math.pi*2)
        if len(vesselsInNeighborhood) > 0:
            print(f"Candidate point {vesselsInNeighborhood[0]} found")
            startingPoints.append([vesselsInNeighborhood[0][0], vesselsInNeighborhood[0][1]])
            imageForDrawing[vesselsInNeighborhood[0][1], vesselsInNeighborhood[0][0]] = greenPixel
        

    for startingPoint in startingPoints:
        print(f"Candidate point {startingPoint} ++++++++++++++++++++")
        find_end_of_candidate_point(odMiddlePoint, startingPoint, skeletonized, imageForDrawing)
    save_and_show_progress(imageForDrawing)
    cv2.imwrite(DataPaths.results_image_path("Skeletonized"),skeletonized)


    

    

