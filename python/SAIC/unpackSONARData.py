import numpy as np
import pandas as pd
import cv2

class SONARData():

    def __init__(self):
        self.rect_exists = False
        self.polar_exists = False
    
    def openCSV(self, path, outlier_fill = 0):
        self.outlier_fill = outlier_fill
        self.rect_img = pd.read_csv(path).to_numpy().astype(np.float32)
        self.rect_img = cv2.normalize(self.rect_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
        self.rect_exists = True
        self.__transformPolar__()

    def __transformPolar__(self):
        if self.rect_exists:
            self.radius = self.rect_img.shape[1]
            self.polar_img = cv2.warpPolar(self.rect_img, dsize=(self.radius*2, self.radius*2), center=[self.radius,self.radius], maxRadius=(self.radius), flags=cv2.INTER_CUBIC +cv2.WARP_INVERSE_MAP+cv2.WARP_POLAR_LINEAR+cv2.WARP_FILL_OUTLIERS)
            if self.outlier_fill != 0:
                mask = np.full((self.radius*2, self.radius*2), fill_value=255, dtype="uint8")
                cv2.circle(mask, (self.radius, self.radius), self.radius, 0, thickness=-1)
                self.polar_img[mask>0] = self.outlier_fill
            self.polar_exists = True
            

    def __generatePolarMask__(self, radius):
        mask = np.full((radius*2, radius*2), False)
        for m, row in enumerate(mask):
            for n, item in enumerate(row):
                y_dist = np.abs(m-radius)
                x_dist = np.abs(n-radius)
                if np.sqrt(x_dist**2+y_dist**2) > radius:
                    mask[m,n] = True
        
        return mask

    def showRectImg(self, window_name):
        if self.rect_exists:
            cv2.imshow(window_name, self.rect_img)
        else:
            raise AttributeError("Rectangular version of image does not exist")
        
    def showPolarImg(self, window_name):
        if self.polar_exists:
            cv2.imshow(window_name, self.polar_img)
        else:
            raise AttributeError("Polar version of image does not exist")

    def saveRectImg(self, path, size=()):
        if self.rect_exists:
            self.__saveImg__(self.rect_img, path, size)
        else:
            raise AttributeError("Rectangular version of image does not exist")

    def savePolarImg(self, path, size=()):
        if self.polar_exists:
            self.__saveImg__(self.polar_img, path, size)
        else:
            raise AttributeError("Polar version of image does not exist")
    
    def __saveImg__(self, img, path, size):
        #Ensure image is normalized from 0 to 255
        working_img = cv2.normalize(img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX).astype(np.uint8)
        if len(size) == 0:
            #Don't resize image
            pass
        else:
            #Resize Image
            working_img = cv2.resize(working_img, size, interpolation=cv2.INTER_AREA) #Assume image will always be downscaled
        cv2.imwrite(path, working_img)



