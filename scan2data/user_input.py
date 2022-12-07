# -*- coding: utf-8 -*-
"""
Interact with user input through command line

"""
import glob
import process_directory
import sys

import warnings
warnings.filterwarnings('ignore')


def main():
    processAllSubdirectories = True #will not pass to process-extract-management
    master_dir = sys.argv[1] #01_intake/
    dir_csv_output = sys.argv[2] #05_result/
    regex_raw = '*.png'

    if processAllSubdirectories:
        list_all_subdir = glob.glob(master_dir + 'R*/[0-9]*/')
        for sample_subdir in list_all_subdir:
            sample_subdir = sample_subdir.replace('/', '\\')
            sample_subdir = sample_subdir.replace('\\', '/')
            process_directory.process_extract_management(dir_csv_output, master_dir, regex_raw, sample_subdir)

    else:
        sample_subdir = '/Users/Roksana/Desktop/Data Source/R014207938/907A/'  # input('Enter the name of the subdirectory ex: E:/master/R014207968/1246-5A/: ')
        process_directory.process_extract_management(dir_csv_output,
                                                     master_dir,
                                                     regex_raw,
                                                     sample_subdir,
                                                     desire_pickle,
                                                     desire_only_leftside)
if __name__ == "__main__":
        main()
            