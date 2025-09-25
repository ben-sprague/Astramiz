from decode_sensor_binary_log import PingViewerLogReader
import numpy as np
import argparse
from PIL import Image
import os


def writeImage(image_array, name):
    #Toss first 100 indexes on each bearing
    image_array[:,0:100] = np.zeros((np.size(image_array,0),100))
    np.savetxt(f"{args.output_dir}/csv/{name}.csv",image_array, delimiter=",")
    if args.write_image:
        im = Image.fromarray((image_array*255).astype(np.uint8))
        im.save(f"{args.output_dir}/img/{name}.png")


def decodeImage(log):
    decoding_image = False
    last_angle = 0
    full_sweep = False
    assending = True
    for timestamp, message in log.parser():
        if (angle:= message.angle) == message.start_angle and not decoding_image:
            decoding_image = True
            num_steps = message.num_steps
            num_samples = message.number_of_samples
            start_angle = message.start_angle
            end_angle = message.stop_angle
            if start_angle == 0 and end_angle == 399:
                full_sweep = True
                assending = True
            else:
                full_sweep = False
            image_array = np.zeros((int((end_angle-start_angle+1)/num_steps), num_samples))
        if decoding_image:
            raw_data = message.data
            angle_index = int((angle-start_angle)/num_steps)
            image_array[angle_index, :] = np.array(list(map(int, raw_data)))/255
        if angle > end_angle or (no_longer_assending := (last_angle>angle and assending)) or (no_longer_decending := (last_angle<angle and not assending)):
            writeImage(image_array, timestamp.replace(":", "-"))
            num_steps = message.num_steps
            num_samples = message.number_of_samples
            start_angle = message.start_angle
            end_angle = message.stop_angle
            if start_angle == 0 and end_angle == 399:
                full_sweep = True
                assending = True
            else:
                full_sweep = False
            image_array = np.zeros((int((end_angle-start_angle+1)/num_steps), num_samples))
            if angle > end_angle:
                decoding_image = False
            elif no_longer_assending and not full_sweep:
                assending = False
            elif no_longer_decending and not full_sweep:
                assending = True
                
        last_angle = angle

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping360 Data Plotter")
    parser.add_argument('--file', action="store", required=True, type=str, help=".bin file")
    parser.add_argument('--output_dir', action="store", required=True, type=str, help="Directory to store csv files in")
    parser.add_argument('--write_image', action="store_true", default = False, help="Write images")

    args = parser.parse_args()

    if not(os.path.exists(f"{args.output_dir}/csv") and os.path.isdir(f"{args.output_dir}/csv")):
        os.makedirs(f"{args.output_dir}/csv", exist_ok=True)
    if args.write_image and not(os.path.exists(f"{args.output_dir}/img") and os.path.isdir(f"{args.output_dir}/img")):
        os.makedirs(f"{args.output_dir}/img", exist_ok=True)

    logfile = args.file

    log = PingViewerLogReader(logfile)

    decodeImage(log)



        
    
    
    
