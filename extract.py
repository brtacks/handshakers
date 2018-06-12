# Adapted from original code by JeeveshN.
# Original code at https://github.com/JeeveshN/Face-Detect

from random import randint
import cv2
import sys
import os

CASCADE = 'face_cascade.xml'
FACE_CASCADE = cv2.CascadeClassifier(CASCADE)


def extract_face(image_path):
    image = cv2.imread(image_path)
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = FACE_CASCADE.detectMultiScale(image_grey, scaleFactor=1.16,
            minNeighbors=5, minSize=(25, 25), flags=0)

    for (x, y, w, h) in faces:
        sub_img = image[y - 10:y + h + 10, x - 10:x + w + 10]
        cv2.imwrite(image_path.replace('faces/', 'faces/extracted/'),
                    sub_img)

