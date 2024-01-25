from pyteomics import mgf


def library_loading(file_path):
    '''loading different library format '''   
    if file_path.endswith(".mgf"):
        spectra_library = library_loading_mgf(file_path)
    elif file_path.endswith(".msp"):
        spectra_library = library_loading_msp(file_path)
    else:
        print("Library format not supported")
    return(spectra_library)

def library_loading_mgf(file_path):
    spectra_library = mgf.IndexedMGF(file_path, index_by_scans=True)
    return spectra_library
    
def library_loading_msp(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        spectra = []
        spectrum = {}  # Start with an empty dictionary
        for line in file:
            line = line.strip() # remove leading and trailing whitespace characters 
            # Skip empty lines
            if not line:
                continue
            # Check for new spectrum
            if line.startswith('Name:'):
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
