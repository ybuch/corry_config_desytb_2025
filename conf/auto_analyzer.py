import sys
import re
from glob import glob
import os
import numpy as np

skip_until_run = 1820
init_geo = "/home/bgnet/desy_202503/geo/initial_geo/geo_id1_improved.geo"
updated_path = "/home/bgnet/desy_202503/geo/updated_geo"

# if len(sys.argv) < 2:
#     print('Can I haz path to geometry file pls :)')
#     exit()

check_path = "/home/bgnet/desy_202503/desy-tb-2025/data/dut/module_0/chip_0/"
output_path = "/media/bgnet/testbeam_data/desy_202503/conf/output/"
corry_config_template = "analysis_full.conf"

analyzed_run_files = glob(f"{output_path}/analysis*.root")
analyzed_run_numbers = [int(re.search(r"analysis_(\d+)\.root", f).group(1)) for f in analyzed_run_files]
print('analyzed: ', analyzed_run_numbers)

#do not analyze old runs
analyzed_run_numbers.extend([i for i in range(skip_until_run)])

available_run_files = glob(f"{check_path}/*converted*.h5")
available_run_numbers = [int(re.search(r"run(\d+)", f).group(1)) for f in available_run_files]
print('available: ', available_run_numbers)

not_analyzed_runs = list(set(available_run_numbers) - set(analyzed_run_numbers))
print('I will now analyze the following runs for you:', not_analyzed_runs)
for run in not_analyzed_runs:
    updated_geo = f"{updated_path}/aligned{run}.geo"
    align_cmd = f"python align.py {run} {init_geo} {updated_geo}"
    print('aligning with', align_cmd)
    os.system(align_cmd)
    ana_cmd = f"python analyze.py {run} {updated_geo} {corry_config_template}"    
    print('analizing with', ana_cmd)
    os.system(ana_cmd)

                                             
