import math
import cv2
import numpy as np
import copy

def remove_duplicate_coordinates(originalList):
    new_list = []
    for elem in originalList:
        if elem not in new_list:
            new_list.append(elem)
    return new_list


def listOfCoordinates(radius, x_of_middle=0, y_of_middle=0):
    """ Finds all points on circle

    @type radius: uint
    @param radius: radius of desired circle
    @type x_of_middle: int
    @param x_of_middle: x coordinate of middle point
    @type y_of_middle: int
    @param y_of_middle: y coordinate of middle point
   
    
    @rtype: [[uint8]]
    @returns: list of python image coordinates
    """
    y_coordinate = radius
    circle_coordinates = []
    # find all x for all y coordinates
    while y_coordinate >= - radius:
        x_coordinate = round(math.sqrt(radius*radius - y_coordinate*y_coordinate))
        circle_coordinates.append([x_coordinate, y_coordinate])
        if x_coordinate != 0:
            circle_coordinates.append([-x_coordinate, y_coordinate])
        y_coordinate -= 1

    # find all y for x coordinates
    circle_coordinates_mirror = copy.deepcopy(circle_coordinates)
    for point_index in range(len(circle_coordinates_mirror)):
        temp = circle_coordinates_mirror[point_index][0]
        circle_coordinates_mirror[point_index][0] = circle_coordinates_mirror[point_index][1]
        circle_coordinates_mirror[point_index][1] = temp
    # merge y and x coordinates lists
    circle_coordinates = circle_coordinates + circle_coordinates_mirror

    # sort coordinates into quadrants
    first_quadrant = []
    second_quadrant = []
    third_quadrant = []
    fourth_quadrant = []
    for point in circle_coordinates:
        if point[0] > 0 and point[1] >= 0:
            first_quadrant.append(point)
        if point[0] <= 0 and point[1] > 0:
            second_quadrant.append(point)
        if point[0] < 0 and point[1] <= 0:
            third_quadrant.append(point)
        if point[0] >= 0 and point[1] < 0:
            fourth_quadrant.append(point)
    # remove duplicate coordinates
    first_quadrant = remove_duplicate_coordinates(first_quadrant)
    second_quadrant = remove_duplicate_coordinates(second_quadrant)
    third_quadrant = remove_duplicate_coordinates(third_quadrant)
    fourth_quadrant = remove_duplicate_coordinates(fourth_quadrant)
    # sort quadrants
    first_quadrant.sort(key=lambda k: (k[1], -k[0]))
    second_quadrant.sort(key=lambda k: (-k[0], -k[1]))
    third_quadrant.sort(key=lambda k: (-k[1], k[0]))
    fourth_quadrant.sort(key=lambda k: (k[0], k[1]))
    # merge quardants
    circle_coordinates = first_quadrant + second_quadrant + third_quadrant + fourth_quadrant
    # move around original middle point
    for point in circle_coordinates:
        point[0] += x_of_middle
        point[1] += y_of_middle
    # switch coordinates
    for point in circle_coordinates:
        tempPoint = point[0]
        point[0] = point[1]
        point[1] = tempPoint
    return circle_coordinates



if __name__ == "__main__":
    blank_image = np.zeros((100,100,3), np.uint8)
    radius = 4
    circle_points = listOfCoordinates(radius, 50, 30)
    

    for point_index in range(len(circle_points)):
        blank_image[circle_points[point_index][0]][circle_points[point_index][1]] = (0,0,255)
    cv2.imshow("middle", blank_image)
    cv2.waitKey(0)

