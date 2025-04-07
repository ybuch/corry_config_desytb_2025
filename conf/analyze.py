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
    cmd = f'./corry -c {config} -o EventLoaderEUDAQ2.file_name={files[0]} -o EventLoaderEUDAQ2:TLU_0.file_name={files[1]} -o EventLoaderHDF5.filename={files[2]} -l {log} -o EventLoaderMuPixTelescope.input_file={files[3]} -l {log} '
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

    # Directory paths where the data is stored
    telDir = 'data/telescope'
    tluDir = 'data/tlu'
    dutDir = 'data/dut'

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

        os.system(f'python ../geo/find_masked_pixel_analysis.py {runNmb}')
        mask_file = f'../mask_files/run{str(runNmb).zfill(6)}_masked_pixels.txt'
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
        dut_file_found = glob(f'data/dut/module_0/chip_0/run{runNmb:06}_converted.h5')
        if dut_file_found:
            files.append(dut_file_found[0])  # Append the first matched DUT file
        else:
            print(f"No DUT file found for run {runNmb:06}")
            sys.exit(1)

        # Globbing for the telepix2 block file
        print(f'Globbing for telepix2 block file for run {runNmb:06}')
        telepix_file_found = glob(f'data/telepix2/single_run_{runNmb:06}.blck')
        if telepix_file_found:
            files.append(os.path.basename(telepix_file_found[0]))  # Append the block file
        else:
            print(f"No telepix2 block file found for run {runNmb:06}")
            sys.exit(1)

        # Run Corry with the found files and configuration
        runCorry(config, files, f'logs/log_ana{runNmb:06}.txt', f'-o histogram_file=analysis_{runNmb:06}.root -o detectors_file={geo} -g Monopix2_0.mask_file={mask_file}')

if __name__ == "__main__":
    main()
