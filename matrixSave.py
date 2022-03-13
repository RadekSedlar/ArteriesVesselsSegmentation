from PIL import Image
import numpy as np
import scipy
import cv2

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

lastMax = kernelFromProfile.max()
lastMin = kernelFromProfile.min()

intervalDiff = lastMax - lastMin


#Rescale to 0-255 and convert to uint8
rescaled = (255.0 / kernelFromProfile.max() * (kernelFromProfile - kernelFromProfile.min())).astype(np.uint8)

im = Image.fromarray(rescaled)
im.save('kernelFromProfile.png')

kernelFromImage = cv2.imread('kernelFromProfile.png', flags=cv2.IMREAD_GRAYSCALE)

rescaled = ((kernelFromProfile / 255.0)*intervalDiff).astype(np.float32)
print(rescaled)