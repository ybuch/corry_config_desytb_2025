import re
import os
import sys
import argparse
from glob import glob


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

    if '-' in runs:
        splitted = runs.split('-')
        first = int(splitted[0])
        last = int(splitted[1])
    else:
        first = last = int(runs)
    
    with open('slurm_submit_template', 'r') as file:
        slurm_generic = file.read()
    file.close

    # Loop through the range of runs
    for runNmb in range(first, last + 1):
        
        slurm = slurm_generic.replace("<jobname>",f"run_{runNmb}").replace("<runnumber>",f"{runNmb}").replace("<geopath>",f"{geo}").replace("<config>",f"{config}")
        with open(f"slurm_submission_scripts/slurm_submit_{runNmb}", "w") as text_file:
            text_file.write(slurm)
        if True:
            os.system(f"sbatch slurm_submission_scripts/slurm_submit_{runNmb}")

if __name__ == "__main__":
    main()

