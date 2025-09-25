import cv2
import numpy as np

img = cv2.imread('120ftTTWalls.png')

sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)

grad_mag = cv2.magnitude(sobelx, sobely)
grad_mag = cv2.convertScaleAbs(grad_mag)

cv2.imshow("Edges", grad_mag)
cv2.waitKey(0)
cv2.destroyAllWindows()
