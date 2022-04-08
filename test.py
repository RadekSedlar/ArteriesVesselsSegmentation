import ProfileBenchmark
import Main
import cv2
from gaussianPlot import VesselProfile
import numpy as np
import DataPaths
import matplotlib.pyplot as plt

preprocessedImage = ProfileBenchmark.preprocessing_source_image()
profile = VesselProfile(7, 0.9, "ProfileTest", 14)
mask = ProfileBenchmark.read_mask_and_erode_it()
primaryFilteringResult = ProfileBenchmark.apply_matched_filtering_on_preprocessed_image(preprocessedImage, np.array(ProfileBenchmark.invert_profile(profile.profile), dtype=np.float32), mask=mask, save=True)
cv2.imwrite(DataPaths.results_image_path("Thresholded_Gauss"),primaryFilteringResult)
cv2.imshow("popis",primaryFilteringResult)
cv2.waitKey(0)
secondaryFilteringResult = ProfileBenchmark.apply_matched_filtering_on_preprocessed_image(preprocessedImage, np.array(ProfileBenchmark.invert_profile(profile.profileSecondDerivative), dtype=np.float32), mask=mask, thresholdLimit=4, save=True)
cv2.imwrite(DataPaths.results_image_path("Thresholded_Gauss_Second"),secondaryFilteringResult)
cv2.imshow("popis2",secondaryFilteringResult)
cv2.waitKey(0)

finalMask = Main.create_kernel_from_profile(profile.profile)

fig = plt.figure(figsize=(1, 3))

fig.add_subplot(1, 3, 1)
plt.imshow(finalMask)

fig.add_subplot(1, 3, 2)
plotMask = Main.rotate_image(finalMask, 15)
plt.imshow(plotMask)

fig.add_subplot(1, 3, 3)
plotMask = Main.rotate_image(finalMask, 90)
plt.imshow(plotMask)

plt.show()

