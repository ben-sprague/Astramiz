import cv2
import argparse
import os
import json
import pandas as pd
import datetime

drawing = False
ix,iy = -1,-1
img = None
window_name = ''
next_image = True
image_data = pd.DataFrame(columns=['id, width', 'height', 'file_name', 'licence'])
annotations_data = pd.DataFrame(columns=['id, image_id', 'category_id', 'bbox', 'area'])

def mouse_callback(event,x,y,flags,param):
    global ix, iy, drawing, img, next_image
    

    drawn_on_img = img
    if event == cv2.EVENT_LBUTTONDOWN:
        if drawing:
            cv2.rectangle(drawn_on_img,(ix,iy),(x,y),(0,0,255),1)
            cv2.imshow(window_name, drawn_on_img)
            drawing = False
        else:
            drawing = True
            ix,iy = x,y
    elif event == cv2.EVENT_RBUTTONUP:
        next_image = True

def label_image(path, name, id):
    global img, window_name, next_image, image_data
    img = cv2.imread(path)
    width, height, _ = img.shape

    license = 1
    images_data_entry = pd.DataFrame([id, width, height, name, license])
    image_data = pd.concat((image_data, images_data_entry))

    print(image_data.to_json())


    cv2.imshow(window_name := f"Image Labeler - {name}", img)
    cv2.setMouseCallback(window_name, mouse_callback)

    while not next_image:
        cv2.waitKey(10)
    else:
        cv2.destroyAllWindows()
        next_image = False



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Labeler")
    parser.add_argument('--input_dir', action="store", required=True, type=str, help="Directory with CSV files")
    parser.add_argument('--output_location', action="store", required=False, default = 'labels.csv', type=str)
    parser.add_argument('--file_ext', type=str, required=False, default='.png')
    parser.add_argument('--starting_file', type=str, required=False, default = None)


    args = parser.parse_args()
    abs_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(abs_path)

    if os.path.isdir(input_path := os.path.join(file_dir,args.input_dir)):
        files = os.listdir(input_path)
        files.sort()

        if args.starting_file is not None:
            indi = files.index(args.starting_file)
            files = files[indi:]

        for index, file in enumerate(files):
            if args.file_ext in file:
                label_image(os.path.join(input_path, file), file, index)

    info_data = {
        "description": "Ice Data Annotations",
        "version": "1.0",
        "year": 2025,
        "contributor": "Ben Sprague",
        "date_created": datetime.datetime.now().strftime("%Y/%m/%d")
    }

    licenses_data = [
        {
            "url": "https://tlo.mit.edu/understand-ip/exploring-mit-open-source-license-comprehensive-guide",
            "id": 1,
            "name": "MIT License"
        }
    ]

    categories_data = [
        {"supercategory": "obstruction", "id": 1, "name": "ice"},
    ]
