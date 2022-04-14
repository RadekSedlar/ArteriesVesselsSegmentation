from lib2to3.pgen2 import driver
import os

def get_current_path():
    """ Gets path of directory, where script have been executed

    @rtype: string
    @returns: path of directory, where script have been executed"""
    return os.path.dirname(os.path.abspath(__file__))

def __adjust_and_check_image_number(numberOfImage, dataSet):
    """ Checks if @numberOfImage is in range of available images and adjust it for further use.

    @type numberOfImage: int
    @param numberOfImage: number of image we want to use

    @rtype: int
    @returns: Checked and adjusted image number."""
    if dataSet == "DRIVE":
        numberOfImage += 20 # images starting from 21 and ending with 40
        if numberOfImage < 21 or numberOfImage > 40:
            raise Exception(f"Image numbers are starting from 21 and ending with 40. You wanted image number {numberOfImage}")
        return numberOfImage
    if numberOfImage < 0 or numberOfImage > 45:
         raise Exception(f"Image numbers are starting from 1 and ending with 45. You wanted image number {numberOfImage}")
    return numberOfImage
        

def original_image_path(numberOfImage=1, dataSet="DRIVE"):
    """ Gets path of original image.

    @type numberOfImage: int
    @param numberOfImage: number of image we want to use

    @rtype: string
    @returns: Path of original image."""

    check_name_of_dataset(dataSet)
    numberOfImage = __adjust_and_check_image_number(numberOfImage, dataSet)
    nameOfImageFile = create_original_image_name(numberOfImage, dataSet)

    return os.path.join(get_current_path(), "Data", dataSet, nameOfImageFile)

def check_name_of_dataset(name):
    if name == "DRIVE" or name == "HRF":
        return
    raise Exception(f"Bad dataset name {name}")


def original_manual_image_path(numberOfImage=1, dataSet="DRIVE"):
    """ Gets path of manualy segmented original image.

    @type numberOfImage: int
    @param numberOfImage: number of image we want to use

    @rtype: string
    @returns: Path of manualy segmented original image."""
    check_name_of_dataset(dataSet)
    numberOfImage = __adjust_and_check_image_number(numberOfImage, dataSet)
    nameOfImageFile = create_original_manual_image_name(numberOfImage, dataSet)
    return os.path.join(get_current_path(), "Data", dataSet, nameOfImageFile)

def original_image_mask_path(numberOfImage=1, dataSet="DRIVE"):
    """ Gets path of mask of original image.

    @type numberOfImage: int
    @param numberOfImage: number of image we want to use

    @rtype: string
    @returns: Path of mask of original image."""
    check_name_of_dataset(dataSet)
    numberOfImage = __adjust_and_check_image_number(numberOfImage, dataSet)
    nameOfImageFile = create_mask_name(numberOfImage, dataSet)
    return os.path.join(get_current_path(), "Data", dataSet, nameOfImageFile)

def results_image_path(nameOfImage):
    """ Gets path to image located in 'Results' folder.

    @type nameOfImage: string
    @param nameOfImage: name of image we want to use

    @rtype: string
    @returns: Path to image located in 'Results' folder."""
    wholeImageName = f"{nameOfImage}.bmp"
    return os.path.join(get_current_path(), "Results", wholeImageName)

def skeletonize_results_image_path(nameOfImage):
    """ Gets path to image located in 'Results/Skeletonize' folder.

    @type nameOfImage: string
    @param nameOfImage: name of image we want to use

    @rtype: string
    @returns: Path to image located in 'Results/Skeletonize' folder."""
    wholeImageName = f"{nameOfImage}.bmp"
    return os.path.join(get_current_path(), "Results", "Skeletonize", wholeImageName)

def results_path():
    """ Gets path to 'Results' folder.

    @rtype: string
    @returns: Path to 'Results' folder."""
    return os.path.join(get_current_path(), "Results")


def create_mask_name(imageNumber, dataSet):
    if dataSet == "DRIVE":
        return create_mask_name_DRIVE(imageNumber)
    return create_mask_name_HRF(imageNumber)

def create_mask_name_DRIVE(imageNumber):
    return f"{imageNumber}_training_mask.gif"

def create_mask_name_HRF(imageNumber):
    number = ((imageNumber-1)//3)+1
    modulo = (imageNumber-1)%3

    if modulo == 0:
        return os.path.join("mask", f"{str(number).zfill(2)}_dr_mask.tif")
    elif modulo == 1:
        return os.path.join("mask", f"{str(number).zfill(2)}_g_mask.tif")
    elif modulo == 2:
        return os.path.join("mask", f"{str(number).zfill(2)}_h_mask.tif")

def create_original_image_name(imageNumber, dataSet):
    if dataSet == "DRIVE":
        return create_original_image_name_DRIVE(imageNumber)
    return create_original_image_name_HRF(imageNumber)

def create_original_image_name_HRF(imageNumber):
    number = ((imageNumber-1)//3)+1
    modulo = (imageNumber-1)%3

    if modulo == 0:
        return os.path.join("images", f"{str(number).zfill(2)}_dr.jpg")
    elif modulo == 1:
        return os.path.join("images", f"{str(number).zfill(2)}_g.jpg")
    elif modulo == 2:
        return os.path.join("images", f"{str(number).zfill(2)}_h.jpg")

def create_original_image_name_DRIVE(imageNumber):
    return f"{imageNumber}_training.tif"

def create_original_manual_image_name(imageNumber, dataSet):
    if dataSet == "DRIVE":
        return create_original_manual_image_name_DRIVE(imageNumber)
    return create_original_manual_image_name_HRF(imageNumber)

def create_original_manual_image_name_HRF(imageNumber):
    number = ((imageNumber-1)//3)+1
    modulo = (imageNumber-1)%3

    if modulo == 0:
        return os.path.join("manual1", f"{str(number).zfill(2)}_dr.tif")
    elif modulo == 1:
        return os.path.join("manual1", f"{str(number).zfill(2)}_g.tif")
    elif modulo == 2:
        return os.path.join("manual1", f"{str(number).zfill(2)}_h.tif")

def create_original_manual_image_name_DRIVE(imageNumber):
    return f"{imageNumber}_manual1.gif"
