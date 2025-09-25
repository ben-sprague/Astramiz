import pickle
from math import pi, dist
import numpy as np

from matplotlib import pyplot as plt
from PIL import Image
import cv2

def unpack_class(fileName):
    file = open(fileName, 'rb')
    rawData = pickle.load(file) 
    file.close()
    return {
        "angle": rawData.angle*pi/200, #radians
        "period": rawData.sample_period*25e-9, #seconds
        "data": list(map(int, rawData.data)),
        "sample_count": rawData.number_of_samples 
    }   

def plot_single_ping(pingData):
    plt.plot(pingData['data'])
    plt.show()

def generate_polar_image_chunk(pingData):
    intensity = np.array(pingData['data'])
    theta = np.full(pingData['sample_count'], pingData['angle'])
    distance_per_sample = speed_of_sound*pingData['period']
    max_range = pingData['sample_count']*distance_per_sample
    range = np.linspace(0,max_range,pingData['sample_count'])
    return {'intensity': intensity, 'theta': theta, 'range': range}

def generate_polar_image():
    intensity = []
    theta = []
    distance = []
    for i in range(0,399):
        pingData = unpack_class(f"angle{i}.bin")
        chunk = generate_polar_image_chunk(pingData)
        intensity.append(chunk['intensity'])
        theta.append(chunk['theta'])
        distance.append(chunk['range'])
    return np.array((intensity, theta, distance))

def plotPolarImg(polar_img):
    intensity = polar_img[0]
    theta = polar_img[1]
    distance = polar_img[2]
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    scatter = ax.scatter(theta, distance, c=intensity, cmap='Greys', s=0.1)
    ax.set_theta_zero_location('N')  # Set 0 degrees to the top
    ax.set_theta_direction(-1)  # Set the direction to be clockwise
    plt.show()

def getPolarIndex(x, y, theta, radius, image_radius):
    center = [image_radius, image_radius]#Center of the image is at (image_radius, image_radius)
    distance = dist(center, [x,y]) #distance from center of the image to the pixel
    

def polarToImg(polar_img, image_radius):
    im_array = np.zeros((image_radius*2,image_radius*2))
    intensity = polar_img[0]
    theta = polar_img[1]
    radius = polar_img[2]
    theta_vals = np.unique(theta)
    radius_vals = np.unique(radius)
    for m in range(0,image_radius*2):
        print(m)
        for n in range(0, image_radius*2):
            #Starting at top left corner
            center = [image_radius, image_radius]#Center of the image is at (image_radius, image_radius)
            distance = dist(center, [m,n]) #distance from center of the image to the pixel
            if distance <= image_radius:
                #if inside the polar image, populate the pixel with the nearest intensity value
                angle = np.arctan2(n-image_radius,m-image_radius) #angle in radians from center to pixel
                #print(angle*180/pi)
                radius_index = np.argmin(np.abs(radius_vals-distance))
                search_radius = radius_vals[radius_index]
                theta_index = np.argmin(np.abs(theta_vals-angle))
                search_theta = theta_vals[theta_index]
                theta_index = np.where(search_theta == theta_vals)
                radius_index = np.where(search_radius == radius_vals)
                #print(theta_index)
                #print(radius_index)
                im_array[m,n] = intensity[theta_index[0].item(), radius_index[0].item()]

    return Image.fromarray(im_array)




if __name__ == "__main__":
    speed_of_sound = 1500 #m/s
    polar_img = generate_polar_image()
    image_radius = np.shape(polar_img)[2]
    circle_image = cv2.warpPolar(polar_img[0,:,:],center=[image_radius,image_radius],dsize=(image_radius*2,image_radius*2),maxRadius=image_radius,flags=cv2.WARP_INVERSE_MAP + cv2.WARP_POLAR_LINEAR)
    cv2.imwrite('rect_SONAR.png', polar_img[0,:,:])
    cv2.imwrite('polar_SONAR.png', circle_image)
    plt.imshow(circle_image,cmap="viridis")
    plt.show()

    #plotPolarImg(polar_img)




