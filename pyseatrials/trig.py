# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_trig.ipynb.

# %% auto 0
__all__ = ['opposite_magnitude_fn', 'adjacent_magnitude_fn', 'law_of_cosines']

# %% ../nbs/00_trig.ipynb 4
import numpy as np
import pandas as pd
from fastcore.test import *

# %% ../nbs/00_trig.ipynb 6
def opposite_magnitude_fn(magnitude:float, #The true speed 
                             angle:float, #The angle in radians
                            ):
    "Product of sin and magnitude"
    
    x = magnitude * np.sin(angle)
    
    return x

# %% ../nbs/00_trig.ipynb 9
def adjacent_magnitude_fn(magnitude:float, # The true speed
                             angle:float, # The Ange in radians
                             ):
    
    "Product of cos and magnitude"
    
    x = magnitude * np.cos(angle)
    
    return x

# %% ../nbs/00_trig.ipynb 13
def law_of_cosines(a:float, # side a which is along the x-axis
                   b:float, #side b makes the angle $\theta$ with side a
                   theta:float): #the angle in radians opposite side c
    
    "Finds the length of side c using the angle theta opposite c and the length of the other two sides"
    
    adjacent_component = a - adjacent_magnitude_fn(b, theta)
    opposite_component = - opposite_magnitude_fn(b, theta)
    
    return np.sqrt(adjacent_component**2 + opposite_component**2)
