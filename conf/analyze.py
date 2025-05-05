import re
import os
import sys
import argparse
from glob import glob

def runCorry(config, files, log, additional=None):
    """
    Function to execute the Corry software with the given parameters.
    Args:
        config: The configuration file to use.
        files: A list of files required by the Corry program.
        log: Log file where the output will be saved.
        additional: Optional string with additional arguments to pass to the Corry program.
    """
    cmd = f'corry -c {config} -o EventLoaderEUDAQ2.file_name={files[0]} -o EventLoaderEUDAQ2:TLU_0.file_name={files[1]} -o EventLoaderHDF5.filename={files[2]} -l {log} -o EventLoaderMuPixTelescope.input_file={files[3]} -l {log} '
    if additional:
        cmd += additional
    print(cmd)  
    os.system(cmd)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Run Corry software with specified configurations and data files.')
    
    # Define the arguments the script expects
    parser.add_argument('runs', type=str, help='Run number or range of run numbers (e.g., "1", or "1-5").')
    parser.add_argument('geo', type=str, help='Path to the geometry file to use.')
    parser.add_argument('config', type=str, nargs='?', default='analysis.conf', help='Configuration file to use (default: analysis.conf).')

    # Parse the arguments
    args = parser.parse_args()

    runs = args.runs
    geo = args.geo
    config = args.config
    geo_dut_aligned = geo[:-4] + "_dut_aligned.geo"
    geo_dut_pre_aligned = geo[:-4] + "_dut_pre_aligned.geo"

    data_path = '/s3_cloud/TB2025/desy-tb-2025'

    # Directory paths where the data is stored
    telDir = data_path+'/data/telescope'
    tluDir = data_path+'/data/tlu'
    dutDir = data_path+'/data/dut'
    mask_file_mimosa26_0 = '/corry_config_desytb_2025/geo/mask_files/mask_MIMOSA26_0.txt'
    mask_file_mimosa26_1 = '/corry_config_desytb_2025/geo/mask_files/mask_MIMOSA26_1.txt'
    mask_file_mimosa26_2 = '/corry_config_desytb_2025/geo/mask_files/mask_MIMOSA26_2.txt'
    mask_file_mimosa26_3 = '/corry_config_desytb_2025/geo/mask_files/mask_MIMOSA26_3.txt'
    mask_file_mimosa26_4 = '/corry_config_desytb_2025/geo/mask_files/mask_MIMOSA26_4.txt'
    mask_file_mimosa26_5 = '/corry_config_desytb_2025/geo/mask_files/mask_MIMOSA26_5.txt'

    # List of directories to glob for the files
    dirs = [telDir, tluDir]

    # Default first and last run number
    first = last = 0

    # If a range is provided, split it into first and last
    if '-' in runs:
        splitted = runs.split('-')
        first = int(splitted[0])
        last = int(splitted[1])
    else:
        first = last = int(runs)

    # Loop through the range of runs
    for runNmb in range(first, last + 1):

        #os.system(f'python /s3_cloud/TB2025/desy-tb-2025/find_masked_pixel_analysis.py {runNmb}')
        mask_file = data_path+f'/data/dut/module_0/chip_0/run{str(runNmb).zfill(6)}_masked_pixels.txt'

        files = []

        # Globbing for telescope and TLU data files based on the run number
        for d in dirs:
            print(f'Globbing for files in {d} with run number {runNmb:06}')
            files_found = glob(f'{d}/*run{runNmb:06}*.raw')
            if files_found:
                files.append(files_found[0])  # Append the first matched file
            else:
                print(f"No files found for run {runNmb:06} in {d}")
                sys.exit(1)  # Exit if no matching files are found

        # Globbing for the DUT file
        print(f'Globbing for DUT file with run number {runNmb:06}')
        dut_file_found = glob(data_path+f'/data/dut/module_0/chip_0/run{runNmb:06}_converted.h5')
        if dut_file_found:
            files.append(dut_file_found[0])  # Append the first matched DUT file
        else:
            print(f"No DUT file found for run {runNmb:06}")
            sys.exit(1)

        # Globbing for the telepix2 block file
        print(f'Globbing for telepix2 block file for run {runNmb:06}')
        telepix_file_found = glob(data_path+f'/data/telepix2/single_run_{runNmb:06}.blck')
        if telepix_file_found:
            files.append(os.path.basename(telepix_file_found[0]))  # Append the block file
        else:
            print(f"No telepix2 block file found for run {runNmb:06}")
            sys.exit(1)

        # Run Corry with the found files and configuration
        runCorry("align_dut.conf",files, f'/corry_config_desytb_2025/logs/log_dut_align1{runNmb:06}.txt',f'-o histogram_file=dut_align_{runNmb:06}.root -o detectors_file={geo} -o number_of_tracks=50000 -o detectors_file_updated={geo_dut_pre_aligned} -o DUTAssociation.spatial_cut_abs=150um,150um -g Monopix2_0.mask_file={mask_file} -g MIMOSA26_0.mask_file={mask_file_mimosa26_0} -g MIMOSA26_1.mask_file={mask_file_mimosa26_1} -g MIMOSA26_2.mask_file={mask_file_mimosa26_2} -g MIMOSA26_3.mask_file={mask_file_mimosa26_3} -g MIMOSA26_4.mask_file={mask_file_mimosa26_4} -g MIMOSA26_5.mask_file={mask_file_mimosa26_5}')
        runCorry("align_dut.conf",files, f'/corry_config_desytb_2025/logs/log_dut_align2{runNmb:06}.txt',f'-o histogram_file=dut_align_{runNmb:06}.root -o detectors_file={geo_dut_pre_aligned} -o number_of_tracks=75000 -o detectors_file_updated={geo_dut_aligned} -o DUTAssociation.spatial_cut_abs=50um,50um -g Monopix2_0.mask_file={mask_file} -g MIMOSA26_0.mask_file={mask_file_mimosa26_0} -g MIMOSA26_1.mask_file={mask_file_mimosa26_1} -g MIMOSA26_2.mask_file={mask_file_mimosa26_2} -g MIMOSA26_3.mask_file={mask_file_mimosa26_3} -g MIMOSA26_4.mask_file={mask_file_mimosa26_4} -g MIMOSA26_5.mask_file={mask_file_mimosa26_5}')
        runCorry(config, files, f'/corry_config_desytb_2025/logs/log_ana{runNmb:06}.txt', f'-o histogram_file=analysis_{runNmb:06}.root -o detectors_file={geo_dut_aligned} -g Monopix2_0.mask_file={mask_file} -g MIMOSA26_0.mask_file={mask_file_mimosa26_0} -g MIMOSA26_1.mask_file={mask_file_mimosa26_1} -g MIMOSA26_2.mask_file={mask_file_mimosa26_2} -g MIMOSA26_3.mask_file={mask_file_mimosa26_3} -g MIMOSA26_4.mask_file={mask_file_mimosa26_4} -g MIMOSA26_5.mask_file={mask_file_mimosa26_5}')

if __name__ == "__main__":
    main()
