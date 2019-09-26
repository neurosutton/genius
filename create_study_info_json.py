#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 09:07:30 2019
The inputs for second-level looping are described by a json file. Below are the basic input fields that are used in the model setup process. Optional inputs are denoted.
@author: brianne
"""
import os, shutil, sys, select
import glob
import collections
import pandas as pd
import json
import re

# Homegrown packages
scripting_tools_dir = os.path.join(os.path.expanduser('~'), os.path.relpath('tools'))
sys.path.append(os.path.join(scripting_tools_dir,'genius'))

class general_study_info:
    def __init__(self):
        self.first_level_data_dir = None
        self.task_output_dir = None
        if self.task_output_dir:
            self.task_output_dir = os.path.basename(self.task_output_dir)
        self.results_output_prefix = None
        if self.results_output_prefix:
            self.results_output_prefix = '_'.join([self.results_output_prefix.split('_')[:-1]]) + "_" # format all sorts of potential entries
        self.first_level_contrast_list = None #List of first-level contrasts that you want to compare
        self.groups =  None # List of tuples names of the groups and trailing signifiers for file list compilation
        if self.groups:
            self.groups = collections.OrderedDict(self.groups)
        
        # Dictionary with keys that title the comparison and values that point to the folders that house the first-levels for the comparisons
        self.comparison_subfolders_dict = None 
        
        self.spm_factors_list = None # To match Jason's desire for pre/post vs. pre/post, us ['Group','Timepoint']
        self.factor_dependences = None # for time being within subject and not independent and Group being independent
        self.regressor_input_file = None
        if self.regressor_input_file:
            self.regressor_input_file = os.path.basename(self.regressor_input_file)
        self.regressors_of_interest = None
        
    def auto_update_study_info(self,json_file=None):
        if not json_file:
            from genius import file_gui
            base = file_gui()
            json_file = base.find_files(msg='Select the study json')
        if isinstance(json_file,list):
            json_file = json_file[0]
        with open(json_file) as read_file:
            self.__dict__ = json.load(read_file, object_pairs_hook=collections.OrderedDict)
        self.json_file=json_file
        
    def manual_update_study_info(self):
        for k, v in self.__dict__.items():
            print('{} set to {}\n'.format(k,v))
            
        key_to_change = input('What would you like to change? (return blank, if nothing)\n')
        while key_to_change != '':
            if 'reg' in key_to_change:
                change_value = 'yes' # dummy variable
                if key_to_change == 'regressor_input_file':
                    change_value = input('Please supply the new values\n')
                    self.__dict__['regressors_of_interest'] = change_value
                    self.update_dir_names(change_value)               
                print('Must choose regressors to load (or enter for none)')
                self.update_regressors()                 
            else:
                change_value = input('Please supply the new values\n')
                if type(self.__dict__[key_to_change]) != type(change_value):
                    orig_type = type(self.__dict__[key_to_change])
                    if isinstance(orig_type, dict):
                        change_value = json.loads(change_value)
                    elif isinstance(orig_type, list):
                        change_value = re.sub("[^a-zA-Z0-9,]","", change_value).split(',')
                    else:
                        print('Expected {}\nInput was {}.\nMay encounter issues.'.format(type(self.__dict__[key_to_change]), type(change_value)))
                self.__dict__[key_to_change] = change_value
            
            # Gather input to break or continue the loop
            key_to_change = input('What else would you like to change? (return blank, if nothing)\n')       
        
        try: 
            if change_value:
                # The user is not asked about overwriting or appending, as this is a manual change. The file can be used as the main json in future analyses, but will marked as simply a manual setup initially.
                self.json_file = self.rename_json_file('_manual_update')
                with open(self.json_file,'w+') as write_file:
                    json.dump(self.__dict__, write_file, indent=4)
        except UnboundLocalError:
            print('Exiting without changing the file')
            
    def update_dir_names(self, new_suffix):
        print('Automatically updating suffixes for result directories.')
        for _ in range(len(self.comparison_subfolders_dict)):
            k, v = self.comparison_subfolders_dict.popitem(last=False)
            basename = k.split('_')[0]
            self.comparison_subfolders_dict[basename + new_suffix] = v
            
    def update_regressors(self):
        if os.path.isfile(self.regressor_input_file):
            # Import the raw demographics-style file
            try:
                df = pd.DataFrame(pd.read_csv(self.regressor_input_file))
            except Exception as e:
                    print(e)
                    df = pd.DataFrame(pd.read_excel(self.regressor_input_file))                 
            if not df.empty:        
                print(df.columns.tolist)            
                self.regressors_of_interest = input('Which one(s) should be used?').strip('\w+\n\t')
                if self.regressors_of_interest:
                    new_suffix = input('What would you like the new suffix to be? ').strip('\w\n_')
                    new_suffix = '_'+ new_suffix
                else:
                    new_suffix = ''
                self.update_dir_names(new_suffix)
            else:
                print('Error loading regressor file.')
            
            
    def rename_json_file(self, suffix):
        suffix = suffix.split('.')[0]  # Discard any extension
        suffix = suffix.strip('\w,._')
        match = re.search(suffix, 'bckp')
        if match:
            m = re.match(suffix,'bckp')
            suffix = m.group(0)
        suffix = '_' + suffix + '.json' # Format underscore and extension
        new_json_name = self.json_file.split('.')[0] + suffix
        return new_json_name
            
    def save_study_info(self, json_file=None):
        """Automatically creates a backup copy of the study parameters"""
        bckp_file_name = self.rename_json_file('bckp')
        if glob.glob(bckp_file_name):
            # Create a running log or overwrite
            print('Backup file exists. Would you like to overwrite [w], append [a], or ignore [i]?')
            tmp, w, x = select.select([sys.stdin], [], [], 10.0)
            if tmp:
                write_opt = sys.stdin.readline().strip('\n')
                if write_opt != "i":
                    print('Writing to {}'.format(bckp_file_name))
                    try:
                        with open(bckp_file_name, write_opt) as write_file:
                            write_file.write('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')
                            json.dump(self.__dict__, write_file, indent=4)
                    except Exception as e:
                        print(e)
            elif not tmp:
                print('No selection made. Ignored writing the json file.')
        else:
            shutil.copyfile(self.json_file, bckp_file_name)

        """In case you wish to overwrite the json file, you may supply a different name as the input argument."""
        if not json_file:
            json_file = self.json_file
            
        with open(json_file,'w+') as write_file:
            json.dump(self.__dict__, write_file, indent=4)
            
if __name__ == '__main__':            
    study = general_study_info()
    study.auto_update_study_info('/data/images/exobk/study_info_exobk.json')
    study.manual_update_study_info()
    study.save_study_info()