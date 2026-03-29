from unpackSONARData import SONARData
import cv2
import numpy as np

sonarImg = SONARData()
sonarImg.openCSV("/Users/ben/Desktop/astramiz/python/SAIC/11SEP25/Short Buoyancy Tank Test/csv/00-00-34.044.csv", outlier_fill=255)
sonarImg.showPolarImg("Polar Img")
cv2.waitKey()
sonarImg.savePolarImg("/Users/ben/Desktop/astramiz/python/SAIC/test.png", size=(300,300))