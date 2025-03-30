#!/usr/bin/env python
# coding: utf-8

#Usage: define path to maskfiles and reference files.
#A csv with in the form
#[fraction of masked pixels, #masked pixels, #pixels in area, #pixels masked by corry]
#will be produced


import numpy as np
import re
import glob
import csv
import os


# Use glob to find all files matching the pattern 'mask*.txt'
# In case no defaut masks are available, use same path as for  mask_files
mask_files = glob.glob('<path_to_masks_after_corry>/mask*.txt')
mask_files_default = glob.glob('<path_to_masks_before_corry>/mask*.txt')
output_file = './data_masks.csv'

mask_files.sort()
mask_files_default.sort()


#takes the path of a mask file and returns [fraction of masked pixels, #masked pixels, #pixels in area]
def mask_calculator(mask_file):   
    col_mask = []
    row_mask = []
    pixel_mask = []
    pixel_mask_counter = 0
    total_pixels = 0
    
    #reads masked colums, rows and pixels from file
    f = open(mask_file, "r")
    for x in f:
        if x[0] == 'c':
            col_mask.append(int(x.split(' ')[1]))
        if x[0] == 'r':
            row_mask.append(int(x.split(' ')[1]))
        if x[0] == 'p':
            pixel_mask.append([int(x.split(' ')[1]),int(x.split(' ')[2])])    
    f.close() 
    
    #remove dublicates
    col_mask = list(set(col_mask))
    row_mask = list(set(row_mask))

    #counts masked pixels in roi (not masked region)
    for element in pixel_mask:
        if element[0] not in col_mask and element[1] not in row_mask:
            pixel_mask_counter += 1
            
    #calculate total amount of pixels in roi            
    total_pixels = (512-len(col_mask))*(512-len(row_mask))
    result = [(pixel_mask_counter/total_pixels)*100,pixel_mask_counter,total_pixels]

    return(result)


#Function to calculate difference between amount of single masked pixels between two maskfiles 
def new_masking(mask_new, mask_old):
    pixel_mask_new = []
    pixel_mask_old = []

    #read in lines starting with p
    f = open(mask_new, "r")
    for x in f:
        if x[0] == 'p':
            pixel_mask_new.append([int(x.split(' ')[1]),int(x.split(' ')[2])])    
    f.close()
    f = open(mask_old, "r")
    for x in f:
        if x[0] == 'p':
            pixel_mask_old.append([int(x.split(' ')[1]),int(x.split(' ')[2])])    
    f.close

    #return difference of length
    return (len(pixel_mask_new)-len(pixel_mask_old))



if __name__ == "__main__":

    #remove existing csv
    if os.path.exists(output_file):
        os.remove(output_file)

    #write header
    with open(output_file, 'a') as table: 
        writer = csv.writer(table, delimiter=',')
        output_data = ["Run Number","Fraction of masked pixels", "Masked pixels", "Pixels in roi", "pixels masked by corry"]
        writer.writerow(output_data)
        table.close()
        

    for file in mask_files:
        #extract run number from file name
        match = re.search(r'mask_run(\d+)', file)
        runNmb = int(match.group(1))
        
        #search for matching file in mask_files_default (needed for 'new_masking()')
        for ref_file in mask_files_default:
            ref = re.search(r'mask_run(\d+)', ref_file)
            runNumb_ref = int(ref.group(1))
            if runNumb_ref == runNmb:
                comparison_mask = ref_file
                break
        #generate output and write to csv
        if match:
            output = mask_calculator(file)
            corry_masking = new_masking(file,comparison_mask)
            with open(output_file, 'a') as table:     #write result to csv file
                writer = csv.writer(table, delimiter=',')
                output_data = [runNmb,output[0],output[1],output[2],corry_masking]
                writer.writerow(output_data)
                table.close()





