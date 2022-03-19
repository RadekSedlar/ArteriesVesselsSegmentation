# Standard imports
import cv2
import numpy as np;
import Main
import ImageScore
import DataPaths
from  gaussianPlot import VesselProfile

def invert_profile(profile):
    listToReturn = []
    for item in profile:
        listToReturn.append(item * (-1))
    return listToReturn

def read_mask_and_erode_it(imageNumber=1, erodeIteration=3):
    mask = Main.read_gif_image(DataPaths.original_image_mask_path(numberOfImage=imageNumber))
    # create kernel for ongoing erosion
    kernel_erosion = np.ones((5,5),np.uint8)
    # eroding mask
    mask = cv2.erode(mask,kernel_erosion,iterations = erodeIteration)
    return mask

def preprocessing_source_image(imageNumber=1, claheKernelSize=10):
    # reading source image
    src = cv2.imread(DataPaths.original_image_path(numberOfImage=imageNumber))
    # splitting image into color channels and keeping only green one
    _, G_channel, _ = cv2.split(src)
    # inverting green channel
    G_channel_inverted = cv2.bitwise_not(G_channel)
    # using white top hat
    invert_top__hat_rect = cv2.morphologyEx(G_channel_inverted, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_RECT,(11,11)))
    # creating CLAHE
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(claheKernelSize, claheKernelSize))
    # using CLAHE
    invert_top_hat_rect_clahe = clahe.apply(invert_top__hat_rect)
    return invert_top_hat_rect_clahe


def apply_matched_filtering_on_preprocessed_image(preprocessedImage, profile, mask, thresholdLimit=5):
    
    # creating kernel from profile
    kernelFromProfile = Main.create_kernel_from_profile(profile)
    # getting final result nad thresholded image
    _, thresh = Main.apply_kernel_on_image_in_angles(preprocessedImage, kernelFromProfile,show_steps=False, threshold_limit = thresholdLimit)
    # thresholded masked
    thresh = cv2.bitwise_or(thresh, thresh, mask=mask)
    return thresh


if __name__ == "__main__":


    vesselProfile1 = VesselProfile(7, 0.9, "Profil-1", 14)
    vesselProfile2 = VesselProfile(7, 0.8, "Profil-2", 14)
    vesselProfile3 = VesselProfile(7, 0.7, "Profil-3", 14)
    vesselProfile6 = VesselProfile(7, 1.1, "Profil-6", 14)
    vesselProfile7 = VesselProfile(7, 1.3, "Profil-7", 14)

    vesselProfiles = [vesselProfile1, vesselProfile6, vesselProfile7]

    biggestScore = 0
    biggestScoreName = ""
    bestAccurancy = 0
    bestAccurancyName = ""
    imageNumber = 1
    mask = read_mask_and_erode_it(imageNumber)
    preprocessedImage = preprocessing_source_image(imageNumber=imageNumber)
    cv2.imwrite(DataPaths.results_image_path(f"Preprocessed_{imageNumber}"), preprocessedImage)
    manualy_separated = Main.read_gif_image(DataPaths.original_manual_image_path(numberOfImage=imageNumber))
    for vesselProfilePrimary in vesselProfiles:
        for primaryThreshold in range(2,6):
            primaryFilteringResult = apply_matched_filtering_on_preprocessed_image(preprocessedImage, np.array(invert_profile(vesselProfilePrimary.profile), dtype=np.float32), mask=mask, thresholdLimit=primaryThreshold)
            for vesselProfileSecondary in vesselProfiles:
                for secondaryThreshold in range(2,6):
                    secondaryFilteringResult = apply_matched_filtering_on_preprocessed_image(preprocessedImage, np.array(invert_profile(vesselProfileSecondary.profileSecondDerivative), dtype=np.float32), mask=mask, thresholdLimit=secondaryThreshold)
                    finalResult = cv2.bitwise_or(secondaryFilteringResult, primaryFilteringResult)
                    imageName = f"merged_{vesselProfilePrimary.name}_{primaryThreshold}___{vesselProfileSecondary.name}_{secondaryThreshold}"
                    cv2.imwrite(DataPaths.results_image_path(imageName), finalResult)
                    print(f"-+-+-+-+-+- Primary: {vesselProfilePrimary.name}/{primaryThreshold}, Secondary: {vesselProfileSecondary.name}/{secondaryThreshold} -+-+-+-+-+-")
                    imageScore = ImageScore.ImageScore(finalResult, manualy_separated, mask)
                    imageScore.compute_statistics()
                    imageScore.print_score()
                    if imageScore.overallScore > biggestScore:
                        biggestScore = imageScore.overallScore
                        biggestScoreName = imageName
                    if imageScore.accuracy > bestAccurancy:
                        bestAccurancy = imageScore.accuracy
                        bestAccurancyName = imageName
    print(f"\nBest Score is: {biggestScoreName} with {biggestScore}")
    print(f"\nBest accuracy is: {bestAccurancyName} with {bestAccurancy}")
                
            

    