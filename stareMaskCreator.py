import cv2
import os
import DataPaths
import re

starePath = os.path.join(DataPaths.get_current_path(), "Data", "STARE")

files = [f for f in os.listdir(starePath) if re.match(r'im[0-9]{4}\.ah\.bmp', f)]

imageNumber = 1

for file in files:

    imagePath = os.path.join(starePath, file)
    print(imagePath)
    


    image = cv2.imread(imagePath)
    
    nweImageName = f"im_{imageNumber}_result.bmp"
    cv2.imwrite(os.path.join(starePath, nweImageName), image)
    os.remove(imagePath)
    imageNumber += 1


exit(0)
