#!/usr/bin/env python
# coding: utf-8

import sys
import os
import uuid
import matplotlib.pyplot as plt
import os
import glob
import numpy as np
import heapq

from LibraryHandling import LibraryLoadingStrategy, LibraryReformat, LibrarySaveStrategy, read_path
from IdentificationMeta import QueryTargetedSpectrum, match_spectrum, group_tuples_by_same_value, filter_tuples, cosine_similarity, custom_sort, macc_score, normalize_to_100
import pandas as pd 




#result_dict = defaultdict(list)

def get_spectra(analyzer, scan_index, library, PrecursorIonMassTolerance):
    query_spectrum = analyzer.get_query_spectrum(scan_index)
    realtime_library = analyzer.get_realtime_lib(scan_index, library, PrecursorIonMassTolerance)
    target_spectrum = analyzer.get_target_spectrum(scan_index, library, PrecursorIonMassTolerance)
    return query_spectrum, realtime_library, target_spectrum


def match_and_calculate_cosine_similarity(query_spectrum, target_spectrum, ppm_tolerance, minmatchedpeaks):
    matched_peaks = match_spectrum(query_spectrum, target_spectrum, ppm_tolerance)
    cosine_scores = []
    for matched_spectrum in group_tuples_by_same_value(matched_peaks, -1):
        filtered_matches = filter_tuples(matched_spectrum)
        if len(filtered_matches) >= minmatchedpeaks:
            cosine_score = cosine_similarity([t[1] for t in filtered_matches], [t[4] for t in filtered_matches])
            cosine_scores.append((cosine_score, filtered_matches))
    return cosine_scores


def main_processing_function(lowerscan,higherscan, analyzer, library, PrecursorIonMassTolerance, ppm_tolerance, minmatchedpeaks, fig_path):
    result_dict = { 'PrecursorMZ': [],'Compensation Voltage': [], 'Cosine_score': [], 'Ion_count': [], 'Scan': [], 'Compound': [], 'CompoundMZ': [], 'Adduct': [], 'Formula': [], 'Macc_score': [], 'Matched_peaks': [] }
    #result_dict = {}
    for scan_index in range(lowerscan,higherscan):
        query_spectrum, realtime_library, target_spectrum = get_spectra(analyzer, scan_index, library, PrecursorIonMassTolerance)
        cosine_scores = match_and_calculate_cosine_similarity(query_spectrum, target_spectrum, ppm_tolerance, minmatchedpeaks)
        if cosine_scores:
            cos = sorted(cosine_scores, key=lambda x: custom_sort(x), reverse=True)[0]
            number = int(cos[1][0][-1])
            ioncount = round(sum([it[1] for it in cos[1]]), 3)
            try:
                compound_info = realtime_library[number]
            
            except IndexError:
                # If `number` is out of bounds for `realtime_library`
                compound_info = {}
            
            #result_dict, compound_info, number = update_results(cos, scan_index, analyzer, realtime_library, result_dict)
            #compound_info = realtime_library.get(number, {})
            result_dict['PrecursorMZ'].append(str(analyzer.get_precusorMZ(scan_index)))
            result_dict['Cosine_score'].append(cos[0])
            result_dict['Ion_count'].append(ioncount)
            result_dict['Scan'].append(scan_index)
            result_dict['Compound'].append(compound_info.get('name', ''))
            result_dict['CompoundMZ'].append(compound_info.get('precursormz', ''))
            result_dict['Adduct'].append(compound_info.get('precursortype', '').upper())
            result_dict['Formula'].append(compound_info.get('formula', '').upper())
            result_dict['Macc_score'].append(macc_score(len(cos[1]), cos[0]))
            result_dict['Matched_peaks'].append(len(cos[1])) 
            result_dict['Compensation Voltage'].append(str(analyzer.get_compensation_voltage(scan_index))) 
            
            #generate_plot(query_spectrum, realtime_library[number], compound_info, cos, scan_index, fig_path)
    return result_dict


def generate_plot(query_spectrum, realtime_library, compound_info, cos, scan_index, fig_path):
    plt.vlines(realtime_library['mz'], [0], normalize_to_100(realtime_library['intensity']), colors="red", label='lib')
    plt.vlines([x[0] for x in query_spectrum], [0], [-item for item in normalize_to_100([x[1] for x in query_spectrum])], colors="blue",label='real')
    plt.legend()
    plt.title(f"{compound_info['name']} cos{cos[0]} scan: {scan_index}")
    plt.savefig(os.path.join(fig_path, f"{scan_index}.png"), dpi=300, bbox_inches='tight')
    plt.show()
    plt.clf()

    
def save_results(result_dict, fig_path, mzml_file_path):
    
    df = pd.DataFrame(result_dict)
    df.to_excel(os.path.join(fig_path, f"{mzml_file_path.split('/')[-1].split('.')[0]}.xlsx"), index=False)







