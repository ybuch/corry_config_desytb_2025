import os.path as path
import os
import numpy as np
from tjmonopix2.analysis import analysis
import tables
from numba import njit
import argparse
import re
import fnmatch


file_name = "/media/testbeam1/tb2025c/tb2025d/desy-tb-2025/data/dut/module_0/chip_0/run001685_20250403_023617_ext_trigger_scan.h5"


# Author: Maximilian Babeluk, last modified by Guglielmo Benfratello
# Quick and dirty converter script to create h5 files to load into corry via the hdf5 loader
# Only intentended for testing, data duplication similar to what is done in the eudaq producer

# Should give the same results as the .raw files, needs a trigger shift of 1


def analyze(file):
    if '_interpreted' in file:
        print('Skipping analysis: already done')
        return file

    file_interpreted = file.rsplit(".h5")[0] + "_interpreted.h5"

    if os.path.exists(file_interpreted):
        print('Skipping analysis: already done')
        return file_interpreted

    print('Analyzing file: ' + path.basename(file))
    with analysis.Analysis(raw_data_file=file, cluster_hits=False, analyzed_data_file=file_interpreted) as a:
        a.analyze_data()

    return file_interpreted

@njit
def inv_tot_response_func(tot, a, b, d):
    return (np.sqrt(b**2 * (a - tot)**2 + 2 * b * d * (a + tot) + d**2) - b * a + b * tot + d) * 0.5


@njit
def process_rows(data, trigger_number, timestamp_first, trigger_extension, calib_plain):
    # First, count how many rows will be produced
    output_count = 0
    for i in range(data.shape[0]):
        col = data[i, 0]
        if col < 512:
            output_count += 1

    processed_data = np.empty((output_count*2, 6), dtype=np.int64)

    j = 0
    trigger_number_last = 0
    for i in range(data.shape[0]):
        col = data[i, 0]  # col or 1022 for TLU
        row = data[i, 1]
        le = int(data[i, 2])
        te = int(data[i, 3])
        token_id = data[i, 4]
        timestamp = data[i, 5]

        if col == 1023:
            trigger_number_new = int(token_id)
            if ((trigger_number_new + trigger_extension) < trigger_number):
                trigger_extension += 0x8000
            if ((trigger_number_new + trigger_extension) < trigger_number):
                print(f"Overflow: {trigger_number_new + trigger_extension} {trigger_number}")
            trigger_number_last = trigger_number
            trigger_number = trigger_number_new + trigger_extension

        timestamp = timestamp * 25   # 40 MHz to 25 ns steps

        if col < 512 and trigger_number != 0:
            if timestamp_first == 0:
                timestamp_first = timestamp

            raw = (te - le) % 128
            charge = ELECTRON_CONVERSION * inv_tot_response_func(
                        raw,
                        calib_plain[col, row, 0],
                        calib_plain[col, row, 1],
                        calib_plain[col, row, 2],
                    )
            timestamp = timestamp - timestamp_first

            processed_data[j, 0] = col
            processed_data[j, 1] = row
            processed_data[j, 2] = raw
            processed_data[j, 3] = 0 #timestamp
            processed_data[j, 4] = trigger_number
            processed_data[j, 5] = charge
            j += 1

            processed_data[j, 0] = col
            processed_data[j, 1] = row
            processed_data[j, 2] = raw
            processed_data[j, 3] = 0 #timestamp
            processed_data[j, 4] = trigger_number - 1
            processed_data[j, 5] = charge
            j += 1

    return processed_data[:j, :], trigger_number, timestamp_first, trigger_extension


def build_table_in_chunks(file, tot_calib_file, chunk_size=1000000):
    file_name = file.rsplit("/")[-1]
    file_name = file_name.rsplit("_")[0] + "_converted.h5"
    file_corry = file.rsplit("run")[0] + file_name
    #file_corry = file.rsplit("_interpreted.h5")[0] + "_corry.h5"

    with tables.open_file(tot_calib_file, "r") as calib_file:
        calib_data = calib_file.root.InjTotCalibration[:]
 
    if os.path.exists(file_corry):
        os.remove(file_corry)
    destination_file = file_corry

    # Prepare output file
    with tables.open_file(destination_file, mode="w") as dst:
        class ProcessedTable(tables.IsDescription):
            column = tables.Int32Col(pos=0)
            row = tables.Int32Col(pos=1)
            raw = tables.Int32Col(pos=2)
            timestamp = tables.UInt64Col(pos=3)
            trigger_number = tables.UInt32Col(pos=4)
            charge = tables.UInt32Col(pos=5)

        result_table = dst.create_table(dst.root, 'Dut', ProcessedTable, "Processed Data")

        # Initial states
        trigger_number = 0
        timestamp_first = 0
        trigger_extension = 0

        calib_plain = np.array((calib_data[:,:]))

        # Process in chunks
        with tables.open_file(file, mode="r") as src:
            table = src.get_node('/Dut')
            total_rows = table.nrows
            start = 0

            while start < total_rows:
                end = min(start + chunk_size, total_rows)
                data_chunk = table.read(start, end)

                # Convert chunk to plain numpy for Numba
                plain_data = np.column_stack((data_chunk['col'], 
                                              data_chunk['row'], 
                                              data_chunk['le'], 
                                              data_chunk['te'], 
                                              data_chunk['token_id'], 
                                              data_chunk['timestamp']))

                processed_data, trigger_number, timestamp_first, trigger_extension = process_rows(
                    plain_data, trigger_number, timestamp_first, trigger_extension, calib_plain
                )

                
                # Get the indices that would sort the array by the specified column
                sorted_indices = np.argsort(processed_data[:, 4])

                # Use these indices to reorder 'a'
                a_sorted = processed_data[sorted_indices]

                # Write this chunk's processed data to file
                for processed_row in a_sorted:
                    row_out = result_table.row
                    row_out['column'] = processed_row[0]
                    row_out['row'] = processed_row[1]
                    row_out['raw'] = processed_row[2]
                    row_out['timestamp'] = processed_row[3]
                    row_out['trigger_number'] = processed_row[4]
                    row_out['charge'] = processed_row[5]
                    row_out.append()

                result_table.flush()
                start = end

    print(f"Processed data saved to {destination_file} as 'Dut'.")



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Conversion script for ToT to electrons of h5.')
    
    parser.add_argument('--input_file', type=str, help='input file')
    parser.add_argument('--trigger_mode', type=str, help='Trigger mode. aida or eudet')
    parser.add_argument('--tot_calib_file', type=str, help='Calibration file')
    parser.add_argument('--conversion_factor', type=str, help='conversion_factor for hvc (18) or dcc (9)')

    args = parser.parse_args()
    #input_file = "/projects/scc/UGOE/UPFB/UPP2/scc_ugoe_upfb_frey/dir.project/tb_data/TB2025/desy-tb-2025/data/dut/module_0/charge_calibrated/run002094_20250412_101501_ext_trigger_scan_interpreted.h5"
    #trigger_mode = "aida"
    #tot_calib_file = '/projects/scc/UGOE/UPFB/UPP2/scc_ugoe_upfb_frey/dir.project/tb_data/TB2025/desy-tb-2025/ToT_TB2025_runs/run002094_20250701_122526_threshold_scan_interpreted_tot_calibration_fit3par_charge_mean.h5'
    ELECTRON_CONVERSION = float(args.conversion_factor)

    input_file = args.input_file
    trigger_mode = args.trigger_mode
    tot_calib_file = args.tot_calib_file

    if trigger_mode !='eudet':
        raise RuntimeError('Use this for eudet only')

    print('Input file: ', input_file,'\n','Calib file: ', tot_calib_file)
    res = analyze(input_file)
    res = build_table_in_chunks(res,tot_calib_file)
    '''
    parser = argparse.ArgumentParser(description="Convert hit table to be compatible with corryvreckan EventLoaderHDF5.")
    parser.add_argument("--path", type=str, help="Path to a directory containing input files (HDF5 files).")
    parser.add_argument("--force", action="store_true", help="Force interpretation and conversion of already existing files.")
    parser.add_argument("--tot_calib_path", type=str, help="Path to a directory containing calibration files.")
    parser.add_argument("--frontend", type=str, help="Frontend. HVC or DCC.")

    args = parser.parse_args()

    #directory = "/media/testbeam1/tb2025c/tb2025d/desy-tb-2025/data/dut/module_0/chip_0/"
    directory = '/projects/scc/UGOE/UPFB/UPP2/scc_ugoe_upfb_frey/dir.project/tb_data/TB2025/desy-tb-2025/data/dut/module_0/charge_calibrated/'
    calib_directory = '/projects/scc/UGOE/UPFB/UPP2/scc_ugoe_upfb_frey/dir.project/tb_data/TB2025/desy-tb-2025/ToT_TB2025_runs/'
    
    run_re = re.compile(r'run(\d+)_')  # Regular expression to extract run numbers from filenames
    input_path = directory
    
    if args.frontend == 'HVC':
        ELECTRON_CONVERSION = 18
    elif args.frontend == 'DCC':
        ELECTRON_CONVERSION = 9
    else:
        raise RuntimeError('frontend unspecified or not DCC or HVC')
    
    if args.path:
        input_path = os.path(args.path)
    
    calib_path = calib_directory
    if args.tot_calib_path:
        calib_path = os.path(args.tot_calib_path)
    
    pattern = '*ext_trigger_scan.h5'

    # List to store matching filenames
    raw_files = []

    # Loop through the files in the directory
    for filename in os.listdir(directory):
        # Check if it's a file and matches the pattern
        if os.path.isfile(os.path.join(directory, filename)) and fnmatch.fnmatch(filename, pattern):
            raw_files.append(filename)

    pattern_calib = '*tot_calibration_fit3par_charge_mean.h5'

    calib_files = []
    # Loop through the files in the directory
    for filename in os.listdir(calib_path):
        # Check if it's a file and matches the pattern
        if os.path.isfile(os.path.join(calib_path, filename)) and fnmatch.fnmatch(filename, pattern_calib):
            calib_files.append(filename)

    # Collect raw HDF5 files that match the naming pattern
    raw_dict = {}
    raw_runs = []

    # print('got ', list(raw_files), '\n\n')    
    for file in raw_files:     
        run_number_match = run_re.search(os.path.splitext(os.path.basename(file))[0])
        if run_number_match:
            run_number = run_number_match.group(1)
            raw_dict[run_number] = file
            raw_runs.append(run_number)

    calib_dict = {}
    calib_runs = []

    for file in calib_files:     
        run_number_match = run_re.search(os.path.splitext(os.path.basename(file))[0])
        if run_number_match:
            run_number = run_number_match.group(1)
            calib_dict[run_number] = calib_directory+file
            calib_runs.append(run_number)

    # Collect interpreted and converted files for comparison
    converted_pattern = "*_converted.h5"
    converted_files = []
    for filename in os.listdir(directory):
        # Check if it's a file and matches the pattern
        if os.path.isfile(os.path.join(directory, filename)) and fnmatch.fnmatch(filename, converted_pattern):
            converted_files.append(filename)

    converted_runs = [run_re.search(os.path.splitext(os.path.basename(file))[0]).group(1) for file in converted_files if run_re.search(os.path.splitext(os.path.basename(file))[0])]

    # Determine raw files that have not yet been converted
    if not args.force:
        not_converted_runs = list(set(calib_runs) - set(converted_runs))
    else:
        not_converted_runs = list(calib_runs)
    
    not_converted_runs_eudet = []
    for run in not_converted_runs:
        if int(run) < 1863:
            not_converted_runs_eudet.append(run)

    not_converted_runs_eudet = sorted(not_converted_runs_eudet)
    
    input_files = [[raw_dict[run] for run in not_converted_runs_eudet][0]]

    #for run in calib_dict.keys():
    #    print(run,' : ', calib_dict[run])

    #for run in raw_dict.keys():
    #    print(run,' : ', raw_dict[run])

    #print(not_converted_runs_eudet)
    for input_file in input_files:
        total_file = directory + input_file
        print('!!!!!!!!', total_file)
        res = analyze(total_file)
        res = build_table_in_chunks(res)
    '''



