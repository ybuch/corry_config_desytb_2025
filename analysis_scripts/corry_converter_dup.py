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
def process_rows(data, trigger_number, timestamp_first, trigger_extension):
    # First, count how many rows will be produced
    output_count = 0
    for i in range(data.shape[0]):
        col = data[i, 0]
        if col < 512:
            output_count += 1

    processed_data = np.empty((output_count*2, 5), dtype=np.int64)

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

            charge = (te - le) % 128
            timestamp = timestamp - timestamp_first

            processed_data[j, 0] = col
            processed_data[j, 1] = row
            processed_data[j, 2] = charge
            processed_data[j, 3] = 0 #timestamp
            processed_data[j, 4] = trigger_number
            j += 1

            processed_data[j, 0] = col
            processed_data[j, 1] = row
            processed_data[j, 2] = charge
            processed_data[j, 3] = 0 #timestamp
            processed_data[j, 4] = trigger_number - 1
            j += 1

    return processed_data[:j, :], trigger_number, timestamp_first, trigger_extension


def build_table_in_chunks(file, chunk_size=1000000):
    file_name = file.rsplit("/")[-1]
    file_name = file_name.rsplit("_")[0] + "_converted.h5"
    file_corry = file.rsplit("run")[0] + file_name
    #file_corry = file.rsplit("_interpreted.h5")[0] + "_corry.h5"

    if os.path.exists(file_corry):
        os.remove(file_corry)
    destination_file = file_corry

    # Prepare output file
    with tables.open_file(destination_file, mode="w") as dst:
        class ProcessedTable(tables.IsDescription):
            column = tables.Int32Col(pos=0)
            row = tables.Int32Col(pos=1)
            charge = tables.Int32Col(pos=2)
            timestamp = tables.UInt64Col(pos=3)
            trigger_number = tables.UInt32Col(pos=4)

        result_table = dst.create_table(dst.root, 'Dut', ProcessedTable, "Processed Data")

        # Initial states
        trigger_number = 0
        timestamp_first = 0
        trigger_extension = 0

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
                    plain_data, trigger_number, timestamp_first, trigger_extension
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
                    row_out['charge'] = processed_row[2]
                    row_out['timestamp'] = processed_row[3]
                    row_out['trigger_number'] = processed_row[4]
                    row_out.append()

                result_table.flush()
                start = end

    print(f"Processed data saved to {destination_file} as 'Dut'.")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert hit table to be compatible with corryvreckan EventLoaderHDF5.")
    parser.add_argument("--path", type=str, help="Path to a directory containing input files (HDF5 files).")
    parser.add_argument("--force", action="store_true", help="Force interpretation and conversion of already existing files.")

    args = parser.parse_args()

    directory = "/media/testbeam1/tb2025c/tb2025d/desy-tb-2025/data/dut/module_0/chip_0/"

    run_re = re.compile(r'run(\d+)_')  # Regular expression to extract run numbers from filenames
    input_path = directory
    if args.path:
        input_path = os.path(args.path)

    pattern = '*ext_trigger_scan.h5'

    # List to store matching filenames
    raw_files = []

    # Loop through the files in the directory
    for filename in os.listdir(directory):
        # Check if it's a file and matches the pattern
        if os.path.isfile(os.path.join(directory, filename)) and fnmatch.fnmatch(filename, pattern):
            raw_files.append(filename)


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
        not_converted_runs = list(set(raw_runs) - set(converted_runs))
    else:
        not_converted_runs = list(raw_runs)
    input_files = [raw_dict[run] for run in not_converted_runs]

    for input_file in input_files:
        total_file = directory + input_file
        res = analyze(total_file)
        res = build_table_in_chunks(res)




