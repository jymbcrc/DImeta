
import numpy as np
import pandas as pd
import os
import pyteomics


def within_tolerance_ppm(mz1, mz2, ppm):
    """ Check if mz2 is within the "ppm" tolerance of mz1. """
    tolerance = mz1 * ppm / 1e6
    return abs(mz1 - mz2) <= tolerance

def within_tolerance_da(mz1, mz2, da):
    """ Check if mz2 is within the "Da" tolerance of mz1. """
    tolerance = da
    return abs(mz1 - mz2) <= tolerance


def match_spectrum(query_spectrum, target_spectrum, ppm_tolerance):
    """
    Match a spectrum to a query spectrum within a given PPM tolerance and return the matched peaks along with their three-dimensional values.
    
    :param query_spectrum: List of (m/z, intensity, value) tuples for the query spectrum.
    :param target_spectrum: List of (m/z, intensity, value) tuples for the target spectrum.
    :param ppm_tolerance: PPM tolerance for matching.
    :return: Matched peaks as a list of tuples (query_mz, query_intensity, query_value, target_mz, target_intensity, target_value).
    """

    matches = []
    for query_mz, query_intensity, query_label in query_spectrum:
        for target_mz, target_intensity, target_label in target_spectrum:
            if within_tolerance_ppm(query_mz, target_mz, ppm_tolerance):
                matches.append((query_mz, query_intensity, query_label, target_mz, target_intensity, target_label))
                break  # Assuming only one match per query peak
            #if within_tolerance_da(query_mz, target_mz, da):
                #matches.append((query_mz, query_intensity, query_label, target_mz, target_intensity, target_label)) 
    return matches

def cosine_similarity(vector1, vector2):
    """
    Calculate the cosine similarity between two vectors.
    
    Args:
    vector1 (np.array): First vector.
    vector2 (np.array): Second vector.
    
    Returns:
    float: Cosine similarity between vector1 and vector2.
    """
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    similarity = dot_product / (norm_vector1 * norm_vector2)
    return similarity
 
def group_tuples_by_same_value(tuples_list,same_value_position):
    """
    Groups tuples in the provided list by their last value.

    :param tuples_list: List of tuples.
    :return: List of lists, where each sublist contains tuples with the same last value.
    """
    grouped_tuples = {}
    for t in tuples_list:
        key = t[same_value_position]  # Last element of the tuple
        grouped_tuples.setdefault(key, []).append(t)

    return list(grouped_tuples.values())

def normalize_to_0_100(lst):
    min_val = min(lst)
    max_val = max(lst)
    # Avoid division by zero in case all values are the same
    if min_val == max_val:
        return [100 if x == max_val else 0 for x in lst]
    return [100 * (x - min_val) / (max_val - min_val) for x in lst]

def get_query_spectrum(scan) -> list:
    
    tmp=pyteomics.mzml.read(input_filepath[2], use_index=True)
    
    ms_level = tmp.get_by_index(scan)['ms level']
    
    mzs, intens,label = [],[],[]
    
    if ms_level == 2: # check if it is a MS2 spectrum     
    #label=[str(tmp.get_by_index(scan)['precursorList']['precursor'][0]['isolationWindow']['isolation window target m/z'])]*len(tmp.get_by_index(scan)['m/z array'])
        mz = tmp.get_by_index(scan)['m/z array']
        inten = tmp.get_by_index(scan)['intensity array']
        filter_mz_inten = [(x, y) for x, y in zip(mz, inten) if y > 4000]  # filter the mass spectrum by peak intensity > 5000
        if filter_mz_inten:  # check if the list is not empty
            mzs, intens = zip(*filter_mz_inten)
        
        else:
            mzs, intens = [],[]
        
        label=[str(scan)]*len(mzs)
    
    else:
        label = []

    return(list(zip(mzs,intens,label)))


def get_realtime_lib(scan, library) -> list:
    
    tmp=pyteomics.mzml.read(input_filepath[2], use_index=True)
    
    ms_level = tmp.get_by_index(scan)['ms level']
    
    realtime_lib=[]
    if ms_level == 2:
        
        precusor=float(tmp.get_by_index(scan)['precursorList']['precursor'][0]['isolationWindow']['isolation window target m/z'])
        
        realtime_lib = [item for item in library if (precusor - 0.1< float(item['precursormz']) < precusor + 0.1)]

    return(realtime_lib)


def get_target_spectrum(scan,library)-> list:
    
    real = get_realtime_lib(scan, library)

    target_spectrum = []
    
    for i in range(len(real)):
        
        target_spectrum.extend(list(zip(real[i]['mz'],real[i]['intensity'],[str(i)]*len(real))))
        
    return(target_spectrum)
       




class Query_Targeted_Spectrum:
    
    def __init__(self, mzml_filepath):
        self.mzml_filepath = mzml_filepath
        self.tmp = pyteomics.mzml.read(mzml_filepath, use_index=True)

    def get_query_spectrum(self, scan) -> list:
        ms_level = self.tmp.get_by_index(scan)['ms level']
        mzs, intens, label = [], [], []

        if ms_level == 2:
            mz = self.tmp.get_by_index(scan)['m/z array']
            inten = self.tmp.get_by_index(scan)['intensity array']
            filter_mz_inten = [(x, y) for x, y in zip(mz, inten) if y > 4000]
            if filter_mz_inten:
                mzs, intens = zip(*filter_mz_inten)
            else:
                mzs, intens = [], []
            label = [str(scan)] * len(mzs)
        else:
            label = []

        return list(zip(mzs, intens, label))

    def get_realtime_lib(self, scan, library) -> list:
        
        ms_level = self.tmp.get_by_index(scan)['ms level']
        
        realtime_lib = []
        
        if ms_level == 2:
            precursor = float(self.tmp.get_by_index(scan)['precursorList']['precursor'][0]['isolationWindow']['isolation window target m/z'])
            realtime_lib = [item for item in library if (precursor - 0.1 < float(item['precursormz']) < precursor + 0.1)]
        
        return realtime_lib

    def get_target_spectrum(self, scan, library) -> list:
        
        real = self.get_realtime_lib(scan, library)
        
        target_spectrum = []
        
        for i in range(len(real)):
            target_spectrum.extend(list(zip(real[i]['mz'], real[i]['intensity'], [str(i)] * len(real[i]['mz']))))
        
        return target_spectrum

