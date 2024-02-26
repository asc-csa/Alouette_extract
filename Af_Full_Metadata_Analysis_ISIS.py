
#ISIS Full MetaData Analysis - Jeyshinee Pyneeandee February 2024

#Required imports 
import pandas as pd
import os
from random import randrange
import time
from datetime import datetime
import gc
import warnings
warnings.filterwarnings('ignore')
import keras_ocr
from optparse import OptionParser
from random import randrange

from Ag_Keras_Ocr import *

#To run this script : e.g Af_Full_Metadata_Analysis_ISIS.py --username jpyneeandee --isis 1 (for ISIS batch 1 run by Jeyshinee)
#Script defaults to ISIS Batch 1 

pipeline = keras_ocr.pipeline.Pipeline()
parser = OptionParser()

parser.add_option('-u', '--username', dest='username', 
        default='jpyneeandee', type='str', 
        help='CSA Network username, default=%default.')

parser.add_option('--isis', dest='isis', 
        default='1', type='str', 
        help='ISIS batch, default=%default.')

(options, args) = parser.parse_args()

        
if options.isis == '2':
     #ISIS BATCH 2 CHOSEN
     directory_path = 'L:/DATA/ISIS/ISIS_102000056114/'
     batch_size = 801

    #Log Directory, do not change
     logDir = 'L:/DATA/ISIS/ISIS_Test_Metadata_Analysis/BATCH_2/04_log/'
     #Path to save results, do not change
     resultDir = 'L:/DATA/ISIS/ISIS_Test_Metadata_Analysis/BATCH_2/05_results/'
     my_path = logDir + 'ISIS_2_Directory_Subdirectory_List.csv'

elif options.isis == '3':
     #ISIS BATCH 3/RAW UPLOAD CHOSEN
     directory_path = 'L:/DATA/ISIS/raw_upload_20230421/'
     batch_size = 359

    #Log Directory, do not change
     logDir = 'L:/DATA/ISIS/ISIS_Test_Metadata_Analysis/BATCH_3/04_log/'
     #Path to save results, do not change
     resultDir = 'L:/DATA/ISIS/ISIS_Test_Metadata_Analysis/BATCH_3/05_results/'
     my_path = logDir + 'ISIS_Raw_Upload_Directory_Subdirectory_List.csv'

else:
     #ISIS BATCH 1 
     directory_path = 'L:/DATA/ISIS/ISIS_101300030772/'
     batch_size = 1720

    #Log Directory, do not change
     logDir = 'L:/DATA/ISIS/ISIS_Test_Metadata_Analysis/BATCH_1/04_log/'
     #Path to save results, do not change
     resultDir = 'L:/DATA/ISIS/ISIS_Test_Metadata_Analysis/BATCH_1/05_results/'
     my_path = logDir + 'ISIS_1_Directory_Subdirectory_List.csv'

#station names and location 
station_log_dir = 'L:/DATA/ISIS/ISIS_Test_Metadata_Analysis/Station_Number_Name_Location.csv'
station_df = pd.read_csv(station_log_dir)
     
#Functions

def read_metadata(prediction_groups, subdir_path, img):
    '''
    Definition:
        This function reads the prediction groups produced by KERAS OCR and separates the metadata strings 
        into their appropriate tags
    Arguments:
        prediction_groups: KERAS OCR output predictions
        subdir_path: Directory + subdirectory path to image
        img: Image being processed 
    Returns:
        Two dataframes of processed metadata and loss images (metadata that have less than 15 characters)
    '''
    #get metadata from keras prediction & concat string
    df_read_temp = pd.DataFrame()
    df_notread_temp = pd.DataFrame()
    for i in range(0, len(prediction_groups)):
        df_ocr = pd.DataFrame()
        predicted_image = prediction_groups[i]
        if len(predicted_image) > 0:
            for text, box in predicted_image:
                row = pd.DataFrame({
                    'number': text,
                    'x': box[1][0],
                    'y': box[1][1]
                }, index=[0])
                df_ocr = pd.concat([df_ocr, row])
            df_ocr = df_ocr.sort_values('x').reset_index(drop=True)
        
            #String concatenate, get all metadata in one string
            read_str = ''
            for j in range(0, len(df_ocr)):
                read_str_ = df_ocr['number'].iloc[j]
                read_str += read_str_

            if len(read_str) == 15:
                    station_number = read_str[2:4]
                    station_location, station_lat, station_lon, station_ID = get_station_info(int(station_number))
                    row2 = pd.DataFrame({'Satellite_Code': read_str[0:1],
                                         'Fixed_Frequency_Code': read_str[1:2],
                                         'Station_Number': station_number,
                                         'Station_Location':station_location,
                                         'Station_ID':station_ID,
                                         'Station_Lat':station_lat,
                                         'Station_Lon':station_lon,
                                         'Year': read_str[4:6],
                                         'Day': read_str[6:9],
                                         'Hour': read_str[9:11],
                                         'Minute': read_str[11:13],
                                         'Second': read_str[13:15],
                                         'Filename': img.replace(subdir_path, '')
                                         }, index=[i])
                    df_read_temp = pd.concat([df_read, row2])
            else:
                    df_ocr['Filename'] = img.replace(subdir_path, '')
                    df_notread_temp = pd.concat([df_notread_temp, df_ocr])
        else:
                df_ocr['Filename'] = img.replace(subdir_path, '')
                df_notread_temp = pd.concat([df_notread_temp, df_ocr])
    
    return df_read_temp, df_notread_temp

def draw_random_subdir():
    '''
    Definition: Draw a directory and subdirectory, that is not currently in progress or has already been processed and updates the status
    of that row 
      
    Arguments: None

    Returns: A directory, subdirectory and the row number at which these are found 
        
    '''
    if os.path.exists(my_path):
            try:
                full_dir_df = pd.read_csv(my_path)
                ind = randrange(len(full_dir_df))
            #   for ind in full_dir_df.index: #instead of a for loop, i'm trying a randomized ind
                directory = full_dir_df['Directory'][ind]
                subdir = full_dir_df['Subdirectory'][ind]

                if (full_dir_df['Status'][ind]) == "Not Processed":
                    full_dir_df.loc[ind, "Status"] = "In Progress"
                    full_dir_df.to_csv(my_path, index=False)
                    return directory, subdir, ind

                elif (full_dir_df['Status'][ind]) == "In Progress":
                    print('Current subdirectory', subdir, 'being processed already, moving on to the next one')
                    draw_random_subdir()
                    
                elif (full_dir_df['Status'][ind]) == "Processed":
                    print("Current subdirectory", subdir, "already processed, moving on to the next one")
                    draw_random_subdir()

            except (OSError, PermissionError) as e:
                print(my_path, 'currently being used, pausing for 30 seconds before another attempt')
                time.sleep(30)

                
def update_my_log_file(ind):
    '''
    Definition: Updates the status of the given index row for dir and subdir as "Processed"
      
    Arguments:
        ind: Index row for processed directory and subdirectory

    Returns: None
        
    '''
    if os.path.exists(my_path):
        try:
            full_dir_df = pd.read_csv(my_path)
            
            if (full_dir_df['Status'][ind]) == "In Progress":
                    full_dir_df.loc[ind, "Status"]= "Processed"
                    full_dir_df.to_csv(my_path, index=False)
            else:
                print("Error with this path - check if dir and subdir at row", str(ind), "has been processed")
                 
        except (OSError, PermissionError) as e:
                print(my_path, 'currently being used, pausing for 30 seconds before another attempt')
                time.sleep(30)


def get_station_info(ind):
    '''
    Definition: This function takes in a station number (read from an ionogram), cross references it with 
    a station information csv and returns the station location, ID, Latitude and Longitude 
 
    Arguments:
        ind: int corresponding to station number 

    Returns: 4 strings corresponding to the location, latitude, longitiude and ID of the given station number 

    '''
    for i in station_df:
        if station_df['Number'][i] == ind:
            station_location = station_df['Location'][i]
            station_lat =  station_df['Latitude'][i]
            station_lon = station_df['Longitude'][i]
            station_ID =  station_df['Station ID'][i]
        
    return station_location, station_lat, station_lon, station_ID
                
#Process remaining subdirectories with while loop
stop_condition = False

while stop_condition == False:
    start = time.time()
    
    #Get number of processed subdirs 
    if os.path.exists(logDir + 'Process_Log.csv'):
        try:
            my_log_file = pd.read_csv(logDir + 'Process_Log.csv')
            subdirs_processed = len(my_log_file['Subdirectory'].drop_duplicates())
            dirs_processed = len(my_log_file['Directory'].drop_duplicates())

        except (OSError, PermissionError) as e:
            print(logDir + 'Process_Log_OCR.csv', 'currently being used, pausing for 30 seconds before another attempt')
            time.sleep(30)

        #get remaining subdirs        
        subdir_rem = batch_size - subdirs_processed

        #Check stop conditions
        if subdir_rem < 2:
            print('Stop!')
            stop_condition = True

    #Process subdirectory
    print('')
    print('Processing ' + subdir_path_end + ' subdirectory')
    print(str(subdir_rem) + ' subdirectories to go!')

    #Get directory and subdirectory path to process and current row index
    directory, subdirectory, curr_row_index = draw_random_subdir()
    subdir_path_end = directory + '/' + subdirectory + '/'

    #Get all images from chosen directory and subdirectory path
    img_fns = []
    for file in os.listdir(directory_path + subdir_path_end):
        img_fns.append(directory_path + subdir_path_end + file)
        num_images = len(img_fns)

    df_read = pd.DataFrame()
    df_notread = pd.DataFrame()

    for img in img_fns:
        prediction_groups = read_image(img) 
        df_read_, df_notread_ = read_metadata(prediction_groups=prediction_groups, subdir_path=directory_path + subdir_path_end,
                                                       img=img)
        df_read = pd.concat([df_read, df_read_])
        df_notread = pd.concat([df_notread, df_notread_])
        
    #Saving results:
    my_temp_path = resultDir + directory
    if not os.path.notexists(my_temp_path):
        os.makedirs(resultDir,directory)
    
    df_read.to_csv(resultDir + directory + '/' +  'Metadata_analysis_' + subdirectory + '.csv', index=False)
    if len(df_notread) > 0:
        df_notread.to_csv(resultDir + directory + '/' +  'LOSS_Metadata_analysis_' + subdirectory + '.csv', index=False)

    print('Dir:', directory, 'Subdir:', subdirectory, "results saved to csv!")

    #update status for current path of dir and subdir
    update_my_log_file(curr_row_index)
    print("Status updated!")

    #Processing time for one subdirectory
    end = time.time()
    t = end - start
    print('Processing time for subdirectory: ' + str(round(t/60, 1)) + ' min')
    print('Processing rate: ' + str(round(t/len(img_fns), 2)) + ' s/img')
    print('')

    #Record performance
    df_result_ = pd.DataFrame({
        'Directory': directory,
        'Subdirectory': subdirectory,
        '# images' : num_images,
        'Process_time': t,
        'Process_timestamp': datetime.fromtimestamp(end),
        'User': options.username
    }, index=[0])

    if os.path.exists(logDir + 'Process_Log.csv'):
        df_log = pd.read_csv(logDir + 'Process_Log.csv')
        df_update = pd.concat([df_log, df_result_], axis=0, ignore_index=True)
        df_update.to_csv(logDir + 'Process_Log.csv', index=False)

    else:
        if len(df_result_) > 0:
            df_result_.to_csv(logDir + 'Process_Log_OCR.csv', index=False)
            
    #Backup 'process_log' (10% of the time), garbage collection
    if randrange(10) == 7:
        df_log = pd.read_csv(logDir + 'Process_Log_OCR.csv')
        datetime_str = datetime.now().strftime("%Y%m%d_%Hh%M")
        os.makedirs(logDir + 'backups/', exist_ok=True)
        df_log.to_csv(logDir + 'backups/' + 'process_log_OCR-' + datetime_str + '.csv', index=False)
        gc.collect()