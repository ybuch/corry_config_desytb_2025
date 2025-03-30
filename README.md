# General Instructions

This repo contains needed scripts and files for the alignment and analysis of TB data. Please note that paths need to be updated in the scrips as well as in geo files (path to mask files). The scripts also assume that the corryvreckan binary is in PATH. 

Alignment: run `full_align.sh` for each geo_id (telescope and DUT alignment) and afterwards `run_alignment.sh` for each run (DUT alignment).

Masking: run `mask_generator.sh` which generates a mask file from a default mask (masking not used frontends) and a yaml file (list of disabeled pixels in the data taking). Please nothe that the default masks do not work for all runs since the frontends were also changed within geo_ids! These masks were adapted by hand and a set of working masks is stored under initial_masks.

Analysis: is done using jobsub which is installed under your corry installation (see corry manual and below). A csv file has to be created with `data_searcher.sh` which contains information of geo and data for each run before starting the analysis.
## Software

Root: 6.24/06, ROOT 6.26/10 seem to work both.
Eudaq: https://github.com/bpilsl/eudaq/tree/monopix2
Corryvreckan: Master branch cf10f1ad0a4ff3e21eb8bdc7235664727f3393f4

## Docker

Refer to readme in docker folder for more information

## conf

This folder contains all config files for corry which are used for the alignment as well as scripts.

### full_align.sh

Script for the alignment of a geo_id (usage: `source ./full_align.sh <runnumber_to_align> <geo_id>`).
It uses `prealign_tel_mpx2.conf`, `align_dut_mpx2.conf` and `align_tel_mpx2.conf`, the output is stored under `/geo/full_aligned`. The initial geo file is taken from `/geo/init_geo`.

### run_alignment.sh

Script for the alignment of the DUT for each run starting from the output geo of `full_align.sh`. Reads the runnumbers and geo_ids from one of the following files: `W02R05_standard.csv`, `W05R15_TID.csv` or `W08R06_p.csv`. The output is stored under `/geo/temp`.

### W02R05_standard.csv, W05R15_TID.csv, W08R06_p.csv

List of runnumbers with matching geo_ids

## geo/mask_files

Folder containing used mask files (applied_masks) and scripts for generating mask_files.

### mask_generator.sh

This script copies a default mask from the default folder (containing information about the masking of the not activated frontends) and appends the information of the yaml files depending on the runnumber (by using extract_masked_pixels.py). The output is stored in the folder applied_masks. Please note that the default masks are not propper for all runs since changes in the masking werde done throughout equal geo_ids. Already finished masks can be found in the folder initial_masks.

### analysis

Use conf/analyze.py. This convenience script does a run specific DUT alignment and analyses the run using the analysis.conf. 
