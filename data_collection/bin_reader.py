# -*- coding: utf-8 -*-
"""
This script converts .bin file data into a Sequence Radar data cubes in the format of numpy array
The output numpy array is of the shape = [Number_of_frames x Num of Rx x Number of chirps per frame x Number_of_adc_samples_per_chirp]
can be called using the format "python bin_reader --input_path=<Path to .bin file> --json_path=<Path to JSON file containing params> --save_path=<Path to save the npy format of data to>"

@author: Somanshu

Our raw data is collected using IWR6843 With DCA1000 [see: https://www.ti.com/lit/an/swra581b/swra581b.pdf?ts=1648804249448&ref_url=https%253A%252F%252Fwww.google.com%252F]
We assume complex data collection.
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
    
    Param Meaning:
        Num of Frames: Number of frames in the gesture
        Num of chirp per frame: Number of chirp in a single frame 
        Num adc sample per chirp: Number of ADC samples per chirp
        Num range bin: Equal to Num adc sample per chirp
        Num virtual antennas: Num Tx * Num Rx antennas
        chirp config per chirp: Number of Tx antenna 
        [basically number of chirp configurations outputted from the device per frame]
        num real channel: Rx ifd real data capture , 2*Rx if complex data capture
        total sample per frame: As per TI manual.    
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
    total_sample_per_frame = num_real_channel*num_adc_sample_per_chirp*chirp_config_per_chirp*num_of_chirp_per_frame ## see data format TI slide to understand.
    return num_of_frames, num_of_chirp_per_frame, num_adc_sample_per_chirp, num_range_bin, num_virtual_antennas, chirp_config_per_chirp, num_real_channel, total_sample_per_frame
    

def read_bin_file (path, num_of_frames, num_of_chirp_per_frame, num_adc_sample_per_chirp, num_range_bin, num_virtual_antennas, chirp_config_per_chirp, num_real_channel, total_sample_per_frame ) :
    """
    Given all the RADAR parameters and the path of the input .bin file returns the data in numpy format
    """
    data_file = np.fromfile(path , dtype=np.int16)
    data = data_file.reshape (num_of_frames,num_of_chirp_per_frame,num_real_channel//2,num_adc_sample_per_chirp*2)
    final_data = np.zeros((num_of_frames,num_of_chirp_per_frame,num_real_channel//2,num_adc_sample_per_chirp),dtype=complex)
    
    
    for i in range(num_of_frames):
        for j in range(num_of_chirp_per_frame):
            for k in range(num_real_channel//2):
                for l in range(num_adc_sample_per_chirp):
                    
                    if l % 2 ==0:
                        final_data[i][j][k][l] = data[i][j][k][2*l] + 1j*data[i][j][k][2*l+2]
                    else:
                        final_data[i][j][k][l] = data[i][j][k][2*l-1] + 1j*data[i][j][k][2*l+1]
    
    
    return final_data


def reshape_np(org_np,num_of_frames,num_real_channel,num_of_chirp_per_frame,num_adc_sample_per_chirp):
    reshaped_data = np.zeros((num_of_frames,num_real_channel//2,num_of_chirp_per_frame,num_adc_sample_per_chirp),dtype=complex)
    
    for i in range(num_of_frames):
        for j in range(num_real_channel//2):
            for k in range(num_of_chirp_per_frame):
                for l in range(num_adc_sample_per_chirp):
                    reshaped_data[i][j][k][l] = org_np[i][k][j][l]
                    
    return reshaped_data

if __name__ == "__main__":
    args = parse_args()
    inp_file_path = args.input_path
    json_file_path = args.json_path
    num_of_frames, num_of_chirp_per_frame, num_adc_sample_per_chirp, num_range_bin, num_virtual_antennas, chirp_config_per_chirp, num_real_channel, total_sample_per_frame = getparams(json_file_path)
    data_in_np = read_bin_file(inp_file_path, num_of_frames, num_of_chirp_per_frame, num_adc_sample_per_chirp, num_range_bin, num_virtual_antennas, chirp_config_per_chirp, num_real_channel, total_sample_per_frame)
    data_in_np=reshape_np(data_in_np,num_of_frames,num_real_channel,num_of_chirp_per_frame,num_adc_sample_per_chirp)
    np.save(args.save_path, data_in_np)