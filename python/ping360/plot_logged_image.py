from decode_sensor_binary_log import PingViewerLogReader
import numpy as np
import argparse
import cv2

parser = argparse.ArgumentParser(description="Ping360 Data Plotter")
parser.add_argument('--file', action="store", required=True, type=str, help=".bin file")
args = parser.parse_args()

logfile = args.file

log = PingViewerLogReader(logfile)

#timestamps, messages = log.parser()

# for timestamp, message in log.parser():
#     if message.message_id == 2301:
#         print(message.data[0])
#     continue


def decodeImage(log):
    timestamp, message = next(log.parser("00:00:05.300"))
    start_angle = message.start_angle
    end_angle = message.stop_angle
    num_steps = message.num_steps
    num_samples = message.number_of_samples
    image_array = np.zeros((int((end_angle-start_angle+1)/num_steps), num_samples))
    for timestamp, message in log.parser("00:01:17.000"):
        print(timestamp)
        angle = message.angle
        raw_data = message.data
        angle_index = int((angle-start_angle)/num_steps)
        image_array[angle_index, :] = np.array(list(map(int, raw_data)))/255
    #Toss first 100 indexes on each bearing
    image_array[:,0:100] = np.zeros((int((end_angle-start_angle+1)/num_steps),100))
    return image_array

im = decodeImage(log)
scaled_image = cv2.normalize(im, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
blured_img = cv2.fastNlMeansDenoising(scaled_image, None, 7, 9, 21)
(ret, cutoff_image) = cv2.threshold(scaled_image, 25, 255, cv2.THRESH_TOZERO)
(ret, blured_cutoff_image) = cv2.threshold(blured_img, 25, 255, cv2.THRESH_TOZERO)
color_img = cv2.applyColorMap(cutoff_image, cv2.COLORMAP_PARULA)
blured_color_img = cv2.applyColorMap(blured_cutoff_image, cv2.COLORMAP_PARULA)
circle_image = cv2.warpPolar(blured_color_img,center=[1200,1200],dsize=(1200*2,1200*2),maxRadius=1200,flags=cv2.WARP_INVERSE_MAP + cv2.WARP_POLAR_LINEAR)

cv2.imshow("Circle Sonar Image", circle_image)
cv2.imshow("Rect Polar Image", blured_color_img)
cv2.imshow("Unblurred Image", color_img)
cv2.waitKey(0)