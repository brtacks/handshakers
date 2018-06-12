# Adapted from JeeveshN's original code.
# Original code at https://github.com/JeeveshN/Face-Detect

from PIL import Image, ImageOps, ImageDraw
import cv2
import sys
import os


CASCADE = 'face_cascade.xml'
FACE_CASCADE = cv2.CascadeClassifier(CASCADE)


# extract_face extracts a face from an image. It saves it to
# ./data/faces/extracted/
def extract_face(path):
    image = cv2.imread(path)
    image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = FACE_CASCADE.detectMultiScale(image_grey, scaleFactor=1.16,
            minNeighbors=5, minSize=(25, 25), flags=0)

    out_path = None
    for (x, y, w, h) in faces:
        sub_img = image[y - 10:y + h + 10, x - 10:x + w + 10]
        out_path = path.replace('faces/', 'faces/extracted/')
        cv2.imwrite(out_path, sub_img)

    return out_path


# crop_circle crops an image into a circle.
def crop_circle(path):
    im = Image.open(path)
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    im.save(path.replace('extracted', 'cropped'))

