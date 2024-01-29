from pyteomics import mgf
import os
from pyteomics import mzml



def read_path(dir)-> list:
    return([os.path.join(dir, file) for file in os.listdir(dir)])


def check_inputlibrary_files(dir)-> str:   
    for item in read_path(dir):
        if not item.endswith('.msp'):
            return "currently we support .msp files "        
    return "Combining all libraries"

def library_loading_msp(file_path)-> list:
    
    '''read input library files line by line and export a new list for all spectrum readed from a file_path'''
    
    with open(file_path, 'r', encoding='utf-8') as file:
        spectra = []
        spectrum = {}  # Start with an empty dictionary
        for line in file:
            line = line.strip().lower()  # remove leading and trailing whitespace characters, format uppercase to lowercase
            # Skip empty lines
            if not line:
                continue
                # Check for new spectrum
            if line.startswith('name:'):
                if 'mz' in spectrum:  # Check if the current spectrum already has 'mz' key
                    spectra.append(spectrum)
                    spectrum = {}  # Reset for new spectrum

            if ':' in line:  # Meta data line
                key, value = line.split(':', 1)
                spectrum[key.strip()] = value.strip()
            else:  # Spectrum data line
                mz, intensity = line.split()
                spectrum.setdefault('mz', []).append(float(mz))
                spectrum.setdefault('intensity', []).append(float(intensity))

            # Add the last spectrum if it contains data
        if 'mz' in spectrum:
            spectra.append(spectrum)
            
        return spectra 


def combine_libraries(dir)-> list:
    '''for each specific spectrum in library is a dict, here we combine all spectrums in all input 
    libraries and make a new library'''
    
    new_library = []
    
    for file_path in read_path(dir):
        new_library.extend(library_loading_msp(file_path))
        
    return(new_library)

        
def save_library_to_msp(libraryname, output_file_path):
    '''can save the new made library to a new .msp file'''
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for spectrum in spectra:
            # Write the spectrum header (e.g., 'Name: ...')
            for key, value in spectrum.items():
                if key not in ['mz', 'intensity']:  # Assuming 'mz' and 'intensity' are lists
                    file.write(f"{key.capitalize()}: {value}\n")

            # Write the mz and intensity data
            mz_intensities = zip(spectrum.get('mz', []), spectrum.get('intensity', []))
            for mz, intensity in mz_intensities:
                file.write(f"{mz} {intensity}\n")

            # Write an empty line as a separator between spectra
            file.write("\n")


def reformat_spectrum(spectrum,topnum):
    
    # Check if the length of 'mz' is less than 10
    if len(spectrum['mz']) < 10:
        return spectrum.copy()
     
    # Pair mz and intensity values and sort by intensity in descending order
    paired_sorted = sorted(zip(spectrum['mz'], spectrum['intensity']), key=lambda pair: pair[1], reverse=True)
    
    # Select the top ? pairs
    top_pairs = paired_sorted[:topnum]
    
    # Unzip the pairs back to two lists: top_mz and top_intensity
    top_mz, top_intensity = zip(*top_pairs)
    
    # Create a new dictionary with the top ten mz and intensity pairs, preserving other metadata
    new_spectrum = spectrum.copy()  # Copy the original spectrum dictionary
    new_spectrum['mz'] = list(top_mz)
    new_spectrum['intensity'] = list(top_intensity)
    
    # Optionally, adjust 'num peaks' if you store the number of peaks in the spectrum
    new_spectrum['num peaks'] = str(len(new_spectrum['mz']))
    
    return new_spectrum

def reformat_library(library=test,topnum=10):
    
    '''format raw library into DIMA library dict,
    need to format the library MS2 peaks to a lower number to reduce low intensity matched peaks and improve identification'''

    reformated_library = []
    for spectrum in library:
        if 'precursormz' in spectrum:
            reformated_library.append(reformat_spectrum(spectrum,topnum))
        
    return(reformated_library) 
      
