import cv2
import os
import sys
import matplotlib.pyplot as plt
  
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
import Main



if __name__ == "__main__":
    startPoint = [13,9]
    currentPoint = [14,10]
    goldenTruth = cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "SeekingTraining.bmp"), cv2.IMREAD_GRAYSCALE)
    pictureForDrawing = cv2.merge((goldenTruth,goldenTruth,goldenTruth))

    CandidatePoints.track_candidate_point(startPoint, currentPoint, goldenTruth, pictureForDrawing)
    print("END")  
