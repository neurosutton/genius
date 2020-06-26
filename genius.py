#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 10:48:28 2017

@author: mohlb
General(ge) neuroimaging (ni) utilities (u) suite (s)


(1) get_remote_files(ip,filepath) will find the files that you are trying to pull into an analysis
"""

from tkinter import filedialog
from tkinter import *

import pathlib
import os
import subprocess

class file_gui:
    """Locate files to pass on using a GUI"""
    root=Tk()
    root.withdraw()

    def __init__(self, init_dir=pathlib.Path.cwd()):
        self.init_dir = init_dir
        self.filenames = []

    def find_dirs(self):
        self.dirnames.append(filedialog.askopendirectories)

    def find_files(self, msg=None):
        if not msg:
            msg = 'Select file'
        filenames = []
        filenames.extend(filedialog.askopenfilenames(initialdir = self.init_dir,title = msg,                                               filetypes = (("nifti files","*.nii*"),("mat files", "*.mat"),("json", "*.json"),("all files","*.*"))))
        self.filenames = filenames # [x for x in file_gui.root.tk.splitlist(filenames)]
        file_gui.root.destroy()
        return (self.filenames)

class define_dir_structure():
    """Build the pieces of the filepath that can be used for templating directories and analysis files."""
    def __init__(self, files = None):
        self.filenames = []
        self.anat_dir=[]
        self.func_dir=[]

    def get_subj_dirs(self):
        pass
    
    def get_subj_files(self,files=None):
        if files:
            self.filenames = files
        else:
            tmp = file_gui()
            self.filenames = tmp.find_files() # run through the method to get files from the GUI, if the list isn't provided.

        if len(self.filenames)>1:
        # Compare the first and last in a file to build the common project-level folder
            self.home_dir = os.path.commonprefix(self.filenames[0],self.filenames[-1]) # full path to proj_dir
            self.proj_dir = os.path.basename(self.home_dir)  # name of the project in path
            self.scan_types = []
            self.subj_list = []
            for subj_file in self.filenames:
                subj = os.path.relpath(self.home_dir, subj_file).split('/')[0]
                self.subj_list.append(subj) # Because subj_list will be long, use unique later
                scan = os.path.basename(os.path.dirname(subj_file))
                if scan not in self.scan_types:
                    # Because scan_types will be a short list, use the conditional
                    self.scan_types.append(scan)
            self.subj_list = unique(self.subj_list)
        else:
             # Reverse the logic a bit, because there is no comparison.
            subj_file = os.path.dirname(self.filenames[0])
            self.scan_types = [os.path.basename(subj_file)]
            subjListIx = subj_file.split('/').index(self.scan_types[0]) # Since there is only one file and therefore, one scan type, bring the item out of the list for indexing
            self.subj_dir = os.path.join(os.sep,*subj_file.split('/')[:subjListIx])
            self.subj_list = subj_file.split('/')[subjListIx-1]
            self.home_dir = os.path.dirname(self.subj_dir)
            self.proj_dir = os.path.basename(self.home_dir)  # singular name of the project in the paths

        for scan_type in self.scan_types:
            # For the few possible names of the scans, find one example in the list of files and then categorize as anat or func.
            scan_example = next(x for x in self.filenames if scan_type in x)
            if scan_example is None:
                scan_example = self.filenames[0]

            script = "fslinfo " + scan_example + " | grep ^dim4 | awk '{print $2}'"

            # Get fslinfo about the example, look for the time dimension and grab the value
            vols = subprocess.run([script], shell=True, stdout=subprocess.PIPE) # Couldn't find a way around shell=True
            vols = int(vols.stdout.decode('ascii').strip())

            if vols > 1:
                print('Found {} volumes.'.format(vols))
                self.func_dir = os.path.basename(os.path.dirname(scan_example))
            else:
                self.anat_dir = os.path.basename(os.path.dirname(scan_example))


if __name__ == "__main__":
    test = file_gui()
    print("Checking files in : {}".format(test.init_dir))
    test.find_files()
    #test.root.mainloop()
    print("Passing {} to next test".format(*test.filenames))
    test1 = define_dir_structure()
    test1.get_subj_files(files=test.filenames)
    print("Found: {} for anatomical\n{} for functional\n{}".format(test1.filenames, test1.anat_dir, test1.func_dir))
