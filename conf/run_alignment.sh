#!/bin/bash

#Reads runnumber and geo ID from CSV file
while IFS=, read -r RUN_NUMBER GEO_ID; do


RAW_DIR="<path_to_data>"
ROOT_DIR="../output"
CORRY_CONFIG="./align_dut_mpx2.conf"

echo "Starting Run $RUN_NUMBER"

FILE_TEL=`ls $RAW_DIR/telescope_run$RUN_NUMBER*`
FILE_MPX=`ls $RAW_DIR/mpx2_run$RUN_NUMBER*`


echo "Found TEL RAW file: $FILE_TEL"
echo "Found MPX2 RAW file: $FILE_MPX"

ROOT_FILE="dut_align/dut_align_run_$RUN_NUMBER.root"
LOG_FILE="logs/dut_align_run_$RUN_NUMBER.log"
echo "Output root file: $ROOT_FILE"


corry -c $CORRY_CONFIG \
-o detectors_file="../geo/full_aligned/geo_id${GEO_ID}_full_aligned.geo" \
-o detectors_file_updated="../geo/temp/dut_align_run_$RUN_NUMBER.geo" \
-o histogram_file="$ROOT_FILE" \
-o output_directory="$ROOT_DIR" \
-o EventLoaderEUDAQ2:MIMOSA26_0.file_name=\"$FILE_TEL\" \
-o EventLoaderEUDAQ2:MIMOSA26_1.file_name=\"$FILE_TEL\" \
-o EventLoaderEUDAQ2:MIMOSA26_2.file_name=\"$FILE_TEL\" \
-o EventLoaderEUDAQ2:MIMOSA26_3.file_name=\"$FILE_TEL\" \
-o EventLoaderEUDAQ2:MIMOSA26_4.file_name=\"$FILE_TEL\" \
-o EventLoaderEUDAQ2:MIMOSA26_5.file_name=\"$FILE_TEL\" \
-o EventLoaderEUDAQ2:Monopix2_0.file_name=\"$FILE_MPX\" 


sed -i "42i\mask_file = "<abs_path_to_masks_you_want_to_use>/mask_run$RUN_NUMBER.txt"" ../geo/temp/dut_align_run_$RUN_NUMBER.geo


done < W08R06_p.csv	#input list

