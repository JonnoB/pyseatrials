# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_wind_resistance_coef.ipynb.

# %% auto 0
__all__ = ['load_wind_coefficients', 'interpolate_cx', 'fujiwara']

# %% ../nbs/05_wind_resistance_coef.ipynb 2
import numpy as np
import pandas as pd
from fastcore.test import *
import pkgutil
from io import BytesIO

# %% ../nbs/05_wind_resistance_coef.ipynb 5
def load_wind_coefficients(vessel_type:str #The name of the vessel type. Must be one of 9 options
                     ): #returns a data set with where the first column us angle_of_attack in radians, the second is angle_of_attack in degrees, the subsequent columns names ship states
        
        "Load a wind coefficient table for a generic ship class. Datasets from ITTC"
        
        #This needs to be adapted so that the paths work on any system, using pathlib.path would be a better choice
        res = pkgutil.get_data('pyseatrials', 'wind_coef_data/'+vessel_type+'.csv')
        
        return pd.read_csv(BytesIO(res))
    

# %% ../nbs/05_wind_resistance_coef.ipynb 9
def interpolate_cx(df, #dataframe of the wind resistance dataset
                   relative_wind_direction:float, #The angle of the wind relative to the ship [rads]
                   ship_state:str #The state of the ship the resistance should be evaluated in. Chosen from the columns of the wind resistance datasets
)->float: # The dimensionless wind resistance coefficient
    
    "Find a linearly interpolated value for wind resistance coefficient"
    
    return np.interp(relative_wind_direction, df.angle_of_attack, df[ship_state])

# %% ../nbs/05_wind_resistance_coef.ipynb 26
def _clf(aod:float, #is the lateral projected area of superstructures on deck [m2]
        axv:float, #is the area of maximum transverse section exposed to the winds [m2]
        alv:float, #is the projected lateral area above the waterline [m2]
        cmc:float, #is the horizontal distance from midship section to centre of lateral projected area ALV, this is often negative. [m2]
        hc:float, #is the height from the waterline to the centre of lateral projected area ALV [m]
        loa:float, #is the length overall [m]
        b:float, #is the ship breadth [m]
        wind_dir:float #is the relative wind direction, 0 means head winds. [deg]
        ) -> float: #returns the internal value clf [-]
    
    beta = {'10': 0.922,
                '11': -0.507,
                '12': -1.162,
                '20': -0.018,
                '21': 5.091,
                '22': -10.367,
                '23': 3.011,
                '24': 0.341
                }
    #formula is valid for angles between 0 and 180deg (assume symmetry).
    if 180<wind_dir<=360:
            wind_dir = 360-wind_dir
            
    wind_dir_rad = np.deg2rad(wind_dir)
    #apply fuji formula for lower interpolation value
    clf = (((beta['10'] + beta['11'] * alv / (loa * b) + beta['12'] * cmc / loa) * (0 <= wind_dir_rad < np.deg2rad(90))) + #for wind between 0 and 90
           ((beta['20'] + beta['21'] * b / loa + beta['22'] * hc / loa + beta['23'] * (aod / loa **2) + beta['24'] * (axv / b **2)) * (np.deg2rad(90) < wind_dir_rad <= np.deg2rad(180)))) #for wind between 0 and 90

    return clf

def _cxli(axv:float, #is the area of maximum transverse section exposed to the winds [m2]
         alv:float, #is the projected lateral area above the waterline [m2]
         hbr:float, #is the height of top of superstructure (bridge etc) [m]
         loa:float, #is the length overall [m]
         b:float, #is the ship breadth [m]
         wind_dir:float #is the relative wind direction, 0 means head winds. [deg]
         ) -> float: #returns the internal value cxli [-]
    
    gamma = {'10': -0.458,
            '11': -3.245,
            '12': 2.313,
            '20': 1.901,
            '21': -12.727,
            '22': -24.407,
            '23': 40.310,
            '24': 5.481
            }
    #formula is valid for angles between 0 and 180deg (assume symmetry).
    if 180<wind_dir<=360:
            wind_dir = 360-wind_dir
            
    wind_dir_rad = np.deg2rad(wind_dir)
    cxli = (((gamma['10'] + gamma['11'] * alv / (loa * hbr) + gamma['12'] * axv / (b * hbr)) * (0 <= wind_dir_rad < np.deg2rad(90))) + #for wind between 0 and 90
            ((gamma['20'] + gamma['21'] * alv / (loa * hbr) + gamma['22'] * axv / alv + gamma['23'] * b / loa + gamma['24'] * axv / (b * hbr)) * (np.deg2rad(90) < wind_dir_rad <= np.deg2rad(180)))) #for wind between 0 and 90
    
    return cxli

def _calf(aod:float, #is the lateral projected area of superstructures on deck in [m2]
         alv:float, #is the projected lateral area above the waterline [m2]
         loa:float, #is the length overall [m]
         b:float, #is the ship breadth [m]
         wind_dir:float #is the relative wind direction, 0 means head winds. [deg]
         ) -> float: #returns the internal value calf [-]
    
    epsilon = {'10': 0.585,
               '11': 0.906,
               '12': -3.239,
               '20': 0.314,
               '21': 1.117
               }
    #formula is valid for angles between 0 and 180deg (assume symmetry).
    if 180<wind_dir<=360:
            wind_dir = 360-wind_dir
            
    wind_dir_rad = np.deg2rad(wind_dir)
    calf = (((epsilon['10'] + epsilon['11'] * aod / alv + epsilon['12'] * b / loa) * (0 <= wind_dir_rad < np.deg2rad(90))) + #for wind between 0 and 90
            ((epsilon['20'] + epsilon['21'] * aod / alv) * (np.deg2rad(90) < wind_dir_rad <= np.deg2rad(180)))) #for wind between 0 and 90
    
    return calf

def _caa(clf:float, #internal value clf [-]
         cxli:float, #internal value cxli [-]
         calf:float, #internal value calf [-]
         wind_dir:float #is the relative wind direction, 0 means head winds. [deg]
         ) -> float:  #returns the internal value caa [-]
    #formula is valid for angles between 0 and 180deg (assume symmetry).
    if 180<wind_dir<=360:
            wind_dir = 360-wind_dir
            
    wind_dir_rad = np.deg2rad(wind_dir)
    
    caa = (clf * np.cos(wind_dir_rad) + 
            cxli * (np.sin(wind_dir_rad) - 0.5 * np.sin(wind_dir_rad) * np.cos(wind_dir_rad) * np.cos(wind_dir_rad)) * np.sin(wind_dir_rad) * np.cos(wind_dir_rad) +
            calf * np.sin(wind_dir_rad) * np.cos(wind_dir_rad) * np.cos(wind_dir_rad) * np.cos(wind_dir_rad)) * -1
    return caa

def _fujiwara_internal(aod:float, #is the lateral projected area of superstructures on deck [m2]
                       axv:float, #is the area of maximum transverse section exposed to the winds [m2]
                       alv:float, #is the projected lateral area above the waterline [m2]
                       cmc:float, #is the horizontal distance from midship section to centre of lateral projected area ALV, this is often negative. [m2]
                       hc:float, #is the height from the waterline to the centre of lateral projected area ALV [m]
                       hbr:float, #is the height of top of superstructure (bridge etc) [m]
                       loa:float, #is the length overall [m]
                       b:float, #is the ship breadth [m]
                       wind_dir:float, #is the relative wind direction, 0 means head winds. [deg]
                       smoothing:float #is the smoothing range, normally 10 degrees. [deg]
                       ) -> float: #returns the wind coefficient in the longitudinal direction [-]
    
    """
    find if the wind angle is in the banned region (90+- smoothing and 270+- smoothing)
    if it is we need to linear interpolate over the banned range
    """
    #create two points either side of banned range (if angle is in range)
    interp_trigger = False
    if (90 - smoothing) <= wind_dir <= (90 + smoothing):
        interp_trigger = True #trigger to interpolate later on
        wind_range_min = 90 - smoothing
        wind_range_max = 90 + smoothing
        interp_range = np.array([wind_range_min, wind_range_max])
    elif (270 - smoothing) <= wind_dir <= (270 + smoothing):
        interp_trigger = True
        wind_range_min = 270 - smoothing
        wind_range_max = 270 + smoothing
        interp_range = np.array([wind_range_min, wind_range_max])
    else:
        pass
        
    #if triggered, evaluate the formula at the angle above and below banned range
    if interp_trigger:
        clf_vals = [_clf(aod = aod, axv = axv, alv = alv, cmc = cmc, hc = hc, loa = loa, b = b, wind_dir = i) for i in interp_range]

        cxli_vals = [_cxli(axv = axv, alv = alv, loa = loa, hbr = hbr, b = b, wind_dir = i) for i in interp_range]

        calf_vals = [_calf(aod = aod, alv = alv, loa = loa, b = b, wind_dir = i) for i in interp_range]

        caa_vals = [_caa(clf = i, cxli = j, calf = k, wind_dir = l) for i, j, k, l in zip(clf_vals, cxli_vals, calf_vals, interp_range)]
        caa_vals = np.array(caa_vals)
        
        #interpolate to the requested wind angle
        ca = np.interp(wind_dir, interp_range, caa_vals)

    #else just evaluate the formula, no dramas :)
    else:
        clf_vals = _clf(aod = aod, axv = axv, alv = alv, cmc = cmc, hc = hc, loa = loa, b = b, wind_dir = wind_dir)

        cxli_vals = _cxli(axv = axv, alv = alv, loa = loa, hbr = hbr, b = b, wind_dir = wind_dir)

        calf_vals = _calf(aod = aod, alv = alv, loa = loa, b = b, wind_dir = wind_dir)

        #calculate formula
        ca = _caa(clf = clf_vals, cxli = cxli_vals, calf = calf_vals, wind_dir = wind_dir)
        
    return ca

def fujiwara(aod:float, #is the lateral projected area of superstructures on deck [m2]
             axv:float, #is the area of maximum transverse section exposed to the winds [m2]
             alv:float, #is the projected lateral area above the waterline [m2]
             cmc:float, #is the horizontal distance from midship section to centre of lateral projected area ALV, this is often negative. [m2]
             hc:float, #is the height from the waterline to the centre of lateral projected area ALV [m]
             hbr:float, #is the height of top of superstructure (bridge etc) [m]
             loa:float, #is the length overall [m]
             b:float, #is the ship breadth [m]
             wind_dir:float, #is the relative wind direction, 0 means head winds. [deg]
             smoothing:float = 10 #is the smoothing range, normally 10 degrees. [deg]
             ) -> float: #returns the wind coefficient in the longitudinal direction [-]
    
    #wrap 'fujiwara_internal' to accept arrays and vectorise the calculation
    
    return np.vectorize(_fujiwara_internal)(aod=aod, axv=axv, alv=alv, cmc=cmc, hc=hc, hbr=hbr, loa=loa, b=b, wind_dir=wind_dir, smoothing=smoothing)

