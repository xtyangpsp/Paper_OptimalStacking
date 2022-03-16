#!/usr/bin/env python
# coding: utf-8
import sys
import time
import scipy
import obspy
import pyasdf
import datetime
import os, glob
import numpy as np
import pandas as pd
from mpi4py import MPI
from scipy.fftpack.helper import next_fast_len
from seisgo import noise
from seisgo import utils

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

# absolute path parameters
rootpath  = 'data_stacking'                                     # root path for this data processing
CCFDIR    = os.path.join(rootpath,'CCF_XZ_tnorm')                                    # dir to store CC data
DATADIR   = os.path.join(rootpath,'Raw_XZ')                               # dir where noise data is located
locations = os.path.join(rootpath,'station.txt')                            # station info including network,station,channel,latitude,longitude,elevation: only needed when input_fmt is not asdf

# some control parameters
freq_norm   = 'no'                                                  # 'no' for no whitening, or 'rma' for running-mean average, 'phase' for sign-bit normalization in freq domain
time_norm   = 'one_bit'                                                          # 'no' for no normalization, or 'rma', 'one_bit' for normalization in time domain
cc_method   = 'xcorr'                                                       # 'xcorr' for pure cross correlation, 'deconv' for deconvolution; FOR "COHERENCY" PLEASE set freq_norm to "rma" and time_norm to "no"
acorr_only  = False                                                         # only perform auto-correlation
xcorr_only  = True                                                          # only perform cross-correlation or not
exclude_chan = []        #Added by Xiaotao Yang. Channels in this list will be skipped.

# pre-processing parameters
cc_len    = 6*3600                                                            # basic unit of data length for fft (sec)
step      = 3*3600                                                             # overlapping between each cc_len (sec)
smooth_N  = 20                                                              # moving window length for time/freq domain normalization if selected (points)

# cross-correlation parameters
maxlag         = 700                                                        # lags of cross-correlation to save (sec)
substack       = True #False                                                      # sub-stack daily cross-correlation or not
substack_len   = 1*cc_len                                                  # how long to stack over (for monitoring purpose): need to be multiples of cc_len
smoothspect_N  = 20                                                         # moving window length to smooth spectrum amplitude (points)

# criteria for data selection
max_over_std = 10                                                           # threahold to remove window of bad signals: set it to 10*9 if prefer not to remove them
max_kurtosis = 10                                                           # max kurtosis allowed, TO BE ADDED!

# load useful download info if start from ASDF
freqmin   = 0.01 #down_info['freqmin']
freqmax   = 2.5  #down_info['freqmax']
##################################################
# we expect no parameters need to be changed below
#--------MPI---------
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # make a dictionary to store all variables: also for later cc
    fc_para={'cc_len':cc_len,'step':step,
            'freqmin':freqmin,'freqmax':freqmax,'freq_norm':freq_norm,'time_norm':time_norm,
            'cc_method':cc_method,'smooth_N':smooth_N,'substack':substack,'substack_len':substack_len,
            'smoothspect_N':smoothspect_N,'maxlag':maxlag,'max_over_std':max_over_std,
            'max_kurtosis':max_kurtosis}
    # save fft metadata for future reference
    fc_metadata  = os.path.join(CCFDIR,'fft_cc_data.txt')
    if not os.path.isdir(CCFDIR):os.makedirs(CCFDIR)
    # save metadata
    fout = open(fc_metadata,'w')
    fout.write(str(fc_para));fout.close()

    # set variables to broadcast
    tdir = sorted(glob.glob(os.path.join(DATADIR,'*.h5')))

    nchunk = len(tdir)
    splits  = nchunk

    if nchunk==0: raise IOError('Abort! no available seismic files for FFT')

else:
    splits,tdir = [None for _ in range(2)]

# broadcast the variables
splits = comm.bcast(splits,root=0)
tdir  = comm.bcast(tdir,root=0)
#loop through all data files.
for ick in range(rank,splits,size):
    sfile=tdir[ick]
    t10=time.time()
    #call the correlation wrapper.
    noise.do_correlation(sfile,cc_len,step,maxlag,cc_method=cc_method,
                         acorr_only=acorr_only,xcorr_only=xcorr_only,substack=substack,
                         smoothspect_N=smoothspect_N,substack_len=substack_len,
                         maxstd=max_over_std,freqmin=freqmin,freqmax=freqmax,
                         time_norm=time_norm,freq_norm=freq_norm,smooth_N=smooth_N,
                         exclude_chan=exclude_chan,outdir=CCFDIR)

    t11 = time.time()
    print('it takes %6.2fs to process the chunk of %s' % (t11-t10,sfile.split('/')[-1]))

comm.barrier()

# merge all path_array and output
#if rank == 0:
#    sys.exit()
