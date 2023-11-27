# Ashley Ferreira, November 2023
# codes to work with contractor error report
# not super efficient, just quick and dirty to get the job done

import os 
import pandas as pd 

# if in L-drive or on GitHub then remove this
relative_path = '//SAQCJ3YWVDCP003.csa.space.gc.ca/L-DFS/DATA/ISIS/contractor_error_reports/'

def subdir_logs():
    '''
    create a log of all ISIS subdirs in our file system
    '''
    dirs = []
    subdirs = []

    # directory where most of data is
    main_dir = '//SAQCJ3YWVDCP003.csa.space.gc.ca/L-DFS/DATA/ISIS/ISIS_101300030772/'
    for box in os.listdir(main_dir):
        print('reading subdirs in', box)
        for subdir in os.listdir(main_dir + box):
            dirs.append(box)
            subdirs.append(subdir)

    # directory where a bit more data is
    secondary_dir = '//SAQCJ3YWVDCP003.csa.space.gc.ca/L-DFS/DATA/ISIS/raw_upload_20230421/'
    for roll in os.listdir(secondary_dir):
        print('reading subdirs in', roll)
        for subdir in os.listdir(secondary_dir + roll):
            dirs.append(roll)
            subdirs.append(subdir)

    # convert to a dataframe and save to a csv
    subdirs_df = pd.DataFrame()
    subdirs_df['current_dir'] = dirs
    subdirs_df['current_subdirs'] = subdirs 
    subdirs_df.to_csv(relative_path + 'current_subdirs.csv', index=False)

def compare_report():
    '''
    compare subdirs in the error reports (which seem to act as an inventory)  
    to those in our current file system using the outputs of subdir_logs()
    '''
    print('################\ncomparing file system subdirs to error report subdirs')

    # read in both error reports and save them to one combined error report
    report1_subdirs = pd.read_csv(relative_path + 'SpaceAgencyErrorReport1.csv', usecols=['Box::Box_Name','Roll_Name'])
    report2_subdirs = pd.read_csv(relative_path + 'SpaceAgencyErrorReport2.csv', usecols=['Box::Box_Name','Roll_Name'])
    report_combined_subdirs = pd.concat([report1_subdirs, report2_subdirs], join="outer")
    report_combined_subdirs.to_csv(relative_path + 'SpaceAgencyErrorReport_1and2.csv', index=False)

    print(f'report 1 subdirectories: {len(report1_subdirs)}')
    print(f'report 2 subdirectories: {len(report2_subdirs)}')
    print(f'report combined subdirectories: {len(report_combined_subdirs)}')

    # read in the list of subdirs in current file system
    current_subdirs = pd.read_csv(relative_path + 'current_subdirs.csv')
    print(f'current subdirectories: {len(current_subdirs)}') 

    # initialize list to indicate if subdir is in current file system
    in_current = []
    # loop over all subdirs in combined error report and if it also
    # appears in the current subdirs then append True, otherwise False
    for item in report_combined_subdirs['Roll_Name']: 
        if item in list(current_subdirs['current_subdirs']):
            in_current.append(True)
        else: 
            in_current.append(False)

    print(len(current_subdirs), 'in current file system')
    print(sum(in_current), 'in error reports AND in current file system')
    print(len(report_combined_subdirs['Roll_Name']) - sum(in_current), 'in error reports but NOT in current file system')

    # add a new column to the combined error report indicating if subdir is in current file syste
    report_combined_subdirs['in_current'] = in_current 
    # save the updated error report
    report_combined_subdirs.to_csv(relative_path + 'report_combined_analysis.csv', index=False)

    # same thing as previous loop but checking if all current subdirs are in error reports
    in_report = []
    for item in current_subdirs['current_subdirs']: 
        if item in list(report_combined_subdirs['Roll_Name']):
            in_report.append(True)
        else: 
            in_report.append(False)
    current_subdirs['in_report'] = in_report 
    current_subdirs.to_csv(relative_path + 'current_subdirs.csv', index=False)
    print(len(in_report) - sum(in_report), 'in file system but not in error reports')
   
if __name__ == '__main__':
    subdir_logs()
    compare_report()

# You can find the two main outputs in report_combined_analysis.csv and current_subdirs.csv
# I have done spot checks and the results so far seem correct. The printed stats are:
    # report 1 subdirectories: 1975
    # report 2 subdirectories: 845
    # report combined subdirectories: 2820
    # current subdirectories: 2066
    # 2066 in current file system
    # 2019 in error reports AND in current file system
    # 801 in error reports but NOT in current file system
    # 28 in file system but not in error reports --> some are box_29 related for sure
# We may want to add more info to these logs like associated rolls/boxes or which report subdir was from.