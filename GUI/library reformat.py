import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Label, Listbox, Button, Scrollbar
import os
import uuid  

class MassSpectraGUI:
    def __init__(self, root):
        self.root = root
        root.title('Mass Spectra Library Importer and Reformatter')
        
        # Log Text Area
        self.log_label = tk.Label(root, text="Log:")
        self.log_label.pack()
        self.log_area = tk.Text(root, height=10, width=50)
        self.log_area.pack(padx=10, pady=5)
        
        # Label for Input Files
        self.input_label = Label(root, text="Input Files:")
        self.input_label.pack()
        
        # Listbox for Displaying Selected Input Files
        self.listbox = Listbox(root, width=50, height=10)
        self.scrollbar = Scrollbar(root, orient="vertical")
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="y", padx=10, pady=5)
        self.scrollbar.pack(side="left", fill="y")
        
        # Output Directory Path Display
        self.output_label = Label(root, text="Output Directory Path:")
        self.output_label.pack()
        self.output_path_display = Entry(root, width=50)
        self.output_path_display.pack(padx=10, pady=5)
        
        # Frame for Buttons
        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)
        
        # Open Files Button
        self.open_files_button = Button(self.frame, text='Open Mass Spectra Files', command=self.open_files)
        self.open_files_button.pack(side=tk.LEFT)
        
        # Select Output Directory Button
        self.save_directory_button = Button(self.frame, text='Select Output Directory', command=self.select_output_directory)
        self.save_directory_button.pack(side=tk.LEFT, padx=10)
        
        # Process and Reformat Files Button
        self.process_files_button = Button(self.frame, text='Process and Reformat Files', command=self.process_files)
        self.process_files_button.pack(side=tk.LEFT, padx=10)
        
        self.filepaths = []
        self.output_directory = ''

    def open_files(self):
        self.filepaths = filedialog.askopenfilenames(
            filetypes=[("Supported Files", "*.mgf;*.msp"), ("All Files", "*.*")]
        )
        self.listbox.delete(0, tk.END)  # Clear current list
        if self.filepaths:
            for filepath in self.filepaths:
                self.listbox.insert(tk.END, filepath)
        else:
            messagebox.showerror("File Selection", "No files were selected.")
    
    def select_output_directory(self):
        self.output_directory = filedialog.askdirectory()
        if self.output_directory:
            self.output_path_display.delete(0, tk.END)
            self.output_path_display.insert(0, self.output_directory)
        else:
            messagebox.showerror("Directory Selection", "No directory was selected.")
            
    def log(self, message):
        self.log_area.config(state='normal')  # Enable text widget to modify it
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state='disabled')  # Disable text widget to prevent user modification
        self.log_area.see(tk.END)  # Auto-scroll to the bottom


    def process_files(self):
        if self.filepaths and self.output_directory:
            topnum = simpledialog.askinteger("Input", "Enter the number of top intensities for reformatting:",
                                             parent=self.root, minvalue=1, maxvalue=100)
            if topnum is not None:
                try:
                    combined_library = LibraryLoadingStrategy.combine_libraries(self.filepaths)
                    reformat = LibraryReformat(topnum)
                    reformatted_library = reformat.reformat_library(combined_library)
                    
                    # Generate a random filename using uuid
                    random_filename = f"reformatted_library_{uuid.uuid4()}.msp"
                    output_file_path = os.path.join(self.output_directory, random_filename)
                    
                    LibrarySaveStrategy.save_library_to_msp_class(reformatted_library, output_file_path)
                    
                    self.log(f"The combined library has been processed and saved successfully as {random_filename}")
                    messagebox.showinfo("Success", f"The combined library has been processed and saved successfully as {random_filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred: {str(e)}")
            else:
                messagebox.showinfo("Cancelled", "Reformatting cancelled.")
        else:
            messagebox.showerror("Error", "Please select one or more input files and an output directory.")
            
if __name__ == '__main__':
    root = tk.Tk()
    gui = MassSpectraGUI(root)
    root.mainloop()
