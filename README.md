# Scripts and Notebooks for Optimal Stacking Paper
This repository contains scripts and Jupyter notebooks for the Optimal Stacking paper. Please contact Xiaotao Yang for any questions or open issues.

## 1. Files included in this repository

**xcorr_scripts**

* X1A_download_MPI_cascadia.py: download cascadia example data (raw waveforms).
* X1B_download_MPI_XZ.py: download raw waveforms of the XZ array data.
* X2A_xcorr_MPI_cascadia_raw.py: compute cross-correlaiton functions of the cascadia data using raw method without normalization.
* X2A_xcorr_MPI_cascadia_tnorm.py: compute cascadia correlation functions using One-bit normalized data.
* X2B_xcorr_MPI_XZ_raw.py: compute XZ correlation functions without normalization.
* X2B_xcorr_MPI_XZ_tnorm.py: compute XZ correlation functions with One-bit time-domain normalization.
* X3A_merge_pairs_MPI_cascadia_raw.py: merge the short-time window correlation functions for each station pair for the cascadia data without normalization.
* X3A_merge_pairs_MPI_cascadia_tnorm.py: merge the short-time window correlation functions for each station pair for the cascadia data (One-bit normalized).
* X3B_merge_pairs_MPI_XZ_raw.py: merge the short-time window correlation functions for each station pair for the XZ data without normalization.
* X3B_merge_pairs_MPI_XZ_tnorm.py: merge the short-time window correlation functions for each station pair for the XZ data with One-bit normalization.


**plot_notebooks**

* P1A_compute_stacks_singlepair.ipynb: stacks of single station pairs for examples in the paper.
* P1B_compute_stacks_allpairs.ipynb: stack of all station pairs from the same virtual sources as used to analyze the moveout-based metrics.
* P1C_compute_stacks_allpairs_bootstrap.py: bootstrap test with random resampling of the whole data set, to examine the influence of temporal variation of the NCF data.
* P1D_assemble_bootstrap_stacks_allpair.py: merge and get the statistics of the bootstrap test. The orginal test output is large (40 Gb or so). This script only keep sthe statistics and the mean NCF stack for each station pair.
* P2A_plot_stacks_singlepair.ipynb: plot single-station pair examples.
* P2B_plot_stacks_allpairs.ipynb: plot moveout or any moveout-based figures.
* P2C_plot_dispersion.ipynb: plot dispersion examples for the XZ array with one example virtual source.
* P2D_plot_stackamplitudes_bootstrap.ipynb: plot the amplitude decay measurements from the XZ array.
* P2E_compare_tfpws_methods.ipynb: compare the two different implementations of the tf-PWS method, using the original stockwell transform or the discret orthogonal stockwell transform. This notebook compares the time and stacking results.

## 2. Python environment

The scripts and notebooks rely on `seisgo` and, optionally, `stackmaster`. The key stacking functions in `stackmaster` have been incorporated in `seisgo`. These two packages could be installed from PyPI project: `pip install seisgo` (https://github.com/xtyangpsp/SeisGo) and `pip install stackmaster` (https://github.com/xtyangpsp/StackMaster). However, we recommend the users following the instructions on https://github.com/xtyangpsp/SeisGo to create a designed Python environment to avoid conflicts with other packages and/or projects.

**To run P2C to compute Structural Similarity Index between dispersion images, package `scikit-image` (https://scikit-image.org/docs/stable/install.html) is required. It can be installed with `pip install scikit-image`.**

## 3. Steps to compute the cross-correlaiton data

All scripts in this section are under **xcorr_scripts** folder. We will refer to the files with the numbered prefixes for each file, e.g., `X1A` refers to `xcorr_scripts/X1A_download_MPI_cascadia.py`. There are two data sets to be processed, tagged as `cascadia` and `XZ` for all processing scripts.

* step-1: Download all data by running scripts X1A and X1B.
* step-2: Compute cross-correlaitons by running scripts X2A and X2B. Please note that X2A and X2B both include two scripts for the Cascadia and XZ datasets.
* step-3: Merge station pairs by running X3A and X3B. Same as step-2, there are two scripts for each dataset.


## 4. Steps to reproduce the figures

All notebooks under **plot_notebooks** should be run under the same Python environment.

* step-1: compute the stacking results for all examples used in the paper, by running P1A and P1B. For the PWS method, we use DOST-based tf-PWS in the examples because of its much-improved effieiency compared to the implementation with the original Stockwell transform. You can change the method list to try the original tf-PWS. The DOST-based tf-PWS is tagged as "tf-pws_dost". Because of the slow-performance of the original tf-PWS method, P1B would take hours to 2-3 days to run depending on the CPU performance.
* step-2: plot all figures with notebooks P2A, P2B,  P2C, P2D, and P2E.


## 5. Reference
Please cite this repository as:
```
@article{Yang2022stacking,
  author       = {Xiaotao Yang and
                  Jared Bryan and
                  Kurama Okubo and
                  Chengxin Jiang and
                  Timothy Clements and
                  Marine A Denolle},
  title        = {{Optimal Stacking of Noise Cross-Correlation Functions}},
  journal = {Geophysical Journal International}
  month        = x,
  year         = in review,
}
```
