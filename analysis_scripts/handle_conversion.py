import pandas as pd
import re
from glob import glob
import os

#input_file = "/projects/scc/UGOE/UPFB/UPP2/scc_ugoe_upfb_frey/dir.project/tb_data/TB2025/desy-tb-2025/data/dut/module_0/charge_calibrated/run002094_20250412_101501_ext_trigger_scan_interpreted.h5"
#trigger_mode = "aida"
#tot_calib_file = '/projects/scc/UGOE/UPFB/UPP2/scc_ugoe_upfb_frey/dir.project/tb_data/TB2025/desy-tb-2025/ToT_TB2025_runs/run002094_20250701_122526_threshold_scan_interpreted_tot_calibration_fit3par_charge_mean.h5'

dcc_conversion_factor = 9
hvc_conversion_factor = 18

calib_path = '/projects/scc/UGOE/UPFB/UPP2/scc_ugoe_upfb_frey/dir.project/tb_data/TB2025/desy-tb-2025/ToT_TB2025_runs'
calib_run_files = glob(f"{calib_path}/*fit3par_charge_mean.h5")
calib_run_numbers = [int(re.search(r"run00(\d+).*?fit3par_charge_mean\.h5", f).group(1)) for f in calib_run_files]
#print(calib_run_numbers)

available_path = '/projects/scc/UGOE/UPFB/UPP2/scc_ugoe_upfb_frey/dir.project/tb_data/TB2025/desy-tb-2025/data/dut/module_0/charge_calibrated'
available_run_files = glob(f"{available_path}/*converted*.h5")
available_run_numbers = [int(re.search(r"run(\d+)", f).group(1)) for f in available_run_files]
#print(available_run_numbers)

not_calibrated_runs = list(set(calib_run_numbers) - set(available_run_numbers))
#print(sorted(not_calibrated_runs))
print('calib_run_numbers',sorted(calib_run_numbers))
print('available_run_numbers',sorted(available_run_numbers))
print('uncal', sorted(not_calibrated_runs))

file = '/user/buch10/u14336/corry_config_desytb_2025/analysis_scripts/config_summary_TB_GOODruns_google.csv'
df = pd.read_csv(file, sep=',')

file = '/user/buch10/u14336/corry_config_desytb_2025/analysis_scripts/elog_extracted.csv'
df_elog = pd.read_csv(file, sep=',')


for calibration_avail in sorted(calib_run_numbers):
    if int(calibration_avail) >= 1863:
        trigger_mode_p = 'aida'
    else:
        trigger_mode_p = 'eudet'
    print(f"Run: {calibration_avail}, device: {(df[(df['Run number']==calibration_avail)]['chip_sn']).values}, frontend: {(df[(df['Run number']==calibration_avail)]['frontend']).values}, trigger_mode: {trigger_mode_p}")


for not_cal in not_calibrated_runs:
    if int(not_cal) >= 1863:
        trigger_mode = 'aida'
    else:
        trigger_mode = 'eudet'
    device = (df[(df['Run number']==not_cal)]['chip_sn']).values
    assert(len(device)==1)
    device = device[0]
    if device == 'W8R6': 
        frontend = df[(df['Run number']==not_cal)]['frontend'].values
        assert(len(frontend)==1)
        frontend = frontend[0]
        if (frontend in ['HVC']):
            print(f"Run: {not_cal}, configid: {df_elog[(df_elog['Run_no']==not_cal)]['ConfigID']}, device: {device}, frontend: {frontend}, factor: {hvc_conversion_factor}, trigger_mode: {trigger_mode}")
            input_file = glob(f"{available_path}/run00{not_cal}_*_*_ext_trigger_scan_interpreted.h5")[0]
            tot_calib_file = glob(f"{calib_path}/run00{not_cal}_*_*_threshold_scan_interpreted_tot_calibration_fit3par_charge_mean.h5")[0]
            #print(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 corryvreckan_converter.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file}')
            if trigger_mode == 'aida':
                print(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 corryvreckan_converter.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file} --conversion_factor {hvc_conversion_factor}')
                os.system(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 corryvreckan_converter.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file} --conversion_factor {hvc_conversion_factor}')
            if trigger_mode == 'eudet':
                print(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 /user/buch10/u14336/corry_config_desytb_2025/analysis_scripts/corry_converter_dup.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file} --conversion_factor {hvc_conversion_factor}')
                os.system(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 /user/buch10/u14336/corry_config_desytb_2025/analysis_scripts/corry_converter_dup.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file} --conversion_factor {hvc_conversion_factor}')

        elif (frontend in ['DCC']):
            print(f"Run: {not_cal}, configid: {df_elog[(df_elog['Run_no']==not_cal)]['ConfigID']}, device: {device}, frontend: {frontend}, factor: {dcc_conversion_factor}, trigger_mode: {trigger_mode}")
            input_file = glob(f"{available_path}/run00{not_cal}_*_*_ext_trigger_scan_interpreted.h5")[0]
            tot_calib_file = glob(f"{calib_path}/run00{not_cal}_*_*_threshold_scan_interpreted_tot_calibration_fit3par_charge_mean.h5")[0]
            #print(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 corryvreckan_converter.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file}')
            if trigger_mode == 'aida':
                print(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 corryvreckan_converter.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file} --conversion_factor {dcc_conversion_factor}')
                os.system(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 corryvreckan_converter.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file} --conversion_factor {dcc_conversion_factor}')
            if trigger_mode == 'eudet':
                print(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 /user/buch10/u14336/corry_config_desytb_2025/analysis_scripts/corry_converter_dup.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file} --conversion_factor {dcc_conversion_factor}')
                os.system(f'source $HOME/.bashrc && conda activate vtx_upgrade && python3 /user/buch10/u14336/corry_config_desytb_2025/analysis_scripts/corry_converter_dup.py --input_file {input_file} --trigger_mode {trigger_mode} --tot_calib_file {tot_calib_file} --conversion_factor {dcc_conversion_factor}')
        
        else:
            continue
    else:
        continue


#raw_path = '/projects/scc/UGOE/UPFB/UPP2/scc_ugoe_upfb_frey/dir.project/tb_data/TB2025/desy-tb-2025/data/dut/module_0/charge_calibrated'
#for runNmbr in not_calibrated_runs:
#    available_run_files = glob(f"{available_path}/*runNmbr*scan_interpreted.h5")
#    print(available_run_files)