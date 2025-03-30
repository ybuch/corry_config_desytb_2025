#!/bin/bash

mask_file="<name_of_default_mask>" #depends on geo_id
RAW_DIR="./yaml_files"


for RUN_NUMBER in <enter_run_numbers>
do
    cp ./default/$mask_file .
    mv $mask_file mask_run${RUN_NUMBER}.txt
    yaml_file=`ls $RAW_DIR/*$RUN_NUMBER*`
    echo "Found yaml file: $yaml_file"
    python3 ./extract_masked_pixels.py $yaml_file >> mask_run${RUN_NUMBER}.txt
    echo "Mask $RUN_NUMBER created"
    mv mask_run${RUN_NUMBER}.txt ./applied_masks
done

echo "done"
