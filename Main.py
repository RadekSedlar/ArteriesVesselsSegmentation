# Standard imports
import cv2
import numpy as np;
import imutils
import math
import DataPaths
from enum import Enum

class VesselOrientation(Enum):
    HORIZONTAL = 1
    VERTICAL = 2
    LEFT_UP_RIGHT_DOWN = 3
    LEFT_DOWN_RIGHT_UP = 4
        
        

def create_kernel_from_profile(profile):
    """ Creates kernel from profile

    @type profile: [float32]
    @param profile: array of float32 representing gaussian profile of vessels
    
    @rtype: ([[float32]],int)
    @returns: Matrix of float32 representing kernel and number of cells added on edges for smooth rotation of kernel"""
    r = profile.size/2

    center_to_corner_distance = math.sqrt(2*(r*r))
    #print(f"Kernel center to corner distance: {center_to_corner_distance}")
    center_to_corner_distance_rounded = math.ceil(center_to_corner_distance)
    #print(f"Kernel center to corner distance rounded: {center_to_corner_distance_rounded}")
    numberOfCellsAdded =  math.ceil(center_to_corner_distance_rounded - r)
    #print(f"Number of added boundaries: {numberOfCellsAdded}")

    for i in range(np.int_(numberOfCellsAdded)):
        profile = np.append(profile, 0)
    for i in range(np.int_(numberOfCellsAdded)):
        profile = np.insert(profile, 0, 0)
    kernelFromProfile = profile
    for item in range(profile.size -1):
        kernelFromProfile = np.vstack((kernelFromProfile, profile))
    kernelFromProfile = kernelFromProfile / (profile.size -1)
    return kernelFromProfile

def apply_kernel_on_image_in_angles(grayScaleImage, kernel, show_steps=False, threshold_limit = 5):
    """ Creates kernel from profile

    @type grayScaleImage: [[uint8]]
    @param grayScaleImage: image of vessels in grayscale
    @type kernel: [[float32]]
    @param kernel: matrix of float32 representing gaussian profile of vessels
    @type show_steps: bool
    @param show_steps: turning info ON/OFF
    @type threshold_limit: int
    @param threshold_limit: limit differentiating vessel from background
    
    
    @rtype: ([[uint8]],[[uint8]])
    @returns: Image with 0 to 255 values and threshodled image with only 0 and 255 values"""
    kernel_used_for_filter = kernel
    angle_sum = sum(sum(kernel_used_for_filter))
    number_of_elements_in_matrix = kernel_used_for_filter.shape[0]*kernel_used_for_filter.shape[1]
    kernel_used_for_filter = kernel_used_for_filter - (angle_sum/number_of_elements_in_matrix)
    result = cv2.filter2D(grayScaleImage, -1, kernel_used_for_filter)
    max_values_in_image = result.max()
    (_,threshold_All) = cv2.threshold(result, max_values_in_image/threshold_limit,255,cv2.THRESH_BINARY)
    if show_steps:
        cv2.imshow("result angle 0", result)
        
        cv2.imshow(f"result angle 0 thresholded ", threshold_All)
        print(f"result angle 0 has sum: {angle_sum}")
    step_angle = 15
    for item in range(11):
        rotatedKernel = rotate_image(kernel, step_angle)
        angle_sum = sum(sum(rotatedKernel))
        rotatedKernel = rotatedKernel - (angle_sum / number_of_elements_in_matrix)
        step = cv2.filter2D(grayScaleImage, -1, rotatedKernel)
        
        max_values_in_image = step.max()
        (_,thresholded) = cv2.threshold(step, max_values_in_image/threshold_limit,255,cv2.THRESH_BINARY)
        if show_steps:
            cv2.imshow(f"result angle {step_angle}", step)
            
            cv2.imshow(f"result angle {step_angle} thresholded ", thresholded)
            print(f"result angle {step_angle} has sum: {angle_sum}")
        result = cv2.bitwise_or(result,step)
        threshold_All = cv2.bitwise_or(threshold_All, thresholded)
        step_angle = step_angle + 15
    if show_steps:
        cv2.imshow(f"Thresholded compiled", threshold_All)
    return (result, threshold_All)


def apply_CLAHE(image, limit = 3, GridSize = 80):
    """ Apply CLAHE on image

    @type image: [[uint8]]
    @param image: image of vessels in grayscale
    @type limit: int
    @param limit: Threshold for contrast limiting.
    @type GridSize: int
    @param GridSize: size of grid where equalization will be apllied
   
    
    @rtype: [[uint8]]
    @returns: Image with 0 to 255 values"""
    clahe = cv2.createCLAHE(clipLimit=limit, tileGridSize=(GridSize, GridSize))
    return clahe.apply(image)

def rotate_image(image, angle):
    """ Rotates image by a certain angle

    @type image: [[uint8]]
    @param image: image of vessels in grayscale
    @type angle: float32
    @param angle: angle.
    
    @rtype: [[uint8]]
    @returns: Image with 0 to 255 values rotated by certain angle"""
    return imutils.rotate(image, angle=angle)





def read_gif_image(path):
    """ Rotates image by a certain angle

    @type path: string
    @param path: path to .gif image
    
    @rtype: [[uint8]]
    @returns: Image with 0 to 255 values"""
    cap = cv2.VideoCapture(path)
    ret, mask = cap.read()
    cap.release()
    B_mask, G_mask, R_mask = cv2.split(mask)
    return G_mask
    


if __name__ == "__main__":
    number_of_image = 1
    #read image
    src = cv2.imread(DataPaths.original_image_path(number_of_image))
    print(src.shape)
    # try to mask instrument pupil edge
    mask = read_gif_image(DataPaths.original_image_mask_path(number_of_image))
    B_separated, G_separated, R_separated = cv2.split(src)
    cv2.imshow("B", B_separated)
    cv2.imshow("G", G_separated)
    cv2.imshow("R", R_separated)
    output = cv2.bitwise_or(G_separated, G_separated, mask=mask)
    cv2.imshow("source masked", output)
    # CLAHE
    # CLAHE on G channel
    equalized = apply_CLAHE(output)
    cv2.imshow("equalized", equalized)
    equalized = cv2.bitwise_or(equalized, equalized, mask=mask)
    cv2.imshow("equalized masked", equalized)
    # reduced noise
    #noise_reduc = cv2.fastNlMeansDenoising(bgr_reconstructed, h=1)
    #cv2.imshow("Noise reduction", noise_reduc)
    # split BGR image to channels
    #B_denoised, G_denoised, R_denoised = cv2.split(noise_reduc)
    #cv2.imshow("G_denoised", G_denoised)
    
    # Profile 1
    profile1 = np.array([40,40,40,40, 25, -35, -40, -50, -60, -60, -50, -40, -35, 25, 40, 40,40,40],dtype=np.float32)
    profile1 = profile1 / 100
    print(f"sum of profile1 is: {sum(profile1)}")
    kernelFromProfile1 = create_kernel_from_profile(profile1)
    result1, thresh1 = apply_kernel_on_image_in_angles(equalized, kernelFromProfile1)
    cv2.imwrite(DataPaths.results_image_path("9_1_result1"), result1)
    cv2.imwrite(DataPaths.results_image_path("9_1_thresh1"), thresh1)
    # Profile 2
    #profile2 = np.array([40,40,40,40,40, 30, -15, -20, -40, -50,-55,-50,-50,-55 -50, -40, -20, -15, 30, 40, 40,40,40,40],dtype=np.float32)
    #profile2 = np.transpose()
    #print(f"sum of profile2 is: {sum(profile2)}")
    kernelFromProfile2 = np.transpose(kernelFromProfile1)
    result2, thresh2 = apply_kernel_on_image_in_angles(equalized, kernelFromProfile2)
    cv2.imwrite(DataPaths.results_image_path("9_2_result2"), result2)
    cv2.imwrite(DataPaths.results_image_path("9_2_thresh2"), thresh2)
    # Profile 3
    profile3 = np.array([0.31633472442626953, 0.3105391561985016, 0.2857006788253784, 0.2072349339723587, 0.027591779828071594, -0.2603360116481781, -0.5555772185325623, -0.6825006604194641, -0.550753653049469, -0.25396889448165894, 0.03237013891339302, 0.20965129137039185, 0.2865690588951111, 0.3107662796974182, 0.31637847423553467],dtype=np.float32)
    print(f"sum of profile3 is: {sum(profile3)}")
    kernelFromProfile3 = create_kernel_from_profile(profile3)
    result3, thresh3 = apply_kernel_on_image_in_angles(equalized, kernelFromProfile3)
    cv2.imwrite(DataPaths.results_image_path("9_3_result3"), result3)
    cv2.imwrite(DataPaths.results_image_path("9_3_thresh3"), thresh3)
    # Profile 4
    profile4 = np.array([0.2787064015865326, 0.27806562185287476, 0.2723526954650879, 0.23917321860790253, 0.11567062884569168, -0.16909335553646088, -0.5409485101699829, -0.7212237119674683, -0.5343244075775146, -0.1618843674659729, 0.11959248781204224, 0.24043728411197662, 0.2726072669029236, 0.2780984044075012, 0.27870914340019226],dtype=np.float32)
    print(f"sum of profile4 is: {sum(profile4)}")
    kernelFromProfile4 = create_kernel_from_profile(profile4)
    result4, thresh4 = apply_kernel_on_image_in_angles(equalized, kernelFromProfile4)
    cv2.imwrite(DataPaths.results_image_path("9_4_result4"), result4)
    cv2.imwrite(DataPaths.results_image_path("9_4_thresh4"), thresh4)
    # Profile 5
    profile5 = np.array([0.11699070036411285, 0.11699070036411285, 0.11699070036411285, 0.11699061095714569, 0.11688151955604553, 0.09940937906503677, -0.25085121393203735, -0.8829072713851929, -0.23613952100276947, 0.10078757256269455, 0.11689410358667374, 0.11699062585830688, 0.11699070036411285, 0.11699070036411285, 0.11699070036411285],dtype=np.float32)
    print(f"sum of profile5 is: {sum(profile5)}")
    kernelFromProfile5 = create_kernel_from_profile(profile5)
    result5, thresh5 = apply_kernel_on_image_in_angles(equalized, kernelFromProfile5)
    cv2.imwrite(DataPaths.results_image_path("9_5_result5"), result5)
    cv2.imwrite(DataPaths.results_image_path("9_5_thresh5"), thresh5)


    cv2.imshow("thresh5", thresh5)
    # Perform an area filter on the binary blobs:
    componentsNumber, labeledImage, componentStats, componentCentroids = \
    cv2.connectedComponentsWithStats(thresh5, connectivity=8)

    # Set the minimum pixels for the area filter:
    minArea = 10

    # Get the indices/labels of the remaining components based on the area stat
    # (skip the background component at index 0)
    remainingComponentLabels = [i for i in range(1, componentsNumber) if componentStats[i][4] >= minArea]

    # Filter the labeled pixels based on the remaining labels,
    # assign pixel intensity to 255 (uint8) for the remaining pixels
    filteredImage = np.where(np.isin(labeledImage, remainingComponentLabels) == True, 255, 0).astype("uint8")
    cv2.imshow("filteredImage", filteredImage)
    cv2.waitKey(0)