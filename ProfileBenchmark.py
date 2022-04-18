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

def read_mask_and_erode_it(imageNumber, dateSet, erodeIteration=3):
    mask = Main.read_mask_image(DataPaths.original_image_mask_path(imageNumber, dateSet), dateSet)
    # create kernel for ongoing erosion
    kernel_erosion = np.ones((5,5),np.uint8)
    # eroding mask
    mask = cv2.erode(mask,kernel_erosion,iterations = erodeIteration)
    return mask

def preprocessing_source_image(imageNumber, dataSet, claheKernelSize=10):
    # reading source image
    pathToSourceImage = DataPaths.original_image_path(numberOfImage=imageNumber, dataSet=dataSet)
    I_src = cv2.imread(pathToSourceImage)
    # splitting image into color channels and keeping only green one
    _, I_green, _ = cv2.split(I_src)
    # inverting green channel
    I_green_inverted = cv2.bitwise_not(I_green)
    #cv2.imwrite(DataPaths.results_image_path("I_green_inverted"), I_green_inverted)
    # using white top hat
    I_top_hat = cv2.morphologyEx(I_green_inverted, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_RECT,(11,11)))
    #cv2.imwrite(DataPaths.results_image_path("I_top_hat"), I_top_hat)
    # creating CLAHE
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(claheKernelSize, claheKernelSize))
    # using CLAHE
    I_clahe = clahe.apply(I_top_hat)
    #cv2.imwrite(DataPaths.results_image_path("I_clahe"), I_clahe)
    return I_clahe


def apply_matched_filtering_on_preprocessed_image(preprocessedImage, profile, mask, thresholdLimit=5, save=False):
    
    # creating kernel from profile
    kernelFromProfile = Main.create_kernel_from_profile(profile)
    # getting final result nad thresholded image
    notThresholded, thresh = Main.apply_kernel_on_image_in_angles(preprocessedImage, kernelFromProfile,show_steps=False, threshold_limit = thresholdLimit)
    # thresholded masked
    thresh = cv2.bitwise_or(thresh, thresh, mask=mask)
    if save:
        cv2.imwrite(DataPaths.results_image_path("NotThresholded"), notThresholded)

    return thresh


if __name__ == "__main__":


    vesselProfile1 = VesselProfile(7, 0.8, "Profil-1", 14)
    vesselProfile2 = VesselProfile(7, 1.2, "Profil-2", 14)
    vesselProfile3 = VesselProfile(7, 0.9, "Profil-7", 14)

    vesselProfiles = [vesselProfile1]

    biggestScore = 0
    biggestScoreName = ""
    bestAccurancy = 0
    bestAccurancyName = ""
    resultsDict = {}
    saveProgress = False

    dataSet = "HRF"
    numberOfImages = 1
    if dataSet == "DRIVE":
        numberOfImages = 10
    else:
        numberOfImages = 45
            
    
    for imageNumber in range(1,numberOfImages+1):
        
        mask = read_mask_and_erode_it(imageNumber, dataSet)
        preprocessedImage = preprocessing_source_image(imageNumber, dataSet)
        if saveProgress:
            cv2.imwrite(DataPaths.results_image_path(f"Preprocessed_{imageNumber}"), preprocessedImage)
        cv2.imshow("temp", preprocessedImage)
        
        manualy_separated = Main.read_mask_image(DataPaths.original_manual_image_path(imageNumber, dataSet), dataSet)
        cv2.imshow("temp2", manualy_separated)
        cv2.waitKey(0)
        for vesselProfilePrimary in vesselProfiles:
            for primaryThreshold in range(3,5):
                primaryFilteringResult = apply_matched_filtering_on_preprocessed_image(preprocessedImage, np.array(invert_profile(vesselProfilePrimary.profile), dtype=np.float32), mask=mask, thresholdLimit=primaryThreshold)
                imageScoreOnlyPrimary = ImageScore.ImageScore(primaryFilteringResult, manualy_separated, mask)
                imageScoreOnlyPrimary.compute_statistics()
                onlyPrimaryName = f"Only_primary{vesselProfilePrimary.name}_{primaryThreshold}"
                if onlyPrimaryName in resultsDict:
                    resultsDict[onlyPrimaryName].append(imageScoreOnlyPrimary.accuracy)
                else:
                    resultsDict[onlyPrimaryName] = [imageScoreOnlyPrimary.accuracy]

                for vesselProfileSecondary in vesselProfiles:
                    for secondaryThreshold in range(3,5):
                        secondaryFilteringResult = apply_matched_filtering_on_preprocessed_image(preprocessedImage, np.array(invert_profile(vesselProfileSecondary.profileSecondDerivative), dtype=np.float32), mask=mask, thresholdLimit=secondaryThreshold)
                        imageScoreOnlySecondary = ImageScore.ImageScore(secondaryFilteringResult, manualy_separated, mask)
                        imageScoreOnlySecondary.compute_statistics()
                        onlySecondaryName = f"Only_secondary{vesselProfileSecondary.name}_{secondaryThreshold}"
                        if onlySecondaryName in resultsDict:
                            resultsDict[onlySecondaryName].append(imageScoreOnlySecondary.accuracy)
                        else:
                            resultsDict[onlySecondaryName] = [imageScoreOnlySecondary.accuracy]



                        finalResult = cv2.bitwise_or(secondaryFilteringResult, primaryFilteringResult)
                        imageName = f"merged_{vesselProfilePrimary.name}_{primaryThreshold}___{vesselProfileSecondary.name}_{secondaryThreshold}"
                        if saveProgress:
                            cv2.imwrite(DataPaths.results_image_path(imageName), finalResult)
                        print(f"-+-+-+-+-+- Image: {imageNumber}, Primary: {vesselProfilePrimary.name}/{primaryThreshold}, Secondary: {vesselProfileSecondary.name}/{secondaryThreshold} -+-+-+-+-+-")
                        imageScore = ImageScore.ImageScore(finalResult, manualy_separated, mask)
                        imageScore.compute_statistics()
                        imageScore.print_score()
                        if imageScore.overallScore > biggestScore:
                            biggestScore = imageScore.overallScore
                            biggestScoreName = imageName
                        if imageScore.accuracy > bestAccurancy:
                            bestAccurancy = imageScore.accuracy
                            bestAccurancyName = imageName
                        if imageName in resultsDict:
                            resultsDict[imageName].append(imageScore.accuracy)
                        else:
                            resultsDict[imageName] = [imageScore.accuracy]
        
                        
    print(f"\nBest Score is: {biggestScoreName} with {biggestScore}")
    print(f"\nBest accuracy is: {bestAccurancyName} with {bestAccurancy}")
    bestProfileAcc = 0
    bestProfileName = ""
    for key in resultsDict:
        resultsDict[key] = sum(resultsDict[key]) / len(resultsDict[key])
        print(f"{resultsDict[key]} pro {key}")
        if resultsDict[key] > bestProfileAcc:
            bestProfileAcc = resultsDict[key]
            bestProfileName = key
    print(f"Nejlepsi ACC je: {bestProfileAcc} a je to profil {bestProfileName}")

