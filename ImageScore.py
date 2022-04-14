class ImageScore(object):
    def __init__(self, endImage, goldenStandard, mask):
        if endImage.shape != goldenStandard.shape:
            print(f"endImage has different shape than goldenStandard")
            raise Exception("endImage has different shape than goldenStandard")
        self.endImage = endImage
        self.goldenStandard = goldenStandard
        self.mask = mask
        self.truePositive = 0
        self.trueNegative = 0
        self.falsePositive = 0
        self.falseNegative = 0
        self.accuracy = 0
        self.sensitivity = 0
        self.specificity = 0
        self.positivePredictiveValue = 0
        self.negativePredictiveValue = 0
        self.overallScore = 0
    
        
    def compute_statistics(self):
        truePositive = 0
        trueNegative = 0
        falsePositive = 0
        falseNegative = 0
        rows, cols = self.endImage.shape
        for x in range(rows):
            for y in range(cols):
                if self.mask[x,y] == 0:
                    continue
                    
                if self.goldenStandard[x,y] == 0:
                    if self.endImage[x,y] == 0:
                        trueNegative += 1
                    else:
                        falsePositive += 1
                else:
                    if self.endImage[x,y] == 0:
                        falseNegative += 1
                    else:
                        truePositive += 1
        self.truePositive = truePositive
        self.trueNegative = trueNegative
        self.falsePositive = falsePositive
        self.falseNegative = falseNegative

        self.accuracy = (truePositive + trueNegative)/(truePositive + trueNegative + falsePositive + falseNegative)
        self.sensitivity = truePositive/(truePositive + falseNegative)
        self.specificity = trueNegative/(trueNegative + falsePositive)
        self.positivePredictiveValue = (truePositive)/(truePositive  + falsePositive )
        self.negativePredictiveValue = (trueNegative)/(trueNegative  + falseNegative )

        self.overallScore = self.accuracy + self.specificity + self.sensitivity

    def print_score(self):
        print(f"Z => true positive => {self.truePositive}")
        print(f"W => true negative => {self.trueNegative}")
        print(f"X => false positive => {self.falsePositive}")
        print(f"Y => false negative => {self.falseNegative}")
        print(f"Specificity: \t\t\t{self.specificity * 100}")
        print(f"Sensitivity: \t\t\t{self.sensitivity * 100}")      
        print(f"Positive predictive value: \t{self.positivePredictiveValue}")
        print(f"Negative predictive value: \t{self.negativePredictiveValue}")
        print(f"Accuracy: \t\t\t{self.accuracy * 100}")