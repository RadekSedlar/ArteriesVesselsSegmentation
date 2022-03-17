import cv2
from cv2 import split
import os
import sys
import os
  
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
  
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
  
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)
  
# now we can import the module in the parent
# directory.
import CandidatePoints


def setPixel(image, normalCoordinates, color):
    image[normalCoordinates[1],normalCoordinates[0]] = color

src = cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "SeekingTraining.bmp"))
print(src.shape)
_, _, grayScale = cv2.split(src)

startingPoint = [14,10]
setPixel(src, startingPoint, (0,0,255))


CandidatePoints.draw_small_circle(src, startingPoint)







cv2.imshow("image_with_circle", src)
cv2.imwrite(os.path.join(os.path.dirname(os.path.abspath(__file__)), "SeekingTrainingResult.bmp"), src)
cv2.waitKey(0)