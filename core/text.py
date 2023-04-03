import numpy as np
import cv2
from pyocr import pyocr
from pyocr import builders
from PIL import Image
from time import sleep
import imutils
from imutils.perspective import four_point_transform





def resize1():
    image = cv2.imread('test/tankowanie.jpg')
    image = imutils.resize(image, height=700)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 255)
    cv2.imshow('cv',edged)
    cv2.waitKey(0)
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    displayCnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            displayCnt = approx
            break
    output = four_point_transform(image, displayCnt.reshape(4, 2))
    cv2.imshow('cvv',output)
    cv2.waitKey(0)
    height = output.shape[0]
    width = output.shape[1]
    cutoff = height // 2
    price = output[:cutoff, :]
    litres = output[cutoff:, :]
    return price, litres


def processing():

    thresh, erosion_iters, most_common_filter = 35, 2, 4
    price, litres = resize1()
    tab = [price, litres]
    tab2 = []

    for i in range(len(tab)):
        
        sleep(0.2)
        roi = tab[i]
        kernel = np.ones((5, 5), np.uint8)
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imshow('cv',roi)
        cv2.waitKey(0)
        roi = cv2.threshold(roi, thresh, 255, cv2.THRESH_BINARY)[1]
        cv2.imshow('cv',roi)
        cv2.waitKey(0)
        roi = cv2.erode(roi, kernel, iterations=erosion_iters)
        cv2.imshow('cv',roi)
        cv2.waitKey(0)
        tool = pyocr.get_available_tools()[0]  
        lang = 'ssd'
        txt = tool.image_to_string(Image.fromarray(roi), lang=lang, builder=builders.TextBuilder())
        
        try:
            x  = float(txt)/100
            tab2.append(x)
        except:
            tab2.append(None)
    return tab2
    

tab = processing()

price = tab[0]
litres = tab[1]
print('Cena: ', price,'\nLitry: ', litres)

# resize1()