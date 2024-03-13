#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
import os
import uuid
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTextEdit, QListWidget, QLineEdit, QFileDialog, QMessageBox,
                             QInputDialog)
from PyQt5.QtCore import Qt
from LibraryHandling import LibraryLoadingStrategy, LibraryReformat, LibrarySaveStrategy


# In[ ]:




class MassSpectraGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Mass Spectra Library Importer and Reformatter')
        self.setGeometry(100, 100, 640, 480)
        
        layout = QVBoxLayout()
        
        # Log Area
        self.log_label = QLabel("Log:")
        layout.addWidget(self.log_label)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        # Input Files Label and List
        self.input_label = QLabel("Input Files:")
        layout.addWidget(self.input_label)
        self.listWidget = QListWidget()
        layout.addWidget(self.listWidget)
        
        # Output Directory
        self.output_label = QLabel("Output Directory Path:")
        layout.addWidget(self.output_label)
        self.output_path_display = QLineEdit()
        layout.addWidget(self.output_path_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.open_files_button = QPushButton('Open Mass Spectra Files')
        self.open_files_button.clicked.connect(self.open_files)
        button_layout.addWidget(self.open_files_button)
        
        self.save_directory_button = QPushButton('Select Output Directory')
        self.save_directory_button.clicked.connect(self.select_output_directory)
        button_layout.addWidget(self.save_directory_button)
        
        self.process_files_button = QPushButton('Process and Reformat Files')
        self.process_files_button.clicked.connect(self.process_files)
        button_layout.addWidget(self.process_files_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.filepaths = []
        self.output_directory = ''
        
    def open_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Open Mass Spectra Files", "",
                                                "Supported Files (*.mgf *.msp);;All Files (*)", options=options)
        if files:
            self.filepaths = files
            self.listWidget.clear()
            self.listWidget.addItems(files)
        else:
            QMessageBox.warning(self, "File Selection", "No files were selected.")
            
    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_directory = directory
            self.output_path_display.setText(directory)
        else:
            QMessageBox.warning(self, "Directory Selection", "No directory was selected.")
    
    def log(self, message):
        self.log_area.append(message)
    
    def process_files(self):
        if self.filepaths and self.output_directory:
            topnum, ok = QInputDialog.getInt(self, "Input", "Enter the number of top intensities for reformatting:",
                                             min=1, max=20)
            if topnum is not None:
                try:
                    combined_library = LibraryLoadingStrategy.combine_libraries(self.filepaths)
                    reformat = LibraryReformat(topnum)
                    reformatted_library = reformat.reformat_library(combined_library)
                    
                    # Generate a random filename using uuid
                    random_filename = f"reformatted_library_{uuid.uuid4()}.msp"
                    output_file_path = os.path.join(self.output_directory, random_filename)
                    LibrarySaveStrategy.save_library_to_msp_class(reformatted_library, output_file_path)
                    
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            else:
                QMessageBox.information(self, "Cancelled", "Reformatting cancelled.")
        else:
            QMessageBox.warning(self, "Error", "Please select one or more input files and an output directory.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MassSpectraGUI()
    ex.show()
    sys.exit(app.exec_())


# In[ ]:




