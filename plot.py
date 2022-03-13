import cv2
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from numpy.core.fromnumeric import size
from numpy.lib.function_base import append
import math


def AngleBtw2Points(pointA, pointB):
    changeInX = pointB[0] - pointA[0]
    changeInY = pointB[1] - pointA[1]
    return math.atan2(changeInY,changeInX) #remove degrees if you want your answer in radians

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

profile = np.array([0.4, 0.2, 0.1, 0, -0.17, -0.34, -0.5, -0.5, -0.34, -0.17, 0, 0.1, 0.2, 0.4],dtype=np.float32)

OriginalKernel = profile
for item in range(profile.size -1):
    OriginalKernel = np.vstack((OriginalKernel, profile))




print(profile)
originalMatrixHalfSize = (profile.size-1)/2
print(f"originalMatrixHalfSize: {originalMatrixHalfSize}")
newMatrixHalfSize = np.sqrt(2 * (originalMatrixHalfSize*originalMatrixHalfSize))
print(f"newMatrixHalfSize: {newMatrixHalfSize}")
halfSizeDiff = newMatrixHalfSize - originalMatrixHalfSize
print(f"halfSizeDiff: {halfSizeDiff}")
numberOfCellsAdded = np.rint(halfSizeDiff)
print(f"numberOfCellsAdded: {numberOfCellsAdded}")
for i in range(np.int_(numberOfCellsAdded)):
    profile = np.append(profile, 0)
for i in range(np.int_(numberOfCellsAdded)):
    profile = np.insert(profile, 0, 0)
print(profile)

kernelFromProfile = profile
print(profile.size)
print(profile.shape)
print(kernelFromProfile.shape)


for item in range(profile.size -1):
    kernelFromProfile = np.vstack((kernelFromProfile, profile))
print("After")
print(kernelFromProfile)
print(kernelFromProfile.shape)


#cv2.imshow("kernelFromProfileResized", kernelFromProfileResized)
#cv2.imwrite("kernelFromProfileResized.jpg", kernelFromProfileResized)
#cv2.waitKey(0)

kernelFromProfile = rotate_image(kernelFromProfile, 45)


X = np.arange(0,20)
Y = np.arange(0, 20)
X, Y = np.meshgrid(X, Y)
R = np.sqrt(X**2 + Y**2)
Z = np.sin(R)
fig = plt.figure()
ax = fig.gca(projection='3d')
surf = ax.plot_surface(X, Y, kernelFromProfile, rstride=1, cstride=1,cmap=cm.coolwarm, linewidth=0, antialiased=False)
ax.set_zlim(-1.01, 1.01)

fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()