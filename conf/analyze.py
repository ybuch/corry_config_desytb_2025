'''
Usage: python3 analyze.py --start 1400 --stop 1568
'''

import argparse
import glob
import re
import os
import pandas as pd


# These paths might need to be changed
data_folder = '/home/bgnet2/s3_cloud/beam_data/desy'
corry_bin = '~/corryvreckan/bin/corry'

# These paths do not need to be changed.
geo_path_tel = '../geo/full_aligned'
dut_align_conf = '../conf/align_dut_mpx2.conf'
analysis_conf = '../conf/analysis.conf'
run_align_folder = '../geo/run_align'
analysis_folder = '../analysis'

do_align_per_run = True
do_analysis = True
number_of_events_align = 100000

parser = argparse.ArgumentParser(description='corry analysis wrapper')
parser.add_argument('-r', help='run number', default = 0, type=int)
parser.add_argument('--start', help='run number start', default = 0, type=int)
parser.add_argument('--stop', help='run number stop', default = 0, type=int)
parser.add_argument('-n', help='number of events for analysis', default = 100000000, type=int)

args = parser.parse_args()

number_of_events_analyze = args.n

if args.r == 0 and (args.start == 0 or args.stop == 0):
    print("Either use run number or start/stop to give a range of runs to be analyzed.")

if args.r != 0:
    run_start = args.r
    run_stop = args.r
else:
    run_start = args.start
    run_stop = args.stop

df = pd.read_csv("../run_properties.csv", sep=",")
data_in_files = glob.glob(data_folder + '/*.raw')

for current_run in range(run_start,run_stop+1):
    if not current_run in df['run_number'].unique():
        continue
    current_dut_file = ''
    current_tel_file = ''
    for f in data_in_files:
        m = re.search(f'mpx2.+run(0*{current_run})', f)
        if m:
            current_dut_file = f

        m = re.search(f'telescope.+run(0*{current_run})', f)
        if m:
            current_tel_file = f
    if current_dut_file == '' or current_tel_file == '':
        print(f'raw_files empty for run {current_run}')
        continue
    print(f'processing tel: {current_tel_file}, dut: {current_dut_file}')
    geo_id = df.loc[df['run_number'] == current_run]['geoid'].values[0]
    tel_full_aligned = geo_path_tel+'/'+f'geo_id{geo_id}_full_aligned.geo'
    run_aligned = run_align_folder+'/'+f'alignment_run_{current_run}.geo'
    run_aligned_histo = '/'+f'alignment_run_{current_run}.root'
    analysis_histo = analysis_folder+'/'+f'analysis_run_{current_run}.root'

    if do_align_per_run:
        print(f'Running alignment for run {current_run}')
        corry_cmd = f'{corry_bin} -c {dut_align_conf} -o number_of_events={number_of_events_align} -o output_directory={run_align_folder} -o detectors_file={tel_full_aligned} -o detectors_file_updated={run_aligned} -o histogram_file={run_aligned_histo} -o EventLoaderEUDAQ2.file_name={current_tel_file} -o EventLoaderEUDAQ2:Monopix2_0.file_name={current_dut_file}'
        print(corry_cmd)
        os.system(corry_cmd)

        #Add mask file path to run aligned file
        with open(run_align_folder+'/'+f'alignment_run_{current_run}.geo', "r") as f:
            contents = f.readlines()

        index = contents.index('[Monopix2_0]\n')
        contents.insert(index+1, f'mask_file="../mask_files/applied_masks/mask_run{current_run}.txt"\n')

        with open(run_aligned, "w") as f:
            contents = "".join(contents)
            f.write(contents)

    if do_analysis:
        print(f'Running anaylsis for run {current_run}')
        corry_cmd = f'{corry_bin} -c {analysis_conf} -o number_of_events={number_of_events_analyze} -o output_directory={analysis_folder} -o detectors_file={run_aligned} -o histogram_file={analysis_histo} -o EventLoaderEUDAQ2.file_name={current_tel_file} -o EventLoaderEUDAQ2:Monopix2_0.file_name={current_dut_file}'
        print(corry_cmd)
        os.system(corry_cmd)
