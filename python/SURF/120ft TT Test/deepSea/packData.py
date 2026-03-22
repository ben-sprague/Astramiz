import os
import argparse

import numpy as np
import pandas as pd
import xarray as xr

import cv2

#Setup argument parser
parser = argparse.ArgumentParser()
#Data file paths
parser.add_argument('--input_dir', action="store", required=True, type=str, help="Directory with .nc files")

args = parser.parse_args()
input_path = args.input_dir

abs_path = os.path.abspath(__file__)
file_dir = os.path.dirname(abs_path)

df = pd.DataFrame(columns=['file_num','int_return', 'perst_return', 'difference'])
CHUNK_WIDTH = 30
CHUNK_HEIGHT = 500
CHUNK_DURATION = 1 #Seconds
data_chunks = np.ndarray(shape=(CHUNK_HEIGHT,CHUNK_WIDTH,0))
target_distances = np.ndarray(shape=(4,0))
if os.path.isdir(input_path := os.path.join(file_dir,args.input_dir)):
    files = os.listdir(input_path)
    files.sort()

    for index, file in enumerate(files):
        print(os.path.join(input_path, file))
        if file[0] != '.':
            #Open File
            ds = xr.open_dataset(os.path.join(input_path, file), decode_timedelta=True)
            fileName = file.split('.')[0]
            sonar_data = ds.sonar_return.T.to_numpy()
            los_data = ds.los.to_numpy()

            #Map target distance to 0-CHUNK_HEIGHT
            raw_target_distance = ds.attrs['target_distance']
            min_range = ds.range.min().item()
            max_range = ds.range.max().item()
            scaled_range = (raw_target_distance-min_range)/(max_range-min_range)
            working_ranges = np.array([scaled_range, raw_target_distance, min_range, max_range]).T
            #Get indicies of all transitions from True to False
            shifted_los_array = np.insert(los_data[:-1], 0, False)

            TF_transition_mask = ~los_data & shifted_los_array
            TF_transition_indicies = np.where(TF_transition_mask)[0]

            if not(los_data[0]):
                #If the dataset starts without a line of sight, treat first index as a transition
                TF_transition_indicies = np.insert(TF_transition_indicies, 0, 0)

            shifted_los_array[0] = True
            FT_transition_mask = los_data & ~shifted_los_array
            FT_transition_indicies = np.where(FT_transition_mask)[0]

            if not(los_data[-1]):
                #If the dataset ends without a line of sight, treat last index as a transition
                FT_transition_indicies = np.append(FT_transition_indicies, -1)

            

            #Calculate width of data to grab to form chunk
            test_duration = (ds.time[-1]-ds.time[0]).to_numpy().astype(np.float64)/1000
            sampling_rate = ds.attrs['num_samples']/test_duration
            step_size = int(CHUNK_DURATION*sampling_rate)

            for array_index, TF_transition_index in enumerate(TF_transition_indicies):
                FT_transition_index = FT_transition_indicies[array_index]
                for i in range (TF_transition_index, FT_transition_index, step_size):
                    if TF_transition_index+CHUNK_WIDTH<FT_transition_index:
                        #Full Chunk is possible
                        chunk_columns_end = i+CHUNK_WIDTH
                    else:
                        #Partial chunk needed
                        chunk_columns_end = FT_transition_index
                    raw_chunk = sonar_data[:,i:chunk_columns_end].astype(np.float32)
                    #Downscale height
                    scaled_chunk = cv2.resize(raw_chunk, (raw_chunk.shape[1], CHUNK_HEIGHT), interpolation=cv2.INTER_AREA)
                    #Check if upscaling or downscaling width
                    if raw_chunk.shape[0] > CHUNK_WIDTH:
                        #Downscaling, use inter area interpolation
                        scaled_chunk = cv2.resize(scaled_chunk, (CHUNK_WIDTH, CHUNK_HEIGHT), interpolation=cv2.INTER_AREA)
                    else:
                        #Upscaling, use inter cubic interpolation
                        scaled_chunk = cv2.resize(scaled_chunk, (CHUNK_WIDTH, CHUNK_HEIGHT), interpolation=cv2.INTER_CUBIC)

                    scaled_chunk = np.resize(scaled_chunk, (CHUNK_HEIGHT, CHUNK_WIDTH, 1))
                    data_chunks = np.append(data_chunks, scaled_chunk, axis=2)
                    target_distances = np.append(target_distances, np.reshape(working_ranges, (4,1)), axis=1)

#Training vs testing split
TRAINING_PERCENT = 0.8
num_training = int(data_chunks.shape[2]*TRAINING_PERCENT)
num_testing = data_chunks.shape[2]-num_training
training_indies = np.random.randint(0,data_chunks.shape[2],num_training)
testing_indies = np.setdiff1d(np.arange(data_chunks.shape[2]), training_indies)

np.save('fullSONARData', data_chunks.astype(np.float32))
np.save('trainingSONARData', data_chunks[:,:,training_indies].astype(np.float32))
np.save('testingSONARData', data_chunks[:,:,testing_indies].astype(np.float32))
np.save('fullRangeData', target_distances.astype(np.float32))
np.save('trainingRangeData', target_distances[:, training_indies].astype(np.float32))
np.save('testingRangeData', target_distances[:, testing_indies].astype(np.float32))
print(target_distances.shape)
            