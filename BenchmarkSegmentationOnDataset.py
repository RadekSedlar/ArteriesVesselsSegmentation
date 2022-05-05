import numpy as np
import cv2
import ImageScore
import os
import Main
import DataPaths
from ProfileBenchmark import apply_matched_filtering_on_preprocessed_image, invert_profile, preprocessing_source_image, read_mask_and_erode_it
from gaussianPlot import VesselProfile
import sys

def runScript(dataSet, numberOfImages, saveProgress, vesselProfilePrimary, vesselProfileSecondary, primaryThreshold, secondaryThreshold ):
    acumulatedSensitivity = 0.0
    acumulatedSpecificity = 0.0
    acumulatedAccuracy = 0.0
    f = open(os.path.join(DataPaths.results_path(), "RecentResults.txt"), "w")
    for imageNumber in range(1,(numberOfImages+1)):
        print(f"IMAGE NUMBER =>>>> {imageNumber}")
        mask = read_mask_and_erode_it(imageNumber, dataSet)
        preprocessedImage = preprocessing_source_image(imageNumber, dataSet)
        pathToImage = DataPaths.original_manual_image_path(imageNumber, dataSet)
        manualy_separated = Main.read_mask_image(pathToImage, dataSet)

        primaryFilteringResult = apply_matched_filtering_on_preprocessed_image(preprocessedImage, np.array(invert_profile(vesselProfilePrimary.profile), dtype=np.float32), mask=mask, thresholdLimit=primaryThreshold)
        secondaryFilteringResult = apply_matched_filtering_on_preprocessed_image(preprocessedImage, np.array(invert_profile(vesselProfileSecondary.profileSecondDerivative), dtype=np.float32), mask=mask, thresholdLimit=secondaryThreshold)
        finalResult = cv2.bitwise_or(secondaryFilteringResult, primaryFilteringResult)
        imageName = f"{imageNumber}_merged_{vesselProfilePrimary.name}_{primaryThreshold}___{vesselProfileSecondary.name}_{secondaryThreshold}"
        if saveProgress:
            cv2.imwrite(DataPaths.results_image_path(imageName), finalResult)
        imageScore = ImageScore.ImageScore(finalResult, manualy_separated, mask)
        imageScore.compute_statistics()
        imageScore.print_score()

        f.write(f"{pathToImage}\n")
        f.write(f"ACC: {imageScore.accuracy * 100}\n")
        f.write(f"SN: {imageScore.sensitivity * 100}\n")
        f.write(f"SP: {imageScore.specificity * 100}\n")


        if imageNumber == 11:
            cv2.imshow("original", manualy_separated)
            cv2.imshow("result", finalResult)
            cv2.waitKey(0)
            cv2.imwrite(DataPaths.results_image_path(f"stare_{imageNumber}_result"),finalResult)
            cv2.imwrite(DataPaths.results_image_path(f"stare_{imageNumber}_original"),manualy_separated)
            
        #97.6\% & 43.4\% & 91.06\%\\
        formatedSpecificity = "{:.2f}".format(imageScore.specificity * 100)
        formatedSensitivity = "{:.2f}".format(imageScore.sensitivity * 100)
        formatedAccuracy = "{:.2f}".format(imageScore.accuracy * 100)
        f.write(f"{formatedSpecificity}\\% & {formatedSensitivity}\\% & {formatedAccuracy}\\% \\\\\n")

        acumulatedAccuracy += imageScore.accuracy
        acumulatedSensitivity += imageScore.sensitivity
        acumulatedSpecificity += imageScore.specificity
        

    acumulatedAccuracy = acumulatedAccuracy / 20
    acumulatedSensitivity = acumulatedSensitivity / 20
    acumulatedSpecificity = acumulatedSpecificity / 20

    print("Overall score")
    print(f"Accuracy => {acumulatedAccuracy}")
    print(f"Sensitivity => {acumulatedSensitivity}")
    print(f"Specificity => {acumulatedSpecificity}")

    f.close()



def create_vessel_profile_from_user_input(profileNumber):
    mu = float(input("Zadejte mu: "))
    sigma = float(input("Zadejte sigma: "))
    vesselWidth = int(input("Zadejte sirku profilu: "))
    return VesselProfile(mu, sigma, f"Profil-{profileNumber}", vesselWidth)

def main(args):

    if len(args) != 3:
        print(f"Musi byt zadana databaze a zda chceme prubezne vysledky ukladat a jak sestavit profily")
        exit(0)

    ukladat = bool(args[1])


    pocetSnimku = 0
    if args[0] == "STARE":
        pocetSnimku = 20
    elif args[0] == "DRIVE":
        pocetSnimku = 10
    elif args[0] == "HRF":
        pocetSnimku = 45
    else:
        print(f"Databaze {args[0]} neni podporovana")
        exit(0)

    if args[2] == "best":
        vesselProfilePrimary =  VesselProfile(7, 0.8, "Profil-1", 14)
        vesselProfileSecondary = VesselProfile(7, 0.8, "Profil-1", 14)
        primaryThreshold = 4
        secondaryThreshold = 3
        runScript(args[0], pocetSnimku, ukladat, vesselProfilePrimary, vesselProfileSecondary, primaryThreshold, secondaryThreshold)
    elif args[2] == "custom":
        profile1 = create_vessel_profile_from_user_input(1)
        primaryThreshold = int(input("Zadejte threshold prvniho profilu: "))
        profile2 = create_vessel_profile_from_user_input(2)
        secondaryThreshold = int(input("Zadejte threshold druheho profilu: "))
        runScript(args[0], pocetSnimku, ukladat, profile1, profile2, primaryThreshold, secondaryThreshold)
    else:
        print(f"Argument nemuze byt {args[2]}, musi nabyvat hodnot: best, custom")
        exit(0)
        
    

if __name__ == "__main__":
    main(sys.argv[1:])