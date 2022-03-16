import sys,time,os, glob
from mpi4py import MPI
from seisgo import noise
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

'''
Stacking script of SeisGo to:
    1) load cross-correlation data for each station pair
    2) merge all time chuncks
    3) save outputs in ASDF;
'''
tt0=time.time()
########################################
#########PARAMETER SECTION##############
########################################
# absolute path parameters
rootpath  = "data_stacking"                                 # root path for this data processing
CCFDIR    = os.path.join(rootpath,'CCF_cascadia_tnorm')                            # dir where CC data is stored
MERGEDIR  = os.path.join(rootpath,'MERGED_cascadia_tnorm')                          # dir where stacked data is going to
to_egf = False                                               #convert CCF to empirical Green's functions when merging
flag   = True                                                # output intermediate args for debugging
stack = False
win_len = 3600*12
#######################################
###########PROCESSING SECTION##########
#######################################
#--------MPI---------
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    if not os.path.isdir(MERGEDIR):os.mkdir(MERGEDIR)
    # cross-correlation files
    ccfiles   = sorted(glob.glob(os.path.join(CCFDIR,'*.h5')))
    pairs_all,netsta_all=noise.get_stationpairs(ccfiles,False)
    splits  = len(pairs_all)
    if len(ccfiles)==0 or splits==0:
        raise IOError('Abort! no available CCF data for merging')

    for s in netsta_all:
        tmp = os.path.join(MERGEDIR,s)
        if not os.path.isdir(tmp):os.mkdir(tmp)
else:
    splits,ccfiles,pairs_all,ccomp_all = [None for _ in range(4)]

# broadcast the variables
splits    = comm.bcast(splits,root=0)
ccfiles   = comm.bcast(ccfiles,root=0)
pairs_all = comm.bcast(pairs_all,root=0)
# MPI loop: loop through each user-defined time chunck
for ipair in range (rank,splits,size):
    pair=pairs_all[ipair]
    if flag:print('station-pair %s'%(pair))
    noise.merge_pairs(ccfiles,pairlist=pair,outdir=MERGEDIR,verbose=False,to_egf=to_egf,stack=stack,stack_win_len=win_len)

tt1 = time.time()
print('it takes %6.2fs to merge in total' % (tt1-tt0))
comm.barrier()

# merge all path_array and output
#if rank == 0:
#    sys.exit()
