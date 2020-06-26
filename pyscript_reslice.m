fprintf(1,'Executing %s at %s:\n',mfilename(),datestr(now));
ver,
try,
        flags.mean = 0;
        flags.which = 1;
        flags.mask = 0;
        flags.interp = 0;
        infiles = strvcat('/data/images/exobk/exo245_3_d/fp_results_aCompCorr/fsl_exo245_3_d_fp_results_aCompCorr_spmT_0004.nii.gz', '/data/images/exobk/exo245_3_d/t1/thresh_mwc2exo245_3_t1_0005_20170811.nii');
        invols = spm_vol(infiles);
        spm_reslice(invols, flags);
        
,catch ME,
fprintf(2,'MATLAB code threw an exception:\n');
fprintf(2,'%s\n',ME.message);
if length(ME.stack) ~= 0, fprintf(2,'File:%s\nName:%s\nLine:%d\n',ME.stack.file,ME.stack.name,ME.stack.line);, end;
end;