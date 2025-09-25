import cv2
import os
import argparse
import numpy as np
from skimage import filters, morphology, segmentation, measure, color


def denoise(img):
    denoised_img = cv2.fastNlMeansDenoising(scaled_image, None, 7, 9, 21)
    (ret, denoised_cutoff_image) = cv2.threshold(denoised_img, 25, 255, cv2.THRESH_TOZERO)
    return denoised_cutoff_image

def colorize(img):
    denoised_color_img = cv2.applyColorMap(img, cv2.COLORMAP_PARULA)
    return denoised_color_img

def threshold_label(img):
    thresh = filters.threshold_otsu(img)
    (ret, thresh_image)= cv2.threshold(denoised_img,thresh, 255, cv2.THRESH_BINARY)
    connected_image = morphology.closing(thresh_image)
    cleared_image = segmentation.clear_border(connected_image)
    label_image = measure.label(cleared_image,connectivity=1)
    output_image = color.label2rgb(label_image, image=scaled_image, bg_label=0)
    output_image = cv2.normalize(output_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC3)
    return output_image


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping360 Data Plotter")
    parser.add_argument('--input_dir', action="store", required=True, type=str, help="Directory with CSV files")
    parser.add_argument('--output_dir', action="store", required=True, type=str, help="Directory to store images in")

    args = parser.parse_args()

    all_entries = os.listdir(args.input_dir)
    entries = [entry for entry in all_entries if os.path.isfile(os.path.join(args.input_dir, entry))]

    if not(os.path.exists(args.output_dir) and os.path.isdir(args.output_dir)):
        os.makedirs(args.output_dir, exist_ok=True)

    for index, entry in enumerate(entries):
        img = np.loadtxt(os.path.join(args.input_dir, entry), delimiter=",")
        scaled_image = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        denoised_img = denoise(scaled_image)
        output_image = colorize(denoised_img)
        cv2.imwrite(os.path.join(args.output_dir, f"{index}.png"), output_image)
