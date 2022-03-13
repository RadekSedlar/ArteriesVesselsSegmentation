import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import derivative



class VesselProfile(object):
    def __init__(self, mu, sig, name, profileSize):
        self.name = name
        self.mu = mu
        self.sig = sig
        self.x_values = np.linspace(0, 14, 140)

        max_gauss_Value = 0

        for value in self.x_values:
            y = gaussian(value, mu, sig)
            if y > max_gauss_Value:
                max_gauss_Value = y

        self.gaussSubtractedFromMax = gaussian_subtractMax(self.x_values, mu, sig, max_gauss_Value)

        mean = np.mean(self.gaussSubtractedFromMax)

        self.gaussMeanSubtracted = gaussian_subtractMean(self.x_values, mu, sig, max_gauss_Value, mean)

        self.profile = self.gaussMeanSubtracted[::10]


        gauss_second_derivative = gaussian_secondDerivative(self.x_values, self.mu, self.sig)
        self.profileSecondDerivative = np.average(gauss_second_derivative.reshape(-1, 10), axis=1)
    
    def print_profiles(self):
        print(f"-+-+-+-+-+-+- Profile {self.name} -+-+-+-+-+-+-")
        print(f"Profile: {self.profile}")
        print(f"Profile second derivative: {self.profileSecondDerivative}")

    def plot_profile(self):
        fig, ax = plt.subplots()
        gaussianPlot, = ax.plot(self.x_values, gaussian(self.x_values, self.mu, self.sig), label="Hodnoty Gaussova rozdeleni")
        gaussianDerivativePlot, = ax.plot(self.x_values, gaussian_secondDerivative(self.x_values, self.mu, self.sig), label="Hodnoty 2. derivace Gaussova rozdeleni")
        gaussSubtractedFromMaxPlot, = ax.plot(self.x_values, self.gaussSubtractedFromMax, label="Hodnoty Gaussova rozdeleni po odecteni maxima")
        gaussMeanSubtractedPlot, = ax.plot(self.x_values, self.gaussMeanSubtracted, label="Hodnoty Gaussova rozdeleni po odecteni prumeru")
        
        ax.scatter(np.arange(len(self.profile)), self.profile)
        # Create a legend for the first line.
        first_legend = ax.legend(handles=[gaussianPlot, gaussianDerivativePlot, gaussSubtractedFromMaxPlot, gaussMeanSubtractedPlot], loc='lower right')

        # Add the legend manually to the Axes.
        ax.add_artist(first_legend)


        plt.show()


    
        

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def gaussian_subtractMax(x, mu, sig, maxVal):
    return maxVal - gaussian(x, mu, sig)

def gaussian_subtractMean(x, mu, sig, maxVal, mean):
    return gaussian_subtractMax(x, mu, sig, maxVal) - mean

def gaussian_secondDerivative(x_values, mu, sig):
    return derivative(gaussian, x_values, n=2, args=(mu, sig))



if __name__ == "__main__":
    
    profileSize = 14
    mu = profileSize/2
    sig = 0.9

    profilInfo = VesselProfile(mu, sig, "Muj profil", profileSize)
    profilInfo.print_profiles()
    profilInfo.plot_profile()