import cv2
import pywt
import numpy as np;
from matplotlib import pyplot as plt
import os
import matplotlib
import scipy.misc
import imutils
import math

def rotate_image(image, angle):
    return imutils.rotate(image, angle=angle)

def CreateKernelFromProfile(profile):
    r = profile.size/2
    print(f"Kernel raduis: {r}")

    center_to_corner_distance = math.sqrt(2*(r*r))
    print(f"Kernel center to corner distance: {center_to_corner_distance}")
    center_to_corner_distance_rounded = math.ceil(center_to_corner_distance)
    print(f"Kernel center to corner distance rounded: {center_to_corner_distance_rounded}")
    numberOfCellsAdded =  math.ceil(center_to_corner_distance_rounded - r)
    print(f"Number of added boundaries: {numberOfCellsAdded}")

    for i in range(np.int_(numberOfCellsAdded)):
        profile = np.append(profile, 0)
    for i in range(np.int_(numberOfCellsAdded)):
        profile = np.insert(profile, 0, 0)
    kernelFromProfile = profile
    for item in range(profile.size -1):
        kernelFromProfile = np.vstack((kernelFromProfile, profile))
    kernelFromProfile = kernelFromProfile / (profile.size -1)
    return kernelFromProfile

profile = np.array([0.10120511800050735, 0.10120511800050735, 0.10120511800050735, 0.10120511800050735, 0.10120406001806259, 0.09894951432943344, -0.12007845938205719, -0.8986409902572632, -0.10686760395765305, 0.09921079874038696, 0.10120423883199692, 0.10120511800050735, 0.10120511800050735, 0.10120511800050735, 0.10120511800050735],dtype=np.float32)

print(profile)

kernelFromProfile = CreateKernelFromProfile(profile)
print(kernelFromProfile)

script_path = os.path.abspath(__file__)
print(script_path)
dir_path = os.path.dirname(script_path)
print(dir_path)

cv2.imwrite(dir_path + "\\mask2.jpg", kernelFromProfile)


w = 10
h = 10
fig = plt.figure(figsize=(9, 13))
columns = 4
rows = 5
ax = []

rotation_angle = 0

ax.append( fig.add_subplot(1, 3, 1) )
ax[-1].set_title("Angle: " + str(rotation_angle), fontsize=20)
for label in (ax[-1].get_xticklabels() + ax[-1].get_yticklabels()):
    label.set_fontsize(16)
rotated_image = rotate_image(kernelFromProfile, rotation_angle)
croppedImage = rotated_image[4:-4, 4:-4]
plt.imshow(croppedImage)

rotation_angle = 15
ax.append( fig.add_subplot(1, 3, 2) )
ax[-1].set_title("Angle: " + str(rotation_angle), fontsize=20)
for label in (ax[-1].get_xticklabels() + ax[-1].get_yticklabels()):
    label.set_fontsize(16)
rotated_image = rotate_image(kernelFromProfile, rotation_angle)
croppedImage = rotated_image[4:-4, 4:-4]
plt.imshow(croppedImage)

rotation_angle = 90
ax.append( fig.add_subplot(1, 3, 3) )
ax[-1].set_title("Angle: " + str(rotation_angle), fontsize=20)
for label in (ax[-1].get_xticklabels() + ax[-1].get_yticklabels()):
    label.set_fontsize(16)
rotated_image = rotate_image(kernelFromProfile, rotation_angle)
croppedImage = rotated_image[4:-4, 4:-4]
plt.imshow(croppedImage)

plt.show()  # finally, render the plot



