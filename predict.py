
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os
import csv
from utils import segmentDigit_binary
from matplotlib import pyplot as plt
import sys


LETTERSTR = "123456789ABCDEFGHJKLMNPQRSTUVWXYZefqw"
singleDetect = True

model = load_model("./model.h5")


def image_test_color_seg(path):
    test_image = []
    digit_images = segmentDigit_binary(path)

    for i in digit_images:
        nparr = np.array(i)  # convert to np array
        nparr = np.expand_dims(nparr, axis=2)
        nparr = nparr / 255.0
        test_image.append(nparr)

    test_image = np.stack(test_image)

    prediction = model.predict(test_image)
    answer = ""
    for predict in prediction:
        answer += LETTERSTR[np.argmax(predict)]

    return(answer)


def main(argv):
    print(argv)
    print(image_test_color_seg(argv[1]))


if __name__ == "__main__":
    main(sys.argv)
