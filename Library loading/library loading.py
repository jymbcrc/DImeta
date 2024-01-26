from pyteomics import mgf

class LibraryLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.spectra_library = None

    def load_library(self):
        if self.file_path.endswith(".mgf"):
            self.spectra_library = self._load_mgf()
        elif self.file_path.endswith(".msp"):
            self.spectra_library = self._load_msp()
        else:
            print("Library format not supported")
        return self.spectra_library

    def _load_mgf(self):
        # Assuming mgf.IndexedMGF is a class from an external library
        spectra_library = mgf.IndexedMGF(self.file_path, index_by_scans=True)
        return spectra_library

    def _load_msp(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            spectra = []
            spectrum = {}  # Start with an empty dictionary
            for line in file:
                line = line.strip()  # remove leading and trailing whitespace characters
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


