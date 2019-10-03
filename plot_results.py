#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 16:28:25 2019

@author: brianne
"""
import sys
rv = (3,7)
if not sys.version_info[0] >= rv[0] and sys.version.info[1] >= rv[1]:
    raise Exception("Must be using at least Python 3.7")
    
study = 'priming'

import matplotlib.pyplot as plt
import glob
import os
import subprocess
from nilearn.plotting import plot_stat_map
import nipype.interfaces.spm.utils as spmu
import file_gui # Local script calling Tkinter


mask_dict = {'mwc2' : ['white matter','wm'], 'mwc1' : ['gray matter','gm']}  
        
class SummarizeImage:
    def __init__(self):
        pass

    def img_info(self, img, output_dir=None):
        self.img = img
        self.filename  = '_'.join(self.img.split('.')[0].split('/')[-3:])
        self.subj_dir = os.path.dirname(self.img) # Overall directory for organizing the subject's files
        self.fsl_file = os.path.join(self.subj_dir, 'fsl_' + self.filename) # New self.filename  , so that SPM second-cons don't get confused with the zeroes outside the brain, instead of NaNs
        if not output_dir:
            output_dir = file_gui().find_dir('destination')
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        self.out_dir = output_dir
        self.summary_dict={}
        self.wm_dict={}
    
    def reslice_mask(self, segmentation, target=None):
        for k,v in mask_dict.items():
            if segmentation in v:
                print('Reslicing eroded {} mask'.format(v[0]))
                thresh_map = glob.glob(os.path.join('/'.join(self.img.split('/')[:5]),'t1', ('thresh_'+k+'*'+self.img.split('/')[4].split('_')[0] + '*t1*')))

        # Do the reslicing
        coreg = spmu.Reslice()
        coreg.inputs.space_defining = self.fsl_file +'.nii.gz' # target
        try:
            coreg.inputs.in_file = thresh_map[0]
        except IndexError:
            print('Threshrolded image not available.')
            return
        coreg.run() # Throwing error, b/c mimicking bash?


    def plot_con(self):
        #Time intensive step of plotting the axial mosaic, if it has not already been plotted
        print('Plotting ' + self.filename  )
        plot_stat_map(self.img, title=self.filename  , cut_coords=[-30, -15, -7, 2, 10, 25, 35, 45], display_mode='z', draw_cross=False, colorbar=True, black_bg=True, threshold=2.3)
        plt.savefig(os.path.join(self.out_dir, self.filename   + '.pdf'),facecolor='k',edgecolor='k', str='pdf')
        plt.close()

    def collect_stats(self,**kwargs):
        print('Collecting stats: ' + self.filename)

        if not os.path.isfile(self.fsl_file):
            subprocess.run(['fslmaths', self.img, '-nan', self.fsl_file]) # Converting NaN's to zeroes

        if 'mask' in kwargs:
            mask = kwargs['mask']
            for k,v in mask_dict.items():
                if mask in v:
                    mask_file = glob.glob(os.path.join('/'.join(self.img.split('/')[:5]),'t1', ('rthresh_'+ k + '*' + self.img.split('/')[4].split('_')[0] + '*t1*')))

                    if not mask_file:
                        self.reslice_mask(mask)
                        mask_file = glob.glob(os.path.join('/'.join(self.img.split('/')[:5]),'t1', ('rthresh_'+k+'*'+self.img.split('/')[4].split('_')[0] + '*t1*')))

            # Apply the wm mask to the same data as before to test whether there is signal
            if mask_file:
                ans = subprocess.run(["fslstats", self.fsl_file, "-k", mask_file[0], "-M", "-S", "-R"], capture_output=True)  # Note that the mask must be input before the stats measures or it is discounted.
            else:
                print('Mask file was unsuccessfully created. Check that there is a base, thresholded image.')
                return
        else:
            ans = subprocess.run(["fslstats", self.fsl_file, "-M", "-S", "-R"], capture_output=True) # Collect the stats
        return ans
    
    def plot_stats(self):
        if not os.path.isfile(os.path.join(self.out_dir, self.filename + '.pdf')):
            self.plot_con()
            
    def get_roi_stats(self, rois):
        # To get the means, maxes, etc. the thresholded (eroded), normalized white matter maps will be resliced to the con dimensions
        if not self.summary_dict:
            self.summary_dict = {}
            
        for roi in rois:
            # Then, fslstats will be run with and without the mask to generate the desired summary measures.
            ans = self.collect_stats(mask=roi)
            try:
                ans.stdout.decode("utf-8").strip()
                self.summary_dict[self.filename] = (ans.stdout.decode("utf-8").strip().split(' ')) # Put the stats in a dictionary for simple, organized transformation to dataframe 
            except AttributeError as e:
                print(e)
                print("Error info: likely didn't have a thresholded mask. Try running preproc_fmri to threshold segmentations.")
    
    
    def build_stat_table(self):
        import pandas as pd
        df = pd.DataFrame.from_dict(self.summary_dict).T
        wm_df = pd.DataFrame.from_dict(self.wm_dict).T
        df = df.merge(wm_df, left_index=True, right_index=True)
        df.columns = ['gm_mean','gm_stdev','gm_min','gm_max','wm_mean','wm_stdev','wm_min','wm_max']
        df['con'] = ['_'.join(x[4:]) for x in df.index.str.split('_')] # Get the end of the file self.filename
        df.index = ['_'.join(x[0:4]) for x in df.index.str.split('_')] # Rename the index to only contain the subject info
        print('Saving stats: ',os.path.join(self.out_dir,'stats.csv'))
        df.to_csv(os.path.join(self.out_dir,'stats.csv'))#build image dictionary

if study == 'exobk':
    first_level_cons = ['0003','0005','0006','0008']
    cons = ['0001','0002','009','010','011','012']
    fs=['007','008','009','010','013','014']
    cons = ['09','010','015','016']
    fs=['11','12','13']
    output_dir = '/Volumes/bk/data/analysis/brianne/exobk/fp'
elif study == 'priming':
    first_level_cons = ['0001', '0003', '0004','0005','0008']
    ts = ['0001','0004', '0009','0011']
    #fs=['007','008','009','010','013','014']
    output_dir='/Volumes/bk/data/analysis/brianne/priming/food_pics'
    
for first_level in first_level_cons:
    imgs = []
    try:
        for t in ts:
            imgs = imgs + glob.glob(os.path.join(output_dir,'*', '*'+first_level+'*','*spmT*'+t+'.nii'), recursive=True)
    except NameError:
         print('No T contrasts defined.')            

    try:
        for f in fs:
            imgs = imgs + glob.glob(os.path.join(output_dir,'*', '*'+first_level+'*','*spmT*'+t+'.nii'), recursive=True)  
     #       imgs = imgs + glob.glob('/data/analysis/brianne/exobk/fp/con'+first_level+'/*/*spm?_0'+con+'.nii')
    except NameError:
         print('No F contrasts defined.')

    for img in imgs:
        processing = SummarizeImage()
        processing.img_info(img,output_dir=output_dir)

        if not os.path.isfile(os.path.join(processing.out_dir, processing.filename + '.pdf')):
            processing.plot_con()
    