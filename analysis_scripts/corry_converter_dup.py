import os.path as path
import os
import numpy as np
from tjmonopix2.analysis import analysis
import tables
from numba import njit

file_name = "/home/mx/Daten/Schule/aktuell/Nosync/tj-monopix2-daq/tjmonopix2/scans/output_data/module_0/chip_0/20240719_210855_eudaq_scan.h5"


# Author: Maximilian Babeluk
# Quick and dirty converter script to create h5 files to load into corry via the hdf5 loader
# Only intentended for testing, data duplication similar to what is done in the eudaq producer

# Should give the same results as the .raw files, needs a trigger shift of 1


def analyze(file):
    if '_interpreted' in file:
        print('Skipping analysis: already done')
        return filetrigger_number

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
    file_corry = file.rsplit("_interpreted.h5")[0] + "_corry.h5"
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
    res = analyze(file_name)
    res = build_table_in_chunks(res)




