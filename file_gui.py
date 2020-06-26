#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 11:43:47 2019

@author: brianne
"""

from tkinter import filedialog
from tkinter import *
import pathlib
import glob

def get_img_files():
    proj_dir = file_gui().find_dir('project')
    tmp = file_gui().find_files(msg = 'Select contrasts of interest')
    cons = []
    for t in tmp:
        cons.append(t.split('_')[-2:])
        
    paradigm = tmp[0].split('/')[-2]
    imgs = []
    for con in cons:
        imgs.append(glob.glob(os.path.join(self.proj_dir,'*', self.paradigm, '*'+con+'*' )))
    return paradigm, cons, imgs, proj_dir 
        
class file_gui:
    """Locate files to pass on using a GUI"""
    root=Tk()
    
    def __init__(self, init_dir=pathlib.Path.cwd()):
        self.init_dir = init_dir
        
    def find_files(self, msg=None):
        if not msg:
            msg ="Select file"
        filenames =  filedialog.askopenfilenames(initialdir = self.init_dir,title = msg,                                               filetypes = (("nifti files","*.nii*"),("mat files", "*.mat"),("all files","*.*")))
        self.filenames = list(file_gui.root.tk.splitlist(filenames))
        file_gui.root.destroy()
        return (self.filenames)
    
    def find_dir(self, dir_type):
        heading = ('Select {} folder'.format(dir_type))
        self.main_dir = filedialog.askdirectory(initialdir=self.init_dir, title=heading )

if __name__ == "__main__":
    test = file_gui()
    print("Checking files in : {}".format(test.init_dir))
    test.find_files()
    test.root.mainloop()   
    print("Found: {}".format(test.filenames))