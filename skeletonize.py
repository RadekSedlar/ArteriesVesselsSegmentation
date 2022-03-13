# Standard imports
import copy
import cv2
import numpy as np;
import Main
from operator import attrgetter
from operator import itemgetter
import random
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
import DataPaths

class VesselMiddleInfo:
    def __init__(self, point, diameter, vesselOrientation):
        self.point = point
        self.diameter = diameter
        self.vesselOrientation = vesselOrientation



def is_point_in_matrix(columns, rows, point):
    """ Determines if point is in boundaris of image

    @type columns: int
    @param columns: number of columns in image
    @type rows: int
    @param rows: number of rows in image
    @rtype: bool
    @returns: TRUE if in boundaries, otherwise FALSE"""
    if point[1] >= 0 and point[1] < rows and point[0] >= 0 and point[0] < columns:
        return True
    else:
        return False

def remove_small_dots(skeletonized):
    """ Removes small segments from skeletonized image

    @type skeletonized: uint[,]
    @param skeletonized: Image with only 0 or 255, representing middle of segmented blood vessels
    @rtype: uint[,]
    @returns: Skeletonized image without small particles"""
    #find all your connected components (white blobs in your image)
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(skeletonized, connectivity=8)
    #connectedComponentswithStats yields every seperated component with information on each of them, such as size
    #the following part is just taking out the background which is also considered a component, but most of the time we don't want that.
    sizes = stats[1:, -1]; nb_components = nb_components - 1

    # minimum size of particles we want to keep (number of pixels)
    #here, it's a fixed value, but you can set it as you want, eg the mean of the sizes or whatever
    min_size = 5  

    #your answer image
    img2 = np.zeros((output.shape))
    #for every component in the image, you keep it only if it's above min_size
    for i in range(0, nb_components):
        if sizes[i] >= min_size:
            img2[output == i + 1] = 255
    return img2


def get_middle_pixel_vertical(golden_truth, x, y):
    """ Assign middle pixel only in vertical axis

    @type golden_truth: uint[,]
    @param golden_truth: Image with only 0 or 255, representing segmented blood vessels
    @type x: int
    @param x: X coordinate of given point
    @type y: int
    @param y: Y coordinate of given point
    @rtype: VesselMiddleInfo
    @returns: Info about vertical middle pixel"""
    (columns, rows) = golden_truth.shape
    maximum_y = y
    width = 1
    maximum_y += 1
    while maximum_y >= 0 and maximum_y < rows:
        
        if golden_truth[x,maximum_y] == 0:
            #print(f"For y '{maximum_y}' break")
            break
        maximum_y += 1
    maximum_y -= 1
    
    #print(maximum_y)

    minimum_y = maximum_y
    minimum_y -= 1
    while minimum_y >= 0 and minimum_y < rows:
        if golden_truth[x, minimum_y] == 0:
            break
        width += 1
        minimum_y -= 1
    minimum_y += 1
    #print(minimum_y)
    y_of_middle = minimum_y + width//2
    return VesselMiddleInfo((x, y_of_middle), width, Main.VesselOrientation.VERTICAL)


def get_middle_pixel_horizontal(golden_truth, x, y):
    """ Assign middle pixel only in horizontal axis

    @type golden_truth: uint[,]
    @param golden_truth: Image with only 0 or 255, representing segmented blood vessels
    @type x: int
    @param x: X coordinate of given point
    @type y: int
    @param y: Y coordinate of given point
    @rtype: VesselMiddleInfo
    @returns: Info about horizontal middle pixel"""
    (columns, rows) = golden_truth.shape
    maximum_x = x
    height = 1
    maximum_x += 1
    while maximum_x >= 0 and maximum_x < columns:
        
        if golden_truth[maximum_x, y] == 0:
            #print(f"For y '{maximum_y}' break")
            break
        maximum_x += 1
    maximum_x -= 1
    
    #print(maximum_y)

    minimum_x = maximum_x
    minimum_x -= 1
    while minimum_x >= 0 and minimum_x < rows:
        if golden_truth[minimum_x, y] == 0:
            break
        height += 1
        minimum_x -= 1
    minimum_x += 1
    #print(minimum_y)
    x_of_middle = minimum_x + height//2
    return VesselMiddleInfo((x_of_middle, y), height, Main.VesselOrientation.HORIZONTAL)
    

def get_middle_pixel(golden_truth, x, y):
    """ Assign middle pixel and get ist info

    @type golden_truth: uint[,]
    @param golden_truth: Image with only 0 or 255, representing segmented blood vessels
    @type x: int
    @param x: X coordinate of given point
    @type y: int
    @param y: Y coordinate of given point
    @rtype: VesselMiddleInfo
    @returns: Info about middle pixel"""
    results = []
    results.append(get_middle_pixel_vertical(golden_truth, x, y))
    results.append(get_middle_pixel_horizontal(golden_truth, x, y))
    return min(results, key=attrgetter('diameter'))



def get_central_reflex(green_clahe, x, y):
    """ Returns value of pixel according to coordinates given

    @type green_clahe: uint[,]
    @param green_clahe: Green spectrum of original picture, with CLAHE equalization
    @type x: int
    @param x: X coordinate of given point
    @type y: int
    @param y: Y coordinate of given point
    @rtype: uint8
    @returns: value of pixel"""
    return green_clahe[x,y]


def skeletonize_My_Approach(original):
    only_middle = original.copy()
    (columns, rows) = only_middle.shape
    for x in range(columns):
        for y in range(rows):
            only_middle[x ,y] = 0
    for x in range(columns):
        for y in range(rows):
            if original[x,y] == 255:
                vesselMiddleInfo = get_middle_pixel(original, x , y)
                only_middle[vesselMiddleInfo.point[0] ,vesselMiddleInfo.point[1]] = 255
    return only_middle


if __name__ == "__main__":
    imageNumber = 1
    src = cv2.imread(DataPaths.original_image_path(numberOfImage=imageNumber))
    golden_truth = Main.read_gif_image(DataPaths.original_manual_image_path(numberOfImage=imageNumber))
    print(src.shape)
    only_middle = skeletonize_My_Approach(golden_truth)
    (columns, rows) = only_middle.shape
    
    skeleton = cv2.merge((only_middle,only_middle,only_middle))
    result_all = np.concatenate((cv2.merge((golden_truth,golden_truth,golden_truth)), src, skeleton), axis=0)
    cv2.imshow("result_all", result_all)
    withouSmallDots = remove_small_dots(only_middle)
    cv2.imwrite(DataPaths.skeletonize_results_image_path("skeleton_result"), result_all)
    cv2.imwrite(DataPaths.skeletonize_results_image_path("skeleton"), skeleton)
    cv2.imwrite(DataPaths.skeletonize_results_image_path("withoutSmallDots"), withouSmallDots)
    skepetonizeInput = copy.deepcopy(golden_truth)
    for x in range(columns):
        for y in range(rows):
            if skepetonizeInput[x ,y] != 0:
                skepetonizeInput[x ,y] = 1
    plt.imsave(DataPaths.skeletonize_results_image_path("skeleton_skimage"), skeletonize(skepetonizeInput), cmap = plt.cm.gray)

    

    mask = Main.read_gif_image(DataPaths.original_image_mask_path(numberOfImage=imageNumber))
    B_channel, G_channel, R_channel = cv2.split(src)
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(10, 10))

    G_channel_clahe = clahe.apply(G_channel)

    points = []
    while len(points) < 90:
        rand_x = random.randint(0, columns - 1)
        rand_y = random.randint(0, rows - 1)
        if golden_truth[rand_x, rand_y] == 0:
            continue # didnt hit vessel
        vesselMiddleInfo = get_middle_pixel(golden_truth, rand_x , rand_y)
        points.append((vesselMiddleInfo.point[0], vesselMiddleInfo.point[1], vesselMiddleInfo.diameter, get_central_reflex(G_channel_clahe, vesselMiddleInfo.point[0], vesselMiddleInfo.point[1])))
        
    sorted_points_by_diameter = sorted(points, key = itemgetter(2))
    sorted_points_by_diameter = sorted_points_by_diameter[30:60]
    sorted_points_by_diameter = sorted(sorted_points_by_diameter, key = itemgetter(3))
    print(len(sorted_points_by_diameter))
    
    for point_info in sorted_points_by_diameter:
        print(f"[{point_info[0]}, {point_info[1]}] - {point_info[2]} pixels\treflex - {point_info[3]}")
        
    for item in sorted_points_by_diameter[:15]:
        src = cv2.circle(src, (item[1], item[0]), radius = 5, color = (0,0,255), thickness=-1)
    for item in sorted_points_by_diameter[15:]:
        src = cv2.circle(src, (item[1], item[0]), radius = 5, color = (255,0,0), thickness=-1)
        
    
    cv2.imshow("points", src)
    cv2.waitKey(0)