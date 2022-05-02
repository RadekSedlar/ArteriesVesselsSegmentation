import math
import numpy as np
import Main
import copy
import cv2
import DataPaths
from skimage.morphology import skeletonize
import OdLocalization
import CircleCoordinationFinder
import CandidatePoints
import VesselOrientation
import statistics


import matplotlib.pyplot as plt

from sklearn.cluster import KMeans

def get_odr_for_point(point, angle, G_channel, R_channel, golden_truth):
    vesselValueRed =  R_channel[point[1],point[0]]
    vesselValueGreen = G_channel[point[1],point[0]]
    backgroundlValueRed = get_background_reflex(point, angle, R_channel, golden_truth)
    backgroundlValueGreen = get_background_reflex(point, angle, G_channel, golden_truth)
    OdGreen = math.log(vesselValueGreen/backgroundlValueGreen)
    OdRed = math.log(vesselValueRed/backgroundlValueRed)
    if OdGreen == 0.0:
       return OdRed
    Odr = (OdRed-OdGreen)/OdGreen

    return Odr

def get_my_odr_for_point(point, G_channel, R_channel):
    vesselValueRed =  R_channel[point[1],point[0]]
    vesselValueGreen = G_channel[point[1],point[0]]
    Odr = vesselValueRed - vesselValueGreen

    return Odr


def get_vessel_diameter(originPoint, angle, groundTruth):
    leftAngle = angle + math.pi/2
    leftVesselEdgePoint = [originPoint[0], originPoint[1]]
    leftDistance = 0
    while groundTruth[leftVesselEdgePoint[1], leftVesselEdgePoint[0]] == 255:
        nextLeftPoint = VesselOrientation.get_point_from_angle_and_distance(leftVesselEdgePoint, leftAngle, 1)
        leftDistance += 1
        if nextLeftPoint[0] == leftVesselEdgePoint[0] and nextLeftPoint[1] == leftVesselEdgePoint[1]: # in case that distance 1 generates same point repeat with distance 2
            nextLeftPoint = VesselOrientation.get_point_from_angle_and_distance(leftVesselEdgePoint, leftAngle, 2)

        if groundTruth[nextLeftPoint[1], nextLeftPoint[0]] == 0:
            break
        leftVesselEdgePoint = nextLeftPoint

    rightAngle = angle - math.pi/2
    rightVesselEdgePoint = [originPoint[0], originPoint[1]]
    rightDistance = 0
    while groundTruth[rightVesselEdgePoint[1], rightVesselEdgePoint[0]] == 255:
        nextRightPoint = VesselOrientation.get_point_from_angle_and_distance(rightVesselEdgePoint, rightAngle, 1)
        rightDistance += 1
        if nextRightPoint[0] == rightVesselEdgePoint[0] and nextRightPoint[1] == rightVesselEdgePoint[1]: # in case that distance 1 generates same point repeat with distance 2
            nextRightPoint = VesselOrientation.get_point_from_angle_and_distance(rightVesselEdgePoint, rightAngle, 2)

        if groundTruth[nextRightPoint[1], nextRightPoint[0]] == 0:
            break
        rightVesselEdgePoint = nextRightPoint

    return leftDistance + rightDistance

def get_background_reflex(originPoint, angle, grayscaleImage, groundTruth):
    leftAngle = angle + math.pi/2
    leftVesselEdgePoint = [originPoint[0], originPoint[1]]
    leftDistance = 0
    while groundTruth[leftVesselEdgePoint[1], leftVesselEdgePoint[0]] == 255:
        nextLeftPoint = VesselOrientation.get_point_from_angle_and_distance(leftVesselEdgePoint, leftAngle, 1)
        leftDistance += 1
        if nextLeftPoint[0] == leftVesselEdgePoint[0] and nextLeftPoint[1] == leftVesselEdgePoint[1]: # in case that distance 1 generates same point repeat with distance 2
            nextLeftPoint = VesselOrientation.get_point_from_angle_and_distance(leftVesselEdgePoint, leftAngle, 2)

        if groundTruth[nextLeftPoint[1], nextLeftPoint[0]] == 0:
            break
        leftVesselEdgePoint = nextLeftPoint

    rightAngle = angle - math.pi/2
    rightVesselEdgePoint = [originPoint[0], originPoint[1]]
    rightDistance = 0
    while groundTruth[rightVesselEdgePoint[1], rightVesselEdgePoint[0]] == 255:
        nextRightPoint = VesselOrientation.get_point_from_angle_and_distance(rightVesselEdgePoint, rightAngle, 1)
        rightDistance += 1
        if nextRightPoint[0] == rightVesselEdgePoint[0] and nextRightPoint[1] == rightVesselEdgePoint[1]: # in case that distance 1 generates same point repeat with distance 2
            nextRightPoint = VesselOrientation.get_point_from_angle_and_distance(rightVesselEdgePoint, rightAngle, 2)

        if groundTruth[nextRightPoint[1], nextRightPoint[0]] == 0:
            break
        rightVesselEdgePoint = nextRightPoint

    leftBackgroundPoint = VesselOrientation.get_point_from_angle_and_distance(originPoint, leftAngle, leftDistance*2)
    additionalDistance = 1
    while groundTruth[leftBackgroundPoint[1], leftBackgroundPoint[0]] != 0:
        leftBackgroundPoint = VesselOrientation.get_point_from_angle_and_distance(originPoint, leftAngle, (leftDistance*2 + additionalDistance))
        additionalDistance += 1
    
    rightBackgroundPoint = VesselOrientation.get_point_from_angle_and_distance(originPoint, rightAngle, rightDistance*2)
    additionalDistance = 1
    while groundTruth[rightBackgroundPoint[1], rightBackgroundPoint[0]] != 0:
        rightBackgroundPoint = VesselOrientation.get_point_from_angle_and_distance(originPoint, rightAngle, (rightDistance*2 + additionalDistance))
        additionalDistance += 1

    leftBackgroundReflex = grayscaleImage[leftBackgroundPoint[1], leftBackgroundPoint[0]]
    rightBackgroundReflex = grayscaleImage[rightBackgroundPoint[1], rightBackgroundPoint[0]]
    #print(f"1 = {leftBackgroundReflex}, 2 = {rightBackgroundReflex}")
    returningValue = np.mean([leftBackgroundReflex, rightBackgroundReflex])
    #print(f"returning = {returningValue}")
    return returningValue

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
        if are_colors_same(image[neighborhood[coordinateIndex][1], neighborhood[coordinateIndex][0]], greenPixel):
            return greenPixel

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

def find_vessel_root_in_segmented_skeletonized_image(node, angle, skeletonized, segmentedSkeletonized):
    currentPoint = [node[0], node[1]]
    currentAngle = angle
    colorForMarkingPixels = greenPixel
    while True:
        
        minAngle = currentAngle - math.pi/2
        maxAngle = currentAngle + math.pi/2
        vesselPixels = find_white_vessels_in_neighborhood(currentPoint, minAngle, maxAngle, skeletonized)

        if len(vesselPixels) == 0:
            return []

        if len(vesselPixels) == 1:
            skeletonized[currentPoint[1], currentPoint[0]] = colorForMarkingPixels
            nextPoint = [vesselPixels[0][0], vesselPixels[0][1]]
            currentAngle = get_angle_between_two_points(currentPoint, nextPoint)
            currentPoint = nextPoint
            if are_colors_same(segmentedSkeletonized[currentPoint[1], currentPoint[0]], whitePixel):
                return [currentPoint, currentAngle]
                

        if len(vesselPixels) > 1:
            return []


def calculate_average_value_around_point_in_channel(point, channel):
    acumulatedValue = channel[point[1], point[0]]
    neighborhoodPoints = get_neighborhood_coordinates(point, 3, 0, math.pi*2)
    for neighborhoodPoint in neighborhoodPoints:
        acumulatedValue += channel[neighborhoodPoint[1], neighborhoodPoint[0]]
    return (acumulatedValue / 9)

def calculate_average_value_around_points_in_channel(pointsWithAngles, channel):
    acumulatedValue = 0
    for point, _ in pointsWithAngles:
        acumulatedValue += channel[point[1], point[0]]
        neighborhoodPoints = get_neighborhood_coordinates(point, 3, 0, math.pi*2)
        for neighborhoodPoint in neighborhoodPoints:
            acumulatedValue += channel[neighborhoodPoint[1], neighborhoodPoint[0]]

    return acumulatedValue/(len(pointsWithAngles) * 9)

def mean_deviations_of_points(pointsWithAngles, channel):
    #mean = calculate_average_value_around_points_in_channel(pointsWithAngles, channel)

    #meanDerivations = []
    #for point, _ in pointsWithAngles:
    #    meanDerivations.append(abs(calculate_average_value_around_point_in_channel(point, channel) - mean))

    accumulatedValues = [];
    for point, _ in pointsWithAngles:
        neighborhoodPointValues = [float(channel[point[1], point[0]])]
        neighborhoodPoints = get_neighborhood_coordinates(point, 3, 0, math.pi*2)
        for neighborhoodPoint in neighborhoodPoints:
            neighborhoodPointValues.append(float(channel[neighborhoodPoint[1], neighborhoodPoint[0]]))
        accumulatedValues.append(np.mean(np.absolute(neighborhoodPointValues - np.mean(neighborhoodPointValues))))
    return accumulatedValues

    
def std_deviations_of_point(point, channel):
    acumulatedValues = [float(channel[point[1], point[0]])]
    neighborhoodPoints = get_neighborhood_coordinates(point, 3, 0, math.pi*2)
    for neighborhoodPoint in neighborhoodPoints:
        acumulatedValues.append(float(channel[neighborhoodPoint[1], neighborhoodPoint[0]]))
    return statistics.stdev(acumulatedValues)

def std_deviations_of_points(pointsWithAngles, channel):
    stdDeviations = []
    for point, _ in pointsWithAngles:
        stdDeviations.append(std_deviations_of_point(point, channel))
    return stdDeviations
    

def floodfill_vessel(pointOnVessel, skeletonizedImage, color):
    skeletonizedImage[pointOnVessel[1], pointOnVessel[0]] = color
    vesselPixelsInNei = find_white_vessels_in_neighborhood(pointOnVessel, 0, math.pi*2, skeletonizedImage)

    pointsStack = []
    for vesselPixel in vesselPixelsInNei:
        skeletonizedImage[vesselPixel[1], vesselPixel[0]] = color
        pointsStack.append(vesselPixel)

    while len(pointsStack) > 0:
        vesselPixelsInNei = find_white_vessels_in_neighborhood(pointsStack[0], 0, math.pi*2, skeletonizedImage)
        for vesselPixel in vesselPixelsInNei:
            skeletonizedImage[vesselPixel[1], vesselPixel[0]] = color
            pointsStack.append(vesselPixel)
        pointsStack.remove(pointsStack[0])

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def apply_k_means(segmentedPartsRootPoints, G_channel, src, imageForDrawing, waitAndShow=False):
    chunkSize = int(len(segmentedPartsRootPoints)/3) + 1
    firstBatch, secondBatch, thirdBatch = chunks(segmentedPartsRootPoints,chunkSize)

    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    hue, _, _ = cv2.split(hsv)
    plot_k_means_results(firstBatch, create_k_means_data(firstBatch, G_channel, hue), imageForDrawing, waitAndShow=waitAndShow)
    plot_k_means_results(secondBatch, create_k_means_data(secondBatch, G_channel, hue), imageForDrawing, waitAndShow=waitAndShow)
    plot_k_means_results(thirdBatch, create_k_means_data(thirdBatch, G_channel, hue), imageForDrawing, waitAndShow=waitAndShow)

def apply_ODR(segmentedPartsRootPoints, G_channel, R_channel, golden_truth, imageForDrawing, waitAndShow=False):
    chunkSize = int(len(segmentedPartsRootPoints)/3) + 1
    firstBatch, secondBatch, thirdBatch = chunks(segmentedPartsRootPoints,chunkSize)

    #first batch
    allORDs = []
    for point, angle in firstBatch:
        allORDs.append(get_odr_for_point(point,angle, G_channel, R_channel, golden_truth))
    meanOdr = np.mean(allORDs)
    for index in range(len(firstBatch)):
        if allORDs[index] > meanOdr:
            fill_part_of_vessel(firstBatch[index][0],firstBatch[index][1], bluePixel, imageForDrawing)
        else:
            fill_part_of_vessel(firstBatch[index][0],firstBatch[index][1], redPixel, imageForDrawing)

    #second batch
    allORDs = []
    for point, angle in secondBatch:
        allORDs.append(get_odr_for_point(point,angle, G_channel, R_channel, golden_truth))
    meanOdr = np.mean(allORDs)
    for index in range(len(secondBatch)):
        if allORDs[index] > meanOdr:
            fill_part_of_vessel(secondBatch[index][0],secondBatch[index][1], bluePixel, imageForDrawing)
        else:
            fill_part_of_vessel(secondBatch[index][0],secondBatch[index][1], redPixel, imageForDrawing)
        

    #third batch
    allORDs = []
    for point, angle in thirdBatch:
        allORDs.append(get_odr_for_point(point,angle, G_channel, R_channel, golden_truth))
    meanOdr = np.mean(allORDs)
    for index in range(len(thirdBatch)):
        if allORDs[index] > meanOdr:
            fill_part_of_vessel(thirdBatch[index][0],thirdBatch[index][1], bluePixel, imageForDrawing)
        else:
            fill_part_of_vessel(thirdBatch[index][0],thirdBatch[index][1], redPixel, imageForDrawing)

    if waitAndShow:
        cv2.imshow("Batch", imageForDrawing)
    

def plot_k_means_results(pointsWithAngles, kmeansData, imageForDrawing, waitAndShow=False):
    kmeans = KMeans(
        init="random",
        n_clusters=2,
        n_init=10,
        max_iter=300,
        random_state=42)

    kmeans.fit(kmeansData)

    firstCluster = []
    secondCluster = []
    firstClusterMiddle = kmeans.cluster_centers_[0]
    secondClusterMiddle = kmeans.cluster_centers_[1]
    for data in kmeansData:
        distanceFromFirst = math.dist(firstClusterMiddle, data)
        distanceFromSecond= math.dist(secondClusterMiddle, data)
        if distanceFromFirst <= distanceFromSecond:
            firstCluster.append(data)
        else:
            secondCluster.append(data)
    
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    firstCluster = np.array(firstCluster)
    ax.scatter(firstCluster[:,0], firstCluster[:,1], firstCluster[:,2], c="red")

    secondCluster = np.array(secondCluster)
    ax.scatter(secondCluster[:,0], secondCluster[:,1], secondCluster[:,2], c="blue")

        

    kmeansData = np.array(kmeansData)
    ax.set_xlabel("MEADE zelené spektrum")
    ax.set_ylabel("MEADE odstín")
    ax.set_zlabel("STDE zelené spektrum")
    ax.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], kmeans.cluster_centers_[:, 2], s=300, c='black', marker="P")
    

    if waitAndShow:
        plt.show()

    
    for index in range(len(pointsWithAngles)):
        distanceFromFirst = math.dist(firstClusterMiddle, kmeansData[index])
        distanceFromSecond= math.dist(secondClusterMiddle, kmeansData[index])
        if distanceFromFirst <= distanceFromSecond:
            fill_part_of_vessel(pointsWithAngles[index][0], pointsWithAngles[index][1], bluePixel, imageForDrawing)
        else:
            fill_part_of_vessel(pointsWithAngles[index][0], pointsWithAngles[index][1], redPixel, imageForDrawing)

    if waitAndShow:       
        cv2.imshow("result", imageForDrawing)
        cv2.waitKey(0)
    plt.close()
    

def create_k_means_data(pointsWithAngles, G_channel, hue):
    greenMeanDerivations = mean_deviations_of_points(pointsWithAngles, G_channel)
    hueMeanDerivations = mean_deviations_of_points(pointsWithAngles, hue)
    greenStdDerivations = std_deviations_of_points(pointsWithAngles, G_channel)

    kmeansData = []
    for index in range(len(pointsWithAngles)):
        kmeansData.append([greenMeanDerivations[index], hueMeanDerivations[index], greenStdDerivations[index]])
    return kmeansData
    

def attempt_2(method, dataset, imageNumber, waitAndShow=False):
    
    golden_truth = Main.read_mask_image(DataPaths.original_manual_image_path(imageNumber, dataset), dataset)
    skepetonizeInput = copy.deepcopy(golden_truth)
    skeletonized = apply_skeletonization(skepetonizeInput)
    imageForDrawing = cv2.merge((skeletonized,skeletonized,skeletonized))

    src = cv2.imread(DataPaths.original_image_path(imageNumber, dataset))
    radius = 60

    _, G_channel, R_channel = cv2.split(src)
    cv2.imwrite(DataPaths.results_image_path("G_channel"), G_channel)
    cv2.imwrite(DataPaths.results_image_path("R_channel"), R_channel)

    odMiddlePoint = OdLocalization.image_od_localization(G_channel)
    circle_coordinates = CircleCoordinationFinder.listOfCoordinates(radius, x_of_middle=odMiddlePoint[0], y_of_middle=odMiddlePoint[1])
    candidatePoints = CandidatePoints.find_middle_pixels_on_circle(golden_truth, circle_coordinates)
    
    #candidatePoints.sort(key=lambda x: get_odr_for_point(x[0], x[1], G_channel, R_channel, golden_truth))
    

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
            #print(f"Point with angle found: {vesselPoint} => {seekingAngle}")



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
    if waitAndShow:
        save_and_show_progress(imageForDrawing)
    
    for node, angle in startingPointsOfSegments:
    #    print(f"Node with coordinates {node} and angle {angle}")
        imageForDrawing = cv2.circle(imageForDrawing, (node[0],node[1]), radius=3, color=bluePixel, thickness=-1)
    if waitAndShow:
        save_and_show_progress(imageForDrawing)

    skeletonizedWithoudBifructations = cv2.merge((skeletonized, skeletonized, skeletonized))
    skeletonized = cv2.merge((skeletonized, skeletonized, skeletonized))
    for node, angle in startingPointsOfSegments:
        skeletonizedWithoudBifructations = cv2.circle(skeletonizedWithoudBifructations, (node[0],node[1]), radius=5, color=(0,0,0), thickness=-1)
    cv2.imshow("temp", skeletonizedWithoudBifructations)
    _, grayscaledSkeletonization, _ = cv2.split(skeletonizedWithoudBifructations)
    if waitAndShow:
        cv2.imshow("temp skeletonized", grayscaledSkeletonization)
        cv2.waitKey(0)
    cv2.imwrite(DataPaths.results_image_path("new_skeletonized"),grayscaledSkeletonization)

    segmentedPartsRootPoints = []
    imageForDrawing = copy.deepcopy(skeletonizedWithoudBifructations)
    for node, angle in allFoundNodesWithAngles:
        returnedRootPointWithAngle = find_vessel_root_in_segmented_skeletonized_image(node, angle, skeletonized, skeletonizedWithoudBifructations)
        if len(returnedRootPointWithAngle) > 0:
            segmentedPartsRootPoints.append(returnedRootPointWithAngle)

    for node, angle in segmentedPartsRootPoints:
        fill_part_of_vessel(node, angle, redPixel, imageForDrawing)
        imageForDrawing = cv2.circle(imageForDrawing, (node[0],node[1]), radius=2, color=greenPixel, thickness=-1)
    
    print(f"{imageNumber} & {len(allFoundNodesWithAngles)} & {len(startingPointsOfSegments)} & {len(segmentedPartsRootPoints)}  \\\\")
    if waitAndShow:
        cv2.imshow("temp skeletonized", imageForDrawing)
        cv2.waitKey(0)
    cv2.imwrite(DataPaths.results_image_path("new_root_points"),imageForDrawing)
    


    

    segmentedPartsRootPoints.sort(key=lambda x: get_vessel_diameter(x[0], x[1], golden_truth))
    
    
    
    imageForDrawing = copy.deepcopy(skeletonized)

    for segmentedPartsRootPoint in segmentedPartsRootPoints:
        if math.dist(segmentedPartsRootPoint[0], odMiddlePoint) < 20:
            segmentedPartsRootPoints.remove(segmentedPartsRootPoint)
        

    # HEEEEEEEEEEEEEEEEEEEEEERE
    if method == "ODR":
        apply_ODR(segmentedPartsRootPoints, G_channel, R_channel, golden_truth, imageForDrawing, waitAndShow)
    elif method == "KMEANS":
        apply_k_means(segmentedPartsRootPoints, G_channel, src, imageForDrawing, waitAndShow=waitAndShow)
    else:
        print(f"Method {method} is not supported")
        return

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
    if waitAndShow:     
        cv2.imshow("final result", finalImage1)
        cv2.waitKey(0)
    
    iterationNumber = 0
    while True:
        finalImage2 = copy.deepcopy(finalImage1)
        iterationNumber += 1
        if waitAndShow:
            print(f"iteration number: {iterationNumber}")
        changedPixels = 0
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

    veins = 0
    arteries = 0
    notMapped = 0
    for x in range(width):
        for y in range(height):
            if are_colors_same(finalImage1[y, x], whitePixel):
                notMapped += 1
            if are_colors_same(finalImage1[y, x], bluePixel):
                arteries += 1
            if are_colors_same(finalImage1[y, x], redPixel):
                veins += 1

    allPixels = veins + arteries + notMapped
    veinsPercent = "{:.2f}".format((veins/allPixels) * 100)
    arteriesPercent = "{:.2f}".format((arteries/allPixels) * 100)
    notMappedPercent = "{:.2f}".format((notMapped/allPixels) * 100)
    print(f"{imageNumber} & {veinsPercent}\\% & {arteriesPercent}\\%  & {notMappedPercent}\\%  \\\\")
    if waitAndShow:
        cv2.imshow("final result", finalImage1)
        cv2.waitKey(0)
    cv2.imwrite(DataPaths.results_image_path("FINAL_RESULT_2"), finalImage1)

    print("END")

greenPixel = (0,255,0)
bluePixel = (255,0,0)
redPixel = (0,0,255)
whitePixel = (255,255,255)
blackPixel = (0,0,0)





if __name__ == "__main__":
    for imageNumber in range(1,2):
        attempt_2("KMEANS", "DRIVE", imageNumber, False)
