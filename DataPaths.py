import os

def get_current_path():
    """ Gets path of directory, where script have been executed

    @rtype: string
    @returns: path of directory, where script have been executed"""
    return os.path.dirname(os.path.abspath(__file__))

def __adjust_and_check_image_number(numberOfImage):
    """ Checks if @numberOfImage is in range of available images and adjust it for further use.

    @type numberOfImage: int
    @param numberOfImage: number of image we want to use

    @rtype: int
    @returns: Checked and adjusted image number."""
    numberOfImage += 20 # images starting from 21 and ending with 40
    if numberOfImage < 21 or numberOfImage > 40:
        raise Exception(f"Image numbers are starting from 21 and ending with 40. You wanted image number {numberOfImage}")
    return numberOfImage

def original_image_path(numberOfImage=1):
    """ Gets path of original image.

    @type numberOfImage: int
    @param numberOfImage: number of image we want to use

    @rtype: string
    @returns: Path of original image."""
    numberOfImage = __adjust_and_check_image_number(numberOfImage)
    nameOfImageFile = f"{numberOfImage}_training.tif"
    return os.path.join(get_current_path(), "Data", nameOfImageFile)

def original_manual_image_path(numberOfImage=1):
    """ Gets path of manualy segmented original image.

    @type numberOfImage: int
    @param numberOfImage: number of image we want to use

    @rtype: string
    @returns: Path of manualy segmented original image."""
    numberOfImage = __adjust_and_check_image_number(numberOfImage)
    nameOfImageFile = f"{numberOfImage}_manual1.gif"
    return os.path.join(get_current_path(), "Data", nameOfImageFile)

def original_image_mask_path(numberOfImage=1):
    """ Gets path of mask of original image.

    @type numberOfImage: int
    @param numberOfImage: number of image we want to use

    @rtype: string
    @returns: Path of mask of original image."""
    numberOfImage = __adjust_and_check_image_number(numberOfImage)
    nameOfImageFile = f"{numberOfImage}_training_mask.gif"
    return os.path.join(get_current_path(), "Data", nameOfImageFile)

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