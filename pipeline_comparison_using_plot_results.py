#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 13:37:57 2019

@author: brianne
"""
import plot_results
import os
import glob
import pandas as pd

# Make an empty dictionary to store each contrasts mean, stdev, max and min
summary_dict = {}
wm_dict = {}

#build image dictionary
cons = ['0003','0005', '0006','0008']
for con in cons:
    # Find the images that have been processed
    imgs = glob.glob('/data/images/exobk/exo20*3*/fp*results*/spmT_'+con+'.nii')

    for img in imgs:
        # Get the end of the filename  so that it can be displayed on the axials as a reference.
        processing = plot_results.SummarizeImage()
        processing.img_info(img,output_dir='/data/analysis/brianne/exobk/single_subjs')

        if not os.path.isfile(os.path.join(processing.out_dir, processing.filename + '.pdf')) and 'exo25' in processing.filename:
            processing.plot_con()

        # To get the means, maxes, etc. the thresholded (eroded), normalized white matter maps will be resliced to the con dimensions
        # Then, fslstats will be run with and without the mask to generate the desired summary measures.
        ans = processing.collect_stats(mask='gm')
        try:
            ans.stdout.decode("utf-8").strip()
            summary_dict[processing.filename] = (ans.stdout.decode("utf-8").strip().split(' ')) # Put the stats in a dictionary for simple, organized transformation to dataframe 
        except AttributeError as e:
            print(e)
            print("Error info: likely didn't have a thresholded mask. Try running preproc_fmri to threshold segmentations.")


# Coregister the wm mask to the functional, so that FSL can use the wm as a mask for the stats
        ans_wm = processing.collect_stats(mask = 'wm')
        try:
            ans_wm.stdout.decode("utf-8").strip()
            wm_dict[processing.filename] = (ans_wm.stdout.decode("utf-8").strip().split(' '))
        except AttributeError as e:
            print(e)
            print("Error info: likely didn't have a thresholded mask. Try running preproc_fmri to threshold segmentations.")

#Multi-level dictionary
#df = pd.DataFrame.from_dict({(i,j):summary_dict[i][j]
#                       for i in summary_dict.keys()
#                       for j in summary_dict[i].keys()}).T

df = pd.DataFrame.from_dict(summary_dict).T
wm_df = pd.DataFrame.from_dict(wm_dict).T
df = df.merge(wm_df, left_index=True, right_index=True)
df.columns = ['gm_mean','gm_stdev','gm_min','gm_max','wm_mean','wm_stdev','wm_min','wm_max']
df['con'] = ['_'.join(x[4:]) for x in df.index.str.split('_')] # Get the end of the file processing.filename
df.index = ['_'.join(x[0:4]) for x in df.index.str.split('_')] # Rename the index to only contain the subject info
print('Saving stats: ',os.path.join(out_dir,'stats.csv'))
df.to_csv(os.path.join(out_dir,'stats.csv'))