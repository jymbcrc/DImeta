
import numpy as np
import pandas as pd
import os




def within_tolerance(mz1, mz2, ppm):
    """ Check if mz2 is within the ppm tolerance of mz1. """
    tolerance = mz1 * ppm / 1e6
    return abs(mz1 - mz2) <= tolerance

def match_spectrum(query_spectrum, target_spectrum, ppm_tolerance):
    """
    Match a spectrum to a query spectrum within a given PPM tolerance and return the matched peaks along with their three-dimensional values.
    
    :param query_spectrum: List of (m/z, intensity, value) tuples for the query spectrum.
    :param target_spectrum: List of (m/z, intensity, value) tuples for the target spectrum.
    :param ppm_tolerance: PPM tolerance for matching.
    :return: Matched peaks as a list of tuples (query_mz, query_intensity, query_value, target_mz, target_intensity, target_value).
    """

    def within_tolerance(mz1, mz2, ppm):
        """ Check if mz2 is within the ppm tolerance of mz1. """
        tolerance = mz1 * ppm / 1e6
        return abs(mz1 - mz2) <= tolerance

    matches = []
    for query_mz, query_intensity, query_label in query_spectrum:
        for target_mz, target_intensity, target_label in target_spectrum:
            if within_tolerance(query_mz, target_mz, ppm_tolerance):
                matches.append((query_mz, query_intensity, query_label, target_mz, target_intensity, target_label))
                break  # Assuming only one match per query peak
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

