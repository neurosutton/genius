#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 14:35:47 2019

@author: brianne
"""
import sys
import os                                  
import re
import glob
import scipy.io as sio

from nipype.interfaces.matlab import MatlabCommand
from nipype.interfaces.base import TraitedSpec, BaseInterface, BaseInterfaceInputSpec, File, traits, InputMultiPath, StdOutCommandLine,StdOutCommandLineInputSpec
from string import Template

# Standard library imports
from copy import deepcopy

# Third-party imports
import numpy as np

# Local imports
from nipype.interfaces.base import (OutputMultiPath, TraitedSpec, isdefined,
                                    traits, InputMultiPath, File, CommandLineInputSpec,CommandLine)
from nipype.interfaces.spm.base import (SPMCommand, scans_for_fname,
                                        func_is_3d,
                                        scans_for_fnames, SPMCommandInputSpec)
from nipype.utils.filemanip import (fname_presuffix, filename_to_list,
                                    list_to_filename, split_filename)

class ImageCalcInputSpec(SPMCommandInputSpec):
	#in_file =  File(exists=True, desc='Input Image',field='input',mandatory=True,copyFile=True)
	in_file =  InputMultiPath(File(exists=True), field='input',desc='Input Image',mandatory=True,copyfile=False)
	out_file = File(value='out.nii',desc='Output Image Name',field='output',usedefault=True, genfile=True, hash_files=False)
	out_dir =  File(value='', field='outdir', usedefault=True,desc='Output directory')
	expression = traits.String(field='expression', mandatory=True,desc='Expression for Calculation')
	dmtx = traits.Int(0, field='options.dmtx', usedefault=True,desc='DMTX')
	mask = traits.Int(0, field='options.mask', usedefault=True,desc='Mask')
	interp = traits.Int(0, field='options.interp', usedefault=True,desc='Interpalation')
	data_type = traits.Int(16, field='options.dtype', usedefault=True,desc='Datatype')

class ImageCalcOutputSpec(TraitedSpec):
	out_file = File(exists=True, desc='Output Image')

class ImageCalc(SPMCommand):
	"""Use spm_imcalc to do arbitrary arithmatic on images
	Examples
	--------
	>>> import nipype.interfaces.spm as spm
	>>> calc = ImageCalc()
	>>> calc.inputs.in_files = 'functional.nii'
	>>> calc.inputs.expression = 'i1/5'
	>>> calc.run() # doctest: +SKIP
	"""

	input_spec = ImageCalcInputSpec
	output_spec = ImageCalcOutputSpec
	
	_jobtype = 'util'
	_jobname = 'imcalc'

	def _generate_job(self, prefix='', contents=None):
		if isinstance(prefix,str):
			prefix = prefix.replace("imcalc{1}","imcalc")
		return super(ImageCalc, self)._generate_job(prefix,contents)
		
	def _format_arg(self, opt, spec, val):
		f = re.sub("[\[\]']","",str(self.inputs.in_file))
		if opt == 'out_file':
			val = "calc_"+os.path.basename(f)
			self.inputs.out_file = val
		if opt == 'out_dir':
			val = os.path.dirname(f)+"/"
			self.inputs.out_dir = val
		
		if opt == 'in_file' or opt == 'out_dir':
			if isinstance(val,list):
				return np.array(val,dtype=object)
			return np.array([val],dtype=object)
		return super(ImageCalc, self)._format_arg(opt, spec, val)

	def _list_outputs(self):
		outputs = self._outputs().get()
		out = self.inputs.out_file
		if os.path.isdir(self.inputs.out_dir):
			out = os.path.abspath(self.inputs.out_dir+"/"+out)
		outputs['out_file'] = out
		return outputs