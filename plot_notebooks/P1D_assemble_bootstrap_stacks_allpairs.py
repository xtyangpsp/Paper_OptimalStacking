import os,time,pickle
import numpy as np
from seisgo.utils import get_filelist
################################
"""
Assemble all bootstrapping results and get the statistics. The raw bootstrapping waveforms
are NOT assembled.
"""
bootstrap_size,sample_ratio=1000,0.8 #1000 tries. 80% resampling rate.
stackdirbase="stack_by_bootstrap_s"+str(bootstrap_size)+"r"+str(sample_ratio)
dlabels=["Raw","One-bit"]

#############################################
stack_all_xz=dict()
dist_all_xz=dict()
src_all=[]
for i,dlabel in enumerate(dlabels):
    flist=get_filelist(stackdirbase+"_"+dlabels[i],"pk")
    stack_all_xz[dlabel]=dict()
    #
    if i==0:
        with open(flist[0],'rb') as xf:
            stack_temp=pickle.load(xf)
        maxlag_xz=stack_temp["maxlag"]
        dt_xz=stack_temp["dt"]
        npts_xz=stack_temp["data"].shape[-1]
        nmethods=stack_temp["data"].shape[0]
        del stack_temp
    #
    stack_all_xz[dlabel]["min"]=np.ndarray((nmethods,len(flist),npts_xz))
    stack_all_xz[dlabel]["max"]=np.ndarray((nmethods,len(flist),npts_xz))
    stack_all_xz[dlabel]["mean"]=np.ndarray((nmethods,len(flist),npts_xz))
    stack_all_xz[dlabel]["median"]=np.ndarray((nmethods,len(flist),npts_xz))
    stack_all_xz[dlabel]["std"]=np.ndarray((nmethods,len(flist),npts_xz))
    dist_temp=[]
    src=[]
    for j,f in enumerate(flist):
        print(f)
        ftail=os.path.split(f)[1]
        src.append(f.replace('.pk','').split('_')[-1])
        with open(f,'rb') as xf:
            stack_one=pickle.load(xf)
        #
        dist_temp.append(stack_one["dist"])
        for k in range(nmethods):
            data=stack_one["data"][k].copy()
            stack_all_xz[dlabel]["min"][k,j,:] = np.min(data,axis=0)
            stack_all_xz[dlabel]["max"][k,j,:] = np.max(data,axis=0)
            stack_all_xz[dlabel]["mean"][k,j,:] = np.mean(data,axis=0)
            stack_all_xz[dlabel]["median"][k,j,:] = np.median(data,axis=0)
            stack_all_xz[dlabel]["std"][k,j,:] = np.std(data,axis=0)
        #
        del stack_one,data
    #
    src_all.append(src)
    dist_all_xz[dlabel]=np.array(dist_temp)
#
stack_all_xz["maxlag"]=maxlag_xz
stack_all_xz["dt"]=dt_xz
stack_all_xz["npts"]=npts_xz
stack_all_xz["receivers"]=src_all
stack_all_xz["dist"]=dist_all_xz
outfile="xcorr_stacks_allpair_bootstrap_XZ_"+str(bootstrap_size)+"r"+str(sample_ratio)+".pk"
with open(outfile,'wb') as xf:
    pickle.dump(stack_all_xz,xf)
print(">>> saved to: "+outfile)
