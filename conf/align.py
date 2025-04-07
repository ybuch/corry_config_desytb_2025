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
    cmd = f'./corry -c {config} -o EventLoaderEUDAQ2.file_name={files[0]} -o EventLoaderEUDAQ2:TLU_0.file_name={files[1]} -o EventLoaderHDF5.filename={files[2]}   -o EventLoaderMuPixTelescope.input_file={files[3]} -l {log} '
    if additional:
        cmd += additional
    print('\n\n ####### RUNNING: ', cmd,'\n\n')  
    os.system(cmd)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Run Corry software with specific configurations and data files.')
    
    # Define the arguments the script expects
    parser.add_argument('runNmb', type=int, help='Run number used to locate the data files.')
    parser.add_argument('initialGeo', type=str, help='Path to the initial geometry file.')
    parser.add_argument('finalGeo', type=str, help='Path to the final geometry file.')

    # Parse the arguments
    args = parser.parse_args()

    runNmb = args.runNmb
    initialGeo = args.initialGeo
    finalGeo = args.finalGeo

    # Directory paths where the data is stored
    telDir = 'data/telescope'
    tluDir = 'data/tlu'
    dutDir = 'data/dut'

    # List of directories where we need to search for files
    dirs = [telDir, tluDir]

    files = []

    # Globbing the telescope and TLU data files based on the run number
    # We use globbing to find files matching the specific run number pattern
    for d in dirs:
        print(f'Globbing for files in directory {d} with run number {runNmb:06}')
        files_found = glob(f'{d}/*run{runNmb:06}*.raw')
        if files_found:
            files.append(files_found[0])  # Append the first matched file
        else:
            print(f"No files found for run {runNmb:06} in {d}")
            sys.exit(1)  # Exit if no matching files are found

    # Globbing the DUT file based on the run number (converts to .h5 format)
    print(f'Globbing for DUT file with run number {runNmb:06}')
    dut_file_found = glob(f'data/dut/module_0/chip_0/run{runNmb:06}_converted.h5')
    if dut_file_found:
        files.append(dut_file_found[0])  # Append the first matched DUT file
    else:
        print(f"No DUT file found for run {runNmb:06}")
        sys.exit(1)

    # Globbing the telepix2 block file for the given run number
    print(f'Globbing for telepix2 block file for run {runNmb:06}')
    telepix_file_found = glob(f'data/telepix2/single_run_{runNmb:06}.blck')
    if telepix_file_found:
        files.append(os.path.basename(telepix_file_found[0]))  # Append the block file
    else:
        print(f"No telepix2 block file found for run {runNmb:06}")
        sys.exit(1)

    # Running the Corry software with different configuration files
    runCorry('prealign.conf', files, 'logs/log_prealign.txt', f'-o detectors_file={initialGeo}')
    runCorry('align_mille.conf', files, 'logs/log_align_mille.txt', f'-o detectors_file_updated={finalGeo}')
    
    # Optionally, you could add more runs with different configurations
    # runCorry('align_tel.conf', files, 'logs/log_aligntel.txt')
    # runCorry('align_tel2.cfg', files, 'logs/log_aligntel2.txt')
    # runCorry('align_dut.conf', files, 'logs/log_aligndut.txt')
    # runCorry('align_dut2.conf', files, 'logs/log_aligndut2.txt', f'-o detectors_file_updated={finalGeo}')
    # runCorry('align_dut3.cfg', files, 'logs/log_aligndut3.txt', f'-o detectors_file_updated={finalGeo}')

if __name__ == "__main__":
    main()
