# -*- coding: utf-8 -*-
"""
This script converts .bin file data into a Sequence Radar data cubes in the format of numpy array
The output numpy array is of the shape = [Number_of_frames x Number_of_Virtual_Antenna x Number_of_adc_sample_per_chirp x Number_of_chirps]
can be called using the format "python bin_reader --input_path=<Path to .bin file> --json_path=<Path to JSON file containing params> --save_path=<Path to save the npy format of data to>"

@author: Somanshu
"""
import argparse
import json
import numpy as np


def parse_args():
    """
    Parses and returns a namespace object containing the command line arguments
    """
    parser = argparse.ArgumentParser(description='Getting file paths.')
    parser.add_argument('-i','--input_path', type=str, required=True ,help='Path for the .bin file')
    parser.add_argument('-j','--json_path', type=str, required=True ,help='Path for the .json file which contains information about the parameters of RADAR')
    parser.add_argument('-s','--save_path', type=str, required=True ,help='Path to save the output data file')
    args = parser.parse_args()
    return args

def getparams(json_file_path):
    """
    Input: Path of the json file which stores the parameters.
    Output: Returns all the Radar parameters required for reading .bin file.
    """
    file = open(json_file_path)
    file = json.load(file)
    num_of_frames= file["Number of frames"]
    num_of_chirp_per_frame= file["Number of chirps per frame"]
    num_adc_sample_per_chirp= file["Number of ADC samples per chirp"]
    num_range_bin= file["Number of range bins"]
    num_virtual_antennas= file["Number of virtual antenna"]
    chirp_config_per_chirp= file["ChirpConfigs per chirp"]
    num_real_channel= file["Number of real channels "]
    total_sample_per_frame = num_real_channel*num_adc_sample_per_chirp*chirp_config_per_chirp*num_of_chirp_per_frame
    return num_of_frames, num_of_chirp_per_frame, num_adc_sample_per_chirp, num_range_bin, num_virtual_antennas, chirp_config_per_chirp, num_real_channel, total_sample_per_frame
    

def read_bin_file (path, num_of_frames, num_of_chirp_per_frame, num_adc_sample_per_chirp, num_range_bin, num_virtual_antennas, chirp_config_per_chirp, num_real_channel, total_sample_per_frame ) :
    """
    Given all the RADAR parameters and the path of the input .bin file returns the data in numpy format
    """
    data_file = np.fromfile(path , dtype=np.int16)
    data = data_file.reshape (num_of_frames ,(total_sample_per_frame//4) ,4)
    rearrange_data = np.copy(data)
    
    #convert the data to Rx0I0 , Rx0Q0 , Rx0I1 , Rx0Q1 , . . .
    rearrange_data [ : , : , 2 ] = data [ : , : , 1 ]
    rearrange_data [ : , : , 1 ] = data [ : , : , 2 ]
    del(data)
    rearrange_data = rearrange_data.reshape(num_of_frames, 2*num_adc_sample_per_chirp, (num_real_channel//2) * chirp_config_per_chirp, num_of_chirp_per_frame)
    rearrange_data = np.swapaxes(rearrange_data , 1 , 3 )
    
    #Convert to Complex no
    radar_data_real = rearrange_data [ : , : : 2 , : , : ]
    radar_data_imag = rearrange_data [ : , 1 : : 2 , : , : ]
    radar_data = 1j*radar_data_imag
    radar_data += radar_data_real
    radar_data = np.moveaxis (radar_data , [0,1,2,3] , [0,2,1,3] )
    return radar_data

if __name__ == "__main__":
    args = parse_args()
    inp_file_path = args.input_path
    json_file_path = args.json_path
    num_of_frames, num_of_chirp_per_frame, num_adc_sample_per_chirp, num_range_bin, num_virtual_antennas, chirp_config_per_chirp, num_real_channel, total_sample_per_frame = getparams(json_file_path)
    data_in_np = read_bin_file(inp_file_path, num_of_frames, num_of_chirp_per_frame, num_adc_sample_per_chirp, num_range_bin, num_virtual_antennas, chirp_config_per_chirp, num_real_channel, total_sample_per_frame)
    np.save(args.save_path, data_in_np)