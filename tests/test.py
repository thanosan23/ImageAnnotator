#!/usr/bin/env python3
import os
import argparse
from lxml import etree
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument('annotation', help='annotation file')
parser.add_argument('image', help='image file')
args = parser.parse_args()

if not os.path.isdir(os.path.join(os.getcwd(), 'tests', 'processed_images')):
    os.mkdir(os.path.join(os.getcwd(), 'tests', 'processed_images'))

data = {
    'data_x': None,
    'data_y': None,
    'data_width': None,
    'data_height': None
}
fp = os.path.join(os.getcwd(), args.annotation)
with open(fp, 'r', encoding="utf-8", errors="ignore") as f:
    XML = f.read()
root = etree.fromstring(XML)
for bndbox in root.getchildren():
    for element in bndbox.getchildren():
        if element.tag != "label":
          data['data_' + element.tag] = int(element.text)

found_annotation = True
for item, value in data.items():
    if value is None:
        found_annotation = False

if not found_annotation:
    print("Can't draw image because image doesn't have annotations!")
else:
    print("Processing Image...")
    img = Image.open(os.path.join(os.getcwd(), args.image), 'r').convert('RGB')
    img_draw = ImageDraw.Draw(img)
    img_draw.rectangle(((data['data_x'], data['data_y']),
                        (data['data_x'] + data['data_width'],
                         data['data_y'] + data['data_height'])),
                       outline='Red')
    img.save(
        os.path.join(os.getcwd(), 'tests', 'processed_images',
                     os.path.basename(args.image)))
