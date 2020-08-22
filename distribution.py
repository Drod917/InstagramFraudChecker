# %%
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

class Distribution():
    x = np.arange(1,10,1) 

    def __init__(self, filename=""):
        self.filename = filename

    def get_distribution(self):
            df = pd.read_csv(self.filename)
            y_1 = []
            y_2 = []
            for val in df['followers']:
                y_1.append(val)
            for val in df['following']:
                y_2.append(val)
            # Get the least significant digit of each value
            least_significant_digit = lambda x : x // np.power(10, int(np.log10(x)))
            for y in range(y_1.__len__()):
                y_1[y] = least_significant_digit(y_1[y])
            for y in range(y_2.__len__()):
                y_2[y] = least_significant_digit(y_2[y])
            # Create frequency distribution of each follow set
            distribution_1 = np.zeros(10)
            distribution_2 = np.zeros(10)
            for y in y_1:
                distribution_1[int(y) - 1] += 1
            for y in y_2:
                distribution_2[int(y) - 1] += 1
            self.follower_dist = distribution_1[:9]
            self.following_dist = distribution_2[:9]
            plt.plot(self.x, self.follower_dist)
            plt.show()
            plt.plot(self.x, self.following_dist)
            plt.show()
        
    
# %%
