import math
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

    for columnAdditon in range(1-halfOfSize,halfOfSize+1):
        addedPoint = [middlePoint[0]+halfOfSize, middlePoint[1]+columnAdditon]
        #print(f"Adding {addedPoint}")
        returnedCoordinates.append(addedPoint)
    
    for rowAdditon in range(halfOfSize,0-halfOfSize-1, -1):
        addedPoint = [middlePoint[0]+rowAdditon, middlePoint[1]+halfOfSize]
        #print(f"Adding {addedPoint}")
        returnedCoordinates.append(addedPoint)
        
    for columnAdditon in range(halfOfSize,0-halfOfSize, -1):
        addedPoint = [middlePoint[0]-halfOfSize, middlePoint[1]+columnAdditon]
        #print(f"Adding {addedPoint}")
        returnedCoordinates.append(addedPoint)
           
                
    

    finalPoints = []

    for point in returnedCoordinates:
        angleBetweenLastPointAndNewOne = CandidatePoints.angle_between_middle_and_candidate(middlePoint,point)
        angleBetweenLastPointAndNewOne = CandidatePoints.quadrant_angle(middlePoint, point, angleBetweenLastPointAndNewOne)
        if VesselOrientation.is_angle_in_range(angleBetweenLastPointAndNewOne, minAngle, maxAngle):
            finalPoints.append(point)


    return finalPoints
    

def find_next_point(skeletonizedImage, previousPoint, currentPoint, imageForDrawing, neighborhoodSize):

    tempAngle = CandidatePoints.angle_between_middle_and_candidate(previousPoint,currentPoint)
    startingAngle = CandidatePoints.quadrant_angle(previousPoint, currentPoint, tempAngle)

    minAngle = startingAngle - math.pi/2
    maxAngle = startingAngle + math.pi/2

    vesselsInNeighborhood = find_vessels_in_neighborhood(skeletonizedImage, currentPoint, neighborhoodSize, minAngle, maxAngle)

    for vesselPixelCoordinates in vesselsInNeighborhood:
        imageForDrawing[vesselPixelCoordinates[1], vesselPixelCoordinates[0]] = bluePixel
    if len(vesselsInNeighborhood) > 0:
        print(f"found next point {vesselsInNeighborhood[0]}")
        
        imageForDrawing[vesselsInNeighborhood[0][1], vesselsInNeighborhood[0][0]] = greenPixel
        return vesselsInNeighborhood[0]
    print("No new points found")
    return []

def find_end_of_candidate_point(odMiddlePoint, startingPoint, skeletonizedImage, imageForDrawing):
    tempAngle = CandidatePoints.angle_between_middle_and_candidate(odMiddlePoint,startingPoint)
    startingAngle = CandidatePoints.quadrant_angle(odMiddlePoint, startingPoint, tempAngle)

    minAngle = startingAngle - math.pi/2
    maxAngle = startingAngle + math.pi/2

    vesselsInNeighborhood = find_vessels_in_neighborhood(skeletonizedImage, startingPoint, neighborhoodSize, minAngle, maxAngle)
    lastVesselPointFound = [startingPoint[0], startingPoint[1]]

    for vesselPixelCoordinates in vesselsInNeighborhood:
        imageForDrawing[vesselPixelCoordinates[1], vesselPixelCoordinates[0]] = bluePixel
    if len(vesselsInNeighborhood) > 0:
        print(f"found next point {vesselsInNeighborhood[0]}")
        
        currentPoint = [vesselsInNeighborhood[0][0], vesselsInNeighborhood[0][1]]
        print(f"currentPoint: {currentPoint}")
        imageForDrawing[vesselsInNeighborhood[0][1], vesselsInNeighborhood[0][0]] = greenPixel
        while currentPoint:
            nextCurrentPoint = find_next_point(skeletonizedImage, lastVesselPointFound, currentPoint, imageForDrawing, neighborhoodSize)
            
            if not nextCurrentPoint:
                print("Advanced search")
                nextCurrentPoint = find_next_point(skeletonizedImage, lastVesselPointFound, currentPoint, imageForDrawing, 5)
                if not nextCurrentPoint:
                    print("No more points")
                    
                    break
            lastVesselPointFound = [currentPoint[0], currentPoint[1]]
            currentPoint = [nextCurrentPoint[0], nextCurrentPoint[1]]
            print("ITERATION ++++++++++")
            print(f"lastVesselPointFound: {lastVesselPointFound}")
            print(f"currentPoint: {currentPoint}")

        save_and_show_progress(imageForDrawing)
    else:
        print("No next point found in neigbourhood of starting pixel")
    return
    

if __name__ == "__main__":
    greenPixel = (0,255,0)
    bluePixel = (255,0,0)
    redPixel = (0,0,255)
    imageNumber = 1
    golden_truth = Main.read_mask_image(DataPaths.original_manual_image_path())
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
        find_end_of_candidate_point(odMiddlePoint, startingPoint, skeletonized, imageForDrawing)
    save_and_show_progress(imageForDrawing)


    

    

