
import numpy as np
import matplotlib.pyplot as plt
import random
import cv2


def segmentDigit_binary(image_path):
    image = cv2.imread(image_path)
    h = image.shape[0]
    w = image.shape[1]

    new_image = np.zeros((h, w, 3), dtype="uint8")
    final_binary = np.zeros((h, w), dtype="uint8")
    colorset = set()
    for y in range(1, h-1):
        for x in range(1, w-1):
            L = [image[y][x], image[y][x-1]]
            out = (np.diff(np.vstack(L).reshape(len(L), -1), axis=0) == 0).all()
            if(out):
                colorset.add((image[y][x][0], image[y][x][1], image[y][x][2]))
                new_image[y][x] = image[y][x]

    image_stack = []
    for color in colorset:
        singlecolorimage = np.zeros((h, w, 3), dtype="uint8")
        for y in range(1, h-1):
            for x in range(1, w-1):
                if((image[y][x] == color).all()):
                    singlecolorimage[y][x] = new_image[y][x]
        image_stack.append(singlecolorimage)

    rectList = []
    for im in image_stack:
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        binary2, contours, hierarchy = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for i in range(0, len(contours)):
            if(len(contours) > 1):
                break
            x, y, w, h = cv2.boundingRect(contours[i])
            if(600 > w*h > 150 and w < 30 and h < 30 and np.count_nonzero(im)/(w*h) > 0.5):
                rectList.append([x, y, w, h, np.count_nonzero(im)/(w*h)])
                final_binary = cv2.bitwise_or(final_binary, binary)

    rectList = sorted(rectList, key=lambda l: l[0])
    while(len(rectList) > 4):
        rectList = getOutlierIndex(rectList)

    digit_image = []
    for r in rectList:
        x, y, w, h = r[0], r[1], r[2], r[3]
        digit_image.append(cv2.resize(
            final_binary[y:y+h, x:x+w], (20, 20), interpolation=cv2.INTER_AREA))

    return digit_image


def getOutlierIndex(arr):
    upper = 12
    lower = 4
    for i in range(0, len(arr)-1):
        dist = arr[i+1][0] - (arr[i][0] + arr[i][2])
        if(dist > upper or dist < lower):
            if(i+2 >= len(arr)):
                arr.pop(i+1)
                return arr
            else:
                second_dist = arr[i+2][0] - (arr[i][0] + arr[i][2])
                if(lower < second_dist < upper):
                    arr.pop(i+1)
                    return arr
                else:
                    arr.pop(i)
                    return arr
    arr = sorted(arr, key=lambda l: l[4], reverse=True)
    arr.pop()
    arr = sorted(arr, key=lambda l: l[0])
    return arr
