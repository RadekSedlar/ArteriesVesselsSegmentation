import math
import random
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

def find_white_vessels_in_neighborhood(currentLocation, minAngle, maxAngle, imageForDrawing):
    neighborhood = get_neighborhood_coordinates(currentLocation, 3, minAngle, maxAngle)
    vesselPixels = []
    numOfVesselPixelsInSmallNeighborhood = 0

    for coordinateIndex in range(0, len(neighborhood)):
        if are_colors_same(imageForDrawing[neighborhood[coordinateIndex][1], neighborhood[coordinateIndex][0]], whitePixel):
            numOfVesselPixelsInSmallNeighborhood += 1
            if is_index_background_or_out_of_array_colored_image(imageForDrawing, neighborhood, coordinateIndex+1):
                vesselPixels.append(neighborhood[coordinateIndex])

    if numOfVesselPixelsInSmallNeighborhood != len(vesselPixels):
        vesselPixels = []

    if len(vesselPixels) == 0:
        neighborhood = get_neighborhood_coordinates(currentLocation, 5, minAngle, maxAngle)
        for coordinateIndex in range(0, len(neighborhood)):
            if are_colors_same(imageForDrawing[neighborhood[coordinateIndex][1], neighborhood[coordinateIndex][0]], whitePixel):
                if is_index_background_or_out_of_array_colored_image(imageForDrawing, neighborhood, coordinateIndex+1):
                    vesselPixels.append(neighborhood[coordinateIndex])
        
    return vesselPixels

def find_vessels_in_neighborhood(skeletonizedImage, currentLocation, neighborhoodSize, minAngle, maxAngle):
    neighborhood = get_neighborhood_coordinates(currentLocation, neighborhoodSize, minAngle, maxAngle)
    vesselPixels = []

    for coordinateIndex in range(0, len(neighborhood)):
        if skeletonizedImage[neighborhood[coordinateIndex][1], neighborhood[coordinateIndex][0]] == 255:
            if is_index_background_or_out_of_array(skeletonizedImage, neighborhood, coordinateIndex+1):
                vesselPixels.append(neighborhood[coordinateIndex])

    return vesselPixels

def find_colors_in_neighborhood(image, currentLocation):
    neighborhood = get_neighborhood_coordinates(currentLocation, 3, 0, math.pi*2)
    for coordinateIndex in range(0, len(neighborhood)):
        if are_colors_same(image[neighborhood[coordinateIndex][1], neighborhood[coordinateIndex][0]], bluePixel):
            return bluePixel
        if are_colors_same(image[neighborhood[coordinateIndex][1], neighborhood[coordinateIndex][0]], redPixel):
            return redPixel

    return whitePixel

def is_index_background_or_out_of_array(skeletonizedImage, neighborhood, nextIndex):
    if nextIndex >= len(neighborhood):
        return True
    if skeletonizedImage[neighborhood[nextIndex][1], neighborhood[nextIndex][0]] == 0:
        return True
    return False 

def is_index_background_or_out_of_array_colored_image(skeletonizedImage, neighborhood, nextIndex):
    if nextIndex >= len(neighborhood):
        return True
    if are_colors_same(skeletonizedImage[neighborhood[nextIndex][1], neighborhood[nextIndex][0]], blackPixel):
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
    
def get_angle_between_two_points(pointMiddle, pointOnCircle):
    tempAngle = CandidatePoints.angle_between_middle_and_candidate(pointMiddle,pointOnCircle)
    circleAngle = CandidatePoints.quadrant_angle(pointMiddle, pointOnCircle, tempAngle)
    return circleAngle

def apply_skeletonization(skepetonizeInput):
    (columns, rows) = skepetonizeInput.shape
    for x in range(columns):
        for y in range(rows):
            if skepetonizeInput[x ,y] != 0:
                skepetonizeInput[x ,y] = 1
    skeletonized = skeletonize(skepetonizeInput, method='lee')
    skeletonized = skeletonized.astype("uint8")
    for x in range(columns):
        for y in range(rows):
            if skeletonized[x ,y] != 0:
                skeletonized[x ,y] = 255

    return skeletonized

    
def fill_part_of_vessel(node, angle, choosenColor, imageForDrawing):
    currentPoint = [node[0], node[1]]
    currentAngle = angle
    while True:
        
        minAngle = currentAngle - math.pi/2
        maxAngle = currentAngle + math.pi/2
        vesselPixels = find_white_vessels_in_neighborhood(currentPoint, minAngle, maxAngle, imageForDrawing)

        if len(vesselPixels) == 0:
            break

        if len(vesselPixels) == 1:
            imageForDrawing[currentPoint[1], currentPoint[0]] = choosenColor
            nextPoint = [vesselPixels[0][0], vesselPixels[0][1]]
            currentAngle = get_angle_between_two_points(currentPoint, nextPoint)
            currentPoint = nextPoint

        if len(vesselPixels) > 1:
            break


def attempt_2():
    imageNumber = 2
    golden_truth = Main.read_mask_image(DataPaths.original_manual_image_path(imageNumber, "DRIVE"), "DRIVE")
    skepetonizeInput = copy.deepcopy(golden_truth)
    skeletonized = apply_skeletonization(skepetonizeInput)
    imageForDrawing = cv2.merge((skeletonized,skeletonized,skeletonized))

    src = cv2.imread(DataPaths.original_image_path(imageNumber))
    radius = 60

    _, G_channel, R_channel = cv2.split(src)
    greenMerged = cv2.merge((G_channel,G_channel,G_channel))

    odMiddlePoint = OdLocalization.image_od_localization(G_channel)
    circle_coordinates = CircleCoordinationFinder.listOfCoordinates(radius, x_of_middle=odMiddlePoint[0], y_of_middle=odMiddlePoint[1])
    candidatePoints = CandidatePoints.find_middle_pixels_on_circle(golden_truth, circle_coordinates)
    # projit vsechny candidate pointy a v cervenem spektru najit jejich rexlex
    candidatePointCentralReflexes = []
    for candidatePoint in candidatePoints:
        candidatePointCentralReflexes.append(R_channel[candidatePoint[1], candidatePoint[0]])
    maxCentralReflex = max(candidatePointCentralReflexes)
    minCentralReflex = min(candidatePointCentralReflexes)
    differenceCentralReflex = maxCentralReflex - minCentralReflex
    middleCentralReflex = minCentralReflex + (differenceCentralReflex/2)


    for index in range(len(candidatePoints)):
        greenMerged = cv2.circle(greenMerged, (candidatePoints[index][0],candidatePoints[index][1]), radius=2, color=redPixel, thickness=-1)
    cv2.imshow("temp", greenMerged)
    cv2.waitKey(0)

    allFoundNodesWithAngles = []
    startingPointsOfSegments = []

    currentNodesWithAngles = []

    for candidatePoint in candidatePoints:
        vesselsInNeighborhood = find_vessels_in_neighborhood(skeletonized, candidatePoint, 3, 0, math.pi*2)
        if len(vesselsInNeighborhood) > 0:
            vesselPoint = [vesselsInNeighborhood[0][0], vesselsInNeighborhood[0][1]]
            #startingPoints.append(vesselPoint)
            imageForDrawing[vesselPoint[1], vesselPoint[0]] = greenPixel
            triangleAngle = CandidatePoints.angle_between_middle_and_candidate(odMiddlePoint,vesselPoint)
            seekingAngle = CandidatePoints.quadrant_angle(odMiddlePoint, vesselPoint, triangleAngle)
            currentNodesWithAngles.append([vesselPoint, seekingAngle])
            startingPointsOfSegments.append([vesselPoint, seekingAngle])
            print(f"Point with angle found: {vesselPoint} => {seekingAngle}")

    print("Attempt 2")

    while len(currentNodesWithAngles) > 0:
        newNodesWithAngles = []

        for currentNode, nodeAngle in currentNodesWithAngles:
            currentPoint = [currentNode[0], currentNode[1]]
            currentAngle = nodeAngle
            allFoundNodesWithAngles.append([currentNode, nodeAngle])
            numberOfPointsFound = 0
            while True:
                minAngle = currentAngle - ((math.pi/4)*3)
                maxAngle = currentAngle + ((math.pi/4)*3)
                vesselPixels = find_white_vessels_in_neighborhood(currentPoint, minAngle, maxAngle, imageForDrawing)

                if currentPoint[0] == 351 and currentPoint[1] == 202:
                    print("HERE")

                if currentPoint[0] == 351 and currentPoint[1] == 204:
                    print("HERE")

                if currentPoint[0] == 286 and currentPoint[1] == 480:
                    print("HERE")
                
                if currentPoint[0] == 287 and currentPoint[1] == 481:
                    print("HERE")
                if currentPoint[0] == 327 and currentPoint[1] == 493:
                    print("HERE")

                if len(vesselPixels) == 0:
                    imageForDrawing[currentPoint[1], currentPoint[0]] = greenPixel
                    if numberOfPointsFound > 2:
                            startingPointsOfSegments.append([currentNode, nodeAngle ])
                    break

                if len(vesselPixels) == 1:
                    imageForDrawing[currentPoint[1], currentPoint[0]] = greenPixel
                    nextPoint = [vesselPixels[0][0], vesselPixels[0][1]]
                    currentAngle = get_angle_between_two_points(currentPoint, nextPoint)
                    currentPoint = nextPoint
                    numberOfPointsFound = numberOfPointsFound + 1

                if len(vesselPixels) > 1:
                    for vesselPixel in vesselPixels:
                        imageForDrawing[vesselPixel[1], vesselPixel[0]] = greenPixel
                        newNodesWithAngles.append([vesselPixel, get_angle_between_two_points(currentPoint, vesselPixel)])
                        
                            

                    if numberOfPointsFound > 2:
                            startingPointsOfSegments.append([currentNode, nodeAngle])
                            
                        
                    break
                        
    

        currentNodesWithAngles = newNodesWithAngles

    save_and_show_progress(imageForDrawing)
    
    print(f"Listing all {len(allFoundNodesWithAngles)} nodes")
    print(f"Listing all {len(startingPointsOfSegments)} starts of segments")
    for node, angle in startingPointsOfSegments:
    #    print(f"Node with coordinates {node} and angle {angle}")
        imageForDrawing = cv2.circle(imageForDrawing, (node[0],node[1]), radius=3, color=bluePixel, thickness=-1)
            
    save_and_show_progress(imageForDrawing)
    cv2.imwrite(DataPaths.results_image_path("segments"), imageForDrawing)

    imageForDrawing = cv2.merge((skeletonized,skeletonized,skeletonized))

    listOfColors = [(255,255,0), (0,255,0), (0,0,255), (255,0,255), (0,255,255), (127,255,0)]

    for node, angle in startingPointsOfSegments:
        choosenColor = random.choice(listOfColors)
        if node[0] == 287 and node[1] == 481:
            print("HERE")
        fill_part_of_vessel(node, angle, choosenColor, imageForDrawing)
        

    save_and_show_progress(imageForDrawing)
    cv2.imwrite(DataPaths.results_image_path("segments_color"), imageForDrawing)

    imageForDrawing = cv2.merge((golden_truth,golden_truth,golden_truth))
    biggestDistance = 0
    smallestDistance = 500
    for node, angle in startingPointsOfSegments:
        distance = math.dist(node, odMiddlePoint)
        if distance > biggestDistance:
            biggestDistance = distance
        if distance < smallestDistance:
            smallestDistance = distance

    distancesDifference = biggestDistance - smallestDistance
    firstThird = int(smallestDistance + (distancesDifference/3))
    secondThird = int(firstThird + (distancesDifference/3))

    firstBatch = []
    secondBatch = []
    thirdBatch = []
    imageForDrawing = cv2.circle(imageForDrawing, (odMiddlePoint[0],odMiddlePoint[1]), radius=radius, color=(255,255,0), thickness=2)
    for node, angle in startingPointsOfSegments:
        distance = math.dist(node, odMiddlePoint)
        if distance >= radius and distance < firstThird:
            firstBatch.append([node, angle])
        if distance >= firstThird and distance < secondThird:
            secondBatch.append([node, angle])
        if distance >= secondThird and distance <= biggestDistance:
            thirdBatch.append([node, angle])
    
    for node, angle in firstBatch:
        imageForDrawing = cv2.circle(imageForDrawing, (node[0],node[1]), radius=3, color=bluePixel, thickness=-1)
    for node, angle in secondBatch:
        imageForDrawing = cv2.circle(imageForDrawing, (node[0],node[1]), radius=3, color=redPixel, thickness=-1)
    for node, angle in thirdBatch:
        imageForDrawing = cv2.circle(imageForDrawing, (node[0],node[1]), radius=3, color=greenPixel, thickness=-1)

    cv2.imshow("distances", imageForDrawing)
    cv2.imwrite(DataPaths.results_image_path("distances"), imageForDrawing)
    cv2.waitKey(0)
    imageForDrawing = cv2.merge((skeletonized,skeletonized,skeletonized))
    acumulatedOdrs = []
    for node, angle in firstBatch:
        
        vesselValueRed = 0
        vesselValueGreen = 0
        noOfVessels = 0
        backgroundlValueRed = 0
        backgroundlValueGreen = 0
        noOfBackground = 0
        for x in range(node[0]-10,node[0]+10):
            for y in range(node[1]-5,node[1]+5):
                if golden_truth[y,x] == 255:
                    noOfVessels += 1
                    vesselValueGreen += G_channel[y,x]
                    vesselValueRed += R_channel[y,x]
                else:
                    noOfBackground += 1
                    backgroundlValueGreen += G_channel[y,x]
                    backgroundlValueRed += R_channel[y,x]
        vesselValueRed = vesselValueRed/noOfVessels
        vesselValueGreen = vesselValueGreen/noOfVessels
        backgroundlValueRed = backgroundlValueRed/noOfBackground
        backgroundlValueGreen = backgroundlValueGreen/noOfBackground
        OdGreen = math.log(vesselValueGreen/backgroundlValueGreen)
        OdRed = math.log(vesselValueRed/backgroundlValueRed)
        Odr = (OdRed-OdGreen)/OdGreen
        acumulatedOdrs.append(Odr)
    
    maxOdr = max(acumulatedOdrs)
    minOdr = min(acumulatedOdrs)
    middleOdr = sum(acumulatedOdrs) / len(acumulatedOdrs)
    
    print(f"Max ord is {maxOdr} min is {minOdr} and middle is {middleOdr}")
    for index in range(len(firstBatch)):
        nodeCoordinates, angle = firstBatch[index]
        currentOdr = acumulatedOdrs[index]
        if currentOdr <= middleOdr:
            fill_part_of_vessel(nodeCoordinates, angle, bluePixel, imageForDrawing)
        else:
            fill_part_of_vessel(nodeCoordinates, angle, redPixel, imageForDrawing)
            
    cv2.imshow("first batch", imageForDrawing)
    cv2.imwrite(DataPaths.results_image_path("first_batch"), imageForDrawing)
    cv2.waitKey(0)

    acumulatedOdrs = []
    for node, angle in secondBatch:
        
        vesselValueRed = 0
        vesselValueGreen = 0
        noOfVessels = 0
        backgroundlValueRed = 0
        backgroundlValueGreen = 0
        noOfBackground = 0
        for x in range(node[0]-10,node[0]+10):
            for y in range(node[1]-5,node[1]+5):
                if golden_truth[y,x] == 255:
                    noOfVessels += 1
                    vesselValueGreen += G_channel[y,x]
                    vesselValueRed += R_channel[y,x]
                else:
                    noOfBackground += 1
                    backgroundlValueGreen += G_channel[y,x]
                    backgroundlValueRed += R_channel[y,x]
        vesselValueRed = vesselValueRed/noOfVessels
        vesselValueGreen = vesselValueGreen/noOfVessels
        backgroundlValueRed = backgroundlValueRed/noOfBackground
        backgroundlValueGreen = backgroundlValueGreen/noOfBackground
        OdGreen = math.log(vesselValueGreen/backgroundlValueGreen)
        OdRed = math.log(vesselValueRed/backgroundlValueRed)
        Odr = (OdRed-OdGreen)/OdGreen
        acumulatedOdrs.append(Odr)
    
    maxOdr = max(acumulatedOdrs)
    minOdr = min(acumulatedOdrs)
    middleOdr = sum(acumulatedOdrs) / len(acumulatedOdrs)
    
    print(f"Max ord is {maxOdr} min is {minOdr} and middle is {middleOdr}")
    for index in range(len(secondBatch)):
        nodeCoordinates, angle = secondBatch[index]
        currentOdr = acumulatedOdrs[index]
        if currentOdr <= middleOdr:
            fill_part_of_vessel(nodeCoordinates, angle, bluePixel, imageForDrawing)
        else:
            fill_part_of_vessel(nodeCoordinates, angle, redPixel, imageForDrawing)

    cv2.imshow("second batch", imageForDrawing)
    cv2.imwrite(DataPaths.results_image_path("second_batch"), imageForDrawing)
    cv2.waitKey(0)

    acumulatedOdrs = []
    for node, angle in thirdBatch:
        
        vesselValueRed = 0
        vesselValueGreen = 0
        noOfVessels = 0
        backgroundlValueRed = 0
        backgroundlValueGreen = 0
        noOfBackground = 0
        for x in range(node[0]-10,node[0]+10):
            for y in range(node[1]-5,node[1]+5):
                if golden_truth[y,x] == 255:
                    noOfVessels += 1
                    vesselValueGreen += G_channel[y,x]
                    vesselValueRed += R_channel[y,x]
                else:
                    noOfBackground += 1
                    backgroundlValueGreen += G_channel[y,x]
                    backgroundlValueRed += R_channel[y,x]
        vesselValueRed = vesselValueRed/noOfVessels
        vesselValueGreen = vesselValueGreen/noOfVessels
        backgroundlValueRed = backgroundlValueRed/noOfBackground
        backgroundlValueGreen = backgroundlValueGreen/noOfBackground
        OdGreen = math.log(vesselValueGreen/backgroundlValueGreen)
        OdRed = math.log(vesselValueRed/backgroundlValueRed)
        Odr = (OdRed-OdGreen)/OdGreen
        acumulatedOdrs.append(Odr)
    
    maxOdr = max(acumulatedOdrs)
    minOdr = min(acumulatedOdrs)
    middleOdr = sum(acumulatedOdrs) / len(acumulatedOdrs)
    
    print(f"Max ord is {maxOdr} min is {minOdr} and middle is {middleOdr}")
    for index in range(len(thirdBatch)):
        nodeCoordinates, angle = thirdBatch[index]
        currentOdr = acumulatedOdrs[index]
        if currentOdr <= middleOdr:
            fill_part_of_vessel(nodeCoordinates, angle, bluePixel, imageForDrawing)
        else:
            fill_part_of_vessel(nodeCoordinates, angle, redPixel, imageForDrawing)

    cv2.imshow("third batch", imageForDrawing)
    cv2.imwrite(DataPaths.results_image_path("third_batch"), imageForDrawing)
    cv2.waitKey(0)

    finalImage1 = cv2.merge((golden_truth, golden_truth, golden_truth))

    height = len(golden_truth)
    width = len(golden_truth[0])

    for x in range(width):
        for y in range(height):
            actualColor = imageForDrawing[y, x]
            if are_colors_same(actualColor, redPixel):
                finalImage1[y, x] = redPixel
            if are_colors_same(actualColor, bluePixel):
                finalImage1[y, x] = bluePixel
                
    cv2.imshow("final result", finalImage1)
    cv2.waitKey(0)
    
    iterationNumber = 0
    while True:
        finalImage2 = copy.deepcopy(finalImage1)
        iterationNumber += 1
        changedPixels = 0
        print(f"iretation number: {iterationNumber}")
        for x in range(width):
            for y in range(height):
                if are_colors_same(finalImage1[y, x], whitePixel):
                    foundColor = find_colors_in_neighborhood(finalImage1, [x,y])
                    if not are_colors_same(foundColor, whitePixel):
                        finalImage2[y,x] = foundColor
                        changedPixels += 1
        finalImage1 = finalImage2

        if changedPixels == 0:
            break
    cv2.imshow("final result", finalImage1)
    cv2.waitKey(0)
    cv2.imwrite(DataPaths.results_image_path("FINAL_RESULT"), finalImage1)

    print("END")

    






greenPixel = (0,255,0)
bluePixel = (255,0,0)
redPixel = (0,0,255)
whitePixel = (255,255,255)
blackPixel = (0,0,0)





if __name__ == "__main__":
   attempt_2()
