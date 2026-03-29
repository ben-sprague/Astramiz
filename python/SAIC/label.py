import cv2
import argparse
import os
import json
import pandas as pd
import datetime
import numpy as np

from unpackSONARData import SONARData

import progressbar


drawing = False
drawn_on_img = None
working_img = None
x1, y1 = -1, -1
x2, y2 = -1, -1
window_name = ''
next_image = False
image_data = []
working_bboxs = np.ndarray((0,4))
annotations_data = []
scale_factor = 1
current_file = ''
output_path = ''

def print_instructions():
    instructions = '''
    Left click to create bounding box
    Arrow Keys moves bottom left corner
    WASD moves right corner
    x key deletes current working rectangle
    c key clears all rectangles
    Space bar saves the rectangle
    ESC exits and saves progress
    '''
    print(instructions)

def draw_rectangles(rect_array):
    #Rect array is a Nx4 array with (N,:) = x1, y1, x2, y2
    global working_img, drawn_on_img, scale_factor
    drawn_on_img = working_img.copy()
    for row in rect_array:
        x1, y1, x2, y2 = row.astype(int)
        scaled_x1, scaled_y1, scaled_x2, scaled_y2 = list(int(value/scale_factor) for value in [x1, y1, x2, y2])
        cv2.rectangle(drawn_on_img,(scaled_x1,scaled_y1),(scaled_x2, scaled_y2),(0,0,255),2)

def draw_current_rectangle():
    global x1, y1, x2, y2, working_bboxs, drawn_on_img
    draw_rectangles(working_bboxs)
    #Do conversion that will be done when saving to downsample annotations for 300x300px image so position of bounding box location is accurate
    scaled_x1, scaled_y1, scaled_x2, scaled_y2 = list(int(value*scale_factor) for value in [x1, y1, x2, y2])
    scaled_x1, scaled_y1, scaled_x2, scaled_y2 = list(int(value/scale_factor) for value in [scaled_x1, scaled_y1, scaled_x2, scaled_y2])
    cv2.rectangle(drawn_on_img, (scaled_x1,scaled_y1),(scaled_x2, scaled_y2),(0,255,0),2)

def mouse_callback(event,x,y,flags,params):
    global x1, y1, x2, y2, drawn_on_img, drawing, next_image, working_bboxs, working_img, scale_factor, window_name

    if event == cv2.EVENT_LBUTTONDOWN:
        if drawing:
            #Ensure that (x2, y2) is always above and to the right of (x1, y1)
            x2, y2 = (x,y)
            if x1>x2:
                x1, x2 = x2, x1
            if y1>y2:
                y1, y2 = y2, y1
            draw_current_rectangle()
            cv2.imshow(window_name, drawn_on_img)
            drawing = False
        else:
            drawing = True
            x1,y1 = (x,y)
    elif event == cv2.EVENT_RBUTTONUP:
        if x1 >=0:
            #If there is an unsaved annotation, save it
            working_bboxs = np.vstack((working_bboxs, [int(x1*scale_factor), int(y1*scale_factor), int(x2*scale_factor), int(y2*scale_factor)]))
        next_image = True

def keyboard_callback(key, img):
    global x1, y1, x2, y2, drawn_on_img, window_name, working_bboxs, scale_factor, working_img
    jog_dist = int(1/scale_factor) #pixels to jog on key press
    #Arrow keys 0:up, 1:down, 2:left, 3:right
    if key == 0:
        #Jog bottom up 
        y2 -= jog_dist
        draw_current_rectangle()
        cv2.imshow(window_name, drawn_on_img)

    elif key == 1:
        #Move bottom down 
        y2 += jog_dist
        draw_current_rectangle()
        cv2.imshow(window_name, drawn_on_img)
    elif key == ord('a'):
        #Move left side left 
        x1 -= jog_dist
        draw_current_rectangle()
        cv2.imshow(window_name, drawn_on_img)
    elif key == ord("d"):
        #Move left side right 
        x1 += jog_dist
        draw_current_rectangle()
        cv2.imshow(window_name, drawn_on_img)

    
    elif key == ord('w'):
        #Move bottom up
        y1 -= jog_dist    
        draw_current_rectangle()
        cv2.imshow(window_name, drawn_on_img)
    elif key == 2:
        #Move right side left
        x2 -= jog_dist
        draw_current_rectangle()
        cv2.imshow(window_name, drawn_on_img)
    elif key == 3:
        #Move right side right
        x2 += jog_dist
        draw_current_rectangle()
        cv2.imshow(window_name, drawn_on_img)
    elif key == ord('s'):
        #Move top down
        y1 += jog_dist
        draw_current_rectangle()
        cv2.imshow(window_name, drawn_on_img)

    elif key == ord('x'):
        #Delete current rectangle and redraw image
        x1, x2, y1, y2 = -1,-1,-1,-1
        draw_rectangles(working_bboxs)
        cv2.imshow(window_name, drawn_on_img)

    elif key == ord(' '):
        #Save current rectangle to rectangle array
        working_bboxs = np.vstack((working_bboxs, [int(x1*scale_factor), int(y1*scale_factor), int(x2*scale_factor), int(y2*scale_factor)]))
        draw_rectangles(working_bboxs)
        cv2.imshow(window_name, drawn_on_img)
        x1, x2, y1, y2 = -1,-1,-1,-1
    
    elif key == ord('c'):
        #Clear all inputs
        working_bboxs = np.ndarray((0,4))
        cv2.imshow(window_name, working_img)

    elif key == 27:
        #Escape key, exit program
        exit_function()
        exit()
    

def generate_image_dict(path, img, rel_path = ""):
    file_name = path.split("/")[-1] #Get file name (with extention)
    image_id = file_name.split(".")[0] #Strip file extention
    license_id = 1
    height, width = img.shape

    image_dict = {
        "id": image_id,
        "license": license_id,
        "width": width,
        "height": height,
        "file_name": os.path.join(rel_path, file_name)
    }

    return image_dict

def label_image(img, name):
    WINDOW_SIZE = 2400
    global window_name, next_image, working_bboxs, working_img, annotations_data, scale_factor
    working_bboxs = np.ndarray((0,4))
    working_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    true_img_height = working_img.shape[0]
    scale_factor = true_img_height/WINDOW_SIZE
    cv2.imshow(window_name := f"Image Labeler - {name}", working_img := cv2.resize(working_img, (WINDOW_SIZE,WINDOW_SIZE), interpolation=cv2.INTER_LINEAR))
    cv2.setMouseCallback(window_name, mouse_callback)

    while not next_image:
        key = cv2.waitKey(1) & 0xFF

        if key != 255:
            #Pass to keyboard event handeler
            keyboard_callback(key, img)
            
    else:
        cv2.destroyAllWindows()
        annotations_data.extend(gen_annotation_dict(name))
        working_bboxs = working_bboxs = np.ndarray((0,4))
        next_image = False

def gen_annotation_dict(image_id: str):
    global working_bboxs
    image_id = image_id.split(".")[0]
    working_list = []
    annotation_id_num = 0
    for row in working_bboxs:
        x1, y1, x2, y2 = row.astype(int)
        width, height = x2-x1, y2-y1
        area = width*height
        unique_annotation_id = f'{image_id}{annotation_id_num}'
        working_list.append(dict(
            id = unique_annotation_id,
            image_id = image_id,
            category_id = 1,
            area = area,
            bbox = [x1, x1, width, height]
        ))
        annotation_id_num += 1
    
    return working_list

def write_COCO(out_path, image_dict, label_dict):
    info_data = {
        "description": "SONAR Target Data Annotations",
        "version": "1.0",
        "year": 2026,
        "contributor": "Ben Sprague",
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

    full_dict = dict(
        info = info_data,
        licenses = licenses_data,
        images = image_dict,
        annotations = label_dict,
        categories = categories_data,
    )

    with open(out_path, 'w') as json_file:
        json.dump(full_dict, json_file, indent=4, default=int)

def exit_function():
    global current_file, output_path
    write_COCO(output_path, image_data, annotations_data)
    print(f"Saved Annotations to {output_path}")
    print(f"Restart from {current_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Labeler")
    parser.add_argument('--input_dir', action="store", required=True, type=str, help="Directory with CSV files")
    parser.add_argument('--output_location', action="store", required=False, default = 'annotations.json', type=str)
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

        output_path = os.path.join(input_path, args.output_location)
        print_instructions()
        try:
            bar = progressbar.ProgressBar(max_value=len(files))
            for file in files:
                if args.file_ext in file:
                    current_file = file
                    file_name = file.split('.')[0]
                    full_path = os.path.join(input_path, file)
                    if "csv" in args.file_ext:
                        raw_data = SONARData()
                        raw_data.openCSV(full_path, outlier_fill=255)
                        raw_data.savePolarImg(img_path := os.path.join(input_path, f'img/{file_name}.png'), size = (300,300))
                    elif "png" in args.file_ext:
                        img_path = full_path
                    elif "jpeg" in args.file_ext:
                        img_path = full_path
                    elif "jpg" in args.file_ext:
                        img_path = full_path
                    
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    image_data.append(generate_image_dict(img_path, img, rel_path="img"))
                    label_image(img, file)
                bar.increment()

        except KeyboardInterrupt:
            exit_function()

        write_COCO(os.path.join(input_path, args.output_location), image_data, annotations_data)
