#!/usr/bin/env python
# coding: utf-8

# # Bootstrapping the stacks for all pairs from single sources

# In[1]:


import os,random,time,pickle,sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from obspy.signal.filter import bandpass
from seisgo import noise,utils,plotting
from seisgo.stacking import stack
import pygmt as gmt
from obspy import UTCDateTime
from multiprocessing import Pool


# In[ ]:


def stack_wrapper(infile,outdir,bootstrap_size,sample_ratio,methods,source):
    """
    bootstrap_size: number of bootstrapping tries.
    """
    comp="ZZ"
    f=infile.replace("\n","")
    ftail=os.path.split(f)[1]
    outfile=os.path.join(outdir,ftail.replace('h5','pk'))
    print(f+'-->'+outfile)
    cdict=noise.extract_corrdata(f,comp=comp)
    pair=list(cdict.keys())[0]
    cdata=cdict[pair][comp]
            
#     netsta1 = cdata.net[0]+'.'+cdata.sta[0]#+'.'+c.loc[0]+'.'+c.chan[0]
    netsta2 = cdata.net[1]+'.'+cdata.sta[1]#+'.'+c.loc[1]+'.'+c.chan[1]
    stack_all=dict()
    stack_all["maxlag"]=cdata.lag
    stack_all["dt"]=cdata.dt
    stack_all["N"]=bootstrap_size
    stack_all["resample"]=sample_ratio
    stack_all["dist"]=cdata.dist
    stack_all['data']=np.ndarray((len(methods),bootstrap_size,cdata.data.shape[1]))

    ntrace=len(cdata.time)
    idxlist=set(np.arange(0,ntrace,1))
    nsample=int(sample_ratio*ntrace)

    for k,m in enumerate(methods):
        for p in range(bootstrap_size):
            if nsample<1: 
                pass 
            else:
                idx0=random.sample(idxlist,k=nsample)
                data_temp=cdata.data[idx0,:].copy()
                ds = stack(data_temp,m)
                if netsta2.lower() == source.lower(): ds=np.flip(ds)
                stack_all['data'][k,p,:]=ds

    with open(outfile,'wb') as xf:
            pickle.dump(stack_all,xf)
    del stack_all

def main():
    narg=len(sys.argv)
    if narg == 1:
        nproc=1
    else:
        nproc=int(sys.argv[1])
    print(str(nproc)+' processors.')
    ##############
    dataroot='data_stacking'

    raw_xz=os.path.join(dataroot,"MERGED_XZ_raw")
    tnorm_xz=os.path.join(dataroot,"MERGED_XZ_tnorm")
    outdir="stack_by_bootstrap"
    dlabels=["Raw","One-bit"]
    methods=["linear","robust","selective","cluster","pws","tfpws-dost","nroot","acf"]

    # ### XZ pairs from a single virtual source
    XZ_source="XZ.A02"
    network="XZ"
    bootstrap_size,sample_ratio=100,0.8 #100 tries. 50% resampling rate.

    flist_xz=[utils.get_filelist(raw_xz+"/"+XZ_source,"h5"),
              utils.get_filelist(tnorm_xz+"/"+XZ_source,"h5")]
    t1=time.time()
    if nproc>=2: pp=Pool(int(nproc))
    for j,dlabel in enumerate(dlabels):
        # j=1
        # dlabel=dlabels[j]
        print('working on: '+dlabel+' with '+str(len(flist_xz[j]))+' files.')
        outdir_temp=outdir+"_s"+str(bootstrap_size)+"r"+str(sample_ratio)+"_"+dlabel
        if not os.path.isdir(outdir_temp): os.makedirs(outdir_temp)
        if nproc < 2:
            stack_all_out=[]
            for i,fname in enumerate(flist_xz[j]):
                stack_wrapper(fname,outdir_temp,bootstrap_size,sample_ratio,methods,XZ_source)
        else:
            pp.starmap(stack_wrapper,[(fname,outdir_temp,bootstrap_size,sample_ratio,
                                                     methods,XZ_source) for fname in flist_xz[j]])
        
    if nproc>=2: pp.close()

    print("finished in %f s"%(time.time() - t1))
    

#####
if __name__ == "__main__":
    main()

