from bs4 import BeautifulSoup
from PIL import Image, ImageOps, ImageDraw
import cv2
import sys
import requests
import shutil
import os


WIKI_ENDPOINT = 'https://en.wikipedia.org/w/api.php'
DEBATES_LIST_URL = 'https://en.wikipedia.org/wiki/United_States_presidential_' \
                   'debates#1960_Kennedy%E2%80%93Nixon_debates'


# The graphic we are creating only requires one face for each party for each
# year. Moreover, we are not considering independents. PRESIDENTIAL_CANDIDATES
# ignores independents like Ross Perot and "third wheels" like John B. Anderson.
CANDIDATES = [
    'John F. Kennedy', 'Richard Nixon',
    'Gerald Ford', 'Jimmy Carter',
    'Ronald Reagan',
    'Walter Mondale',
    'George H. W. Bush', 'Michael Dukakis',
    'Bill Clinton',
    'Bob Dole',
    'George W. Bush', 'Al Gore',
    'John Kerry',
    'John McCain', 'Barack Obama',
    'Mitt Romney',
    'Hillary Clinton', 'Donald Trump',
]


# get_face_urls gets the image urls for the faces of every candidate.
def get_face_urls():
    urls = {}

    for title in CANDIDATES:
        r = requests.get(
            WIKI_ENDPOINT,
            params={
                'action': 'query',
                'prop': 'pageimages',
                'format': 'json',
                'pithumbsize': 300,
                'titles': title,
            }
        )

        pages = r.json()['query']['pages']
        if len(pages) == 0:
            print('No wikipedia page found for {}. Skipping candidate.'
                  .format(r.url))
            continue
        if len(pages) > 1:
            print('Multiple wikipedia pages found for {}. Skipping candidate.'
                  .format(r.url))
            continue

        try:
            urls[title] = list(pages.values())[0]['thumbnail']['source']
        except (KeyError, IndexError) as e:
            print('Unexpected JSON format for {}.\nIn pages: {}'
                  .format(r.url, pages))

    return urls


# download_faces downloads every face image from face_urls.
def download_faces(face_urls):
    dir = './data/faces/original'
    make_dir( dir )

    paths = []
    for title, url in face_urls.items():
        path = '{}/{}.png'.format(dir, title)
        paths.append( path )
        if os.path.isfile(path):
            continue
        r = requests.get(url, stream=True)
        with open( path, 'wb' ) as out_file:
            shutil.copyfileobj( r.raw, out_file )

    return paths


# extract_faces extracts faces from every face image.
def extract_faces(paths):
    make_dir('./data/faces/extracted')
    make_dir('./data/faces/cropped')
    for path in paths:
        out_path = extract_face(path)
        crop_circle(out_path)


# make_dir makes a directory if it does not already exist.
def make_dir(dir):
    if not os.path.exists( dir ):
        os.makedirs( dir )



# CV code adapted from JeeveshN's original code at
# https://github.com/JeeveshN/Face-Detect

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
        out_path = path.replace('original/', 'extracted/')
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


if __name__ == '__main__':
    face_urls = get_face_urls()
    print('Received face urls.')
    face_paths = download_faces( face_urls )
    print('Downloaded all faces.')
    extract_faces( face_paths )
