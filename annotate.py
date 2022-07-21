#!/usr/bin/env python3
import os
import sys
import argparse
import configparser
import shutil

from lxml import etree
from flask import Flask, render_template, jsonify, request
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

CUR_IMG = None
ANNOTATIONS_PATH = None
IMGS = []

def write_xml(rects, file_name):
    if os.path.exists(file_name):
        open(file_name, 'w').close()
    annotation = etree.Element("annotation")
    for rect in rects:
        (x, y, width, height) = list(map(str, map(abs, rect[:-1])))
        label = rect[-1]
        bounding_box = etree.SubElement(annotation, "bndbox")
        etree.SubElement(bounding_box, "x").text = x
        etree.SubElement(bounding_box, "y").text = y
        etree.SubElement(bounding_box, "width").text = width
        etree.SubElement(bounding_box, "height").text = height
        etree.SubElement(bounding_box, "label").text = label
    tree = etree.ElementTree(annotation)
    tree.write(file_name, pretty_print=True)

@app.route('/')
def serve():
    return render_template('home.html')

@app.route('/cur', methods=['POST'])
def cur():
    global CUR_IMG
    filename = os.path.join('images', os.path.basename(IMGS[CUR_IMG]))
    shutil.copy(IMGS[CUR_IMG], os.path.join('static', filename))
    return jsonify({"filename": filename})

@app.route('/next', methods=['POST'])
def next():
    global CUR_IMG
    filename = os.path.join('images', os.path.basename(IMGS[CUR_IMG]))
    if CUR_IMG + 1 < len(IMGS):
        os.remove(os.path.join('static', filename))
        CUR_IMG += 1
        filename = os.path.join('images', os.path.basename(IMGS[CUR_IMG]))
        shutil.copy(IMGS[CUR_IMG], os.path.join('static', filename))
    return jsonify({"filename": filename})

@app.route('/prev', methods=['POST'])
def prev():
    global CUR_IMG
    filename = os.path.join('images', os.path.basename(IMGS[CUR_IMG]))
    if CUR_IMG - 1 >= 0:
        os.remove(os.path.join('static', filename))
        CUR_IMG -= 1
        filename = os.path.join('images', os.path.basename(IMGS[CUR_IMG]))
        shutil.copy(IMGS[CUR_IMG], os.path.join('static', filename))
    return jsonify({"filename": filename})

@app.route('/save', methods=['POST'])
def save():
    global CUR_IMG
    rects = request.json['rects']
    filename = os.path.join(
        ANNOTATIONS_PATH, IMGS[CUR_IMG].split('/')[-1].split('.')[0] + ".xml")
    write_xml(rects, filename)
    return jsonify({})

def process_IMGS(folder, valid_IMGS=[".jpg", ".png"]):
    global CUR_IMG
    ret = []
    num = 1
    for img in sorted(os.listdir(folder)):
        name, ext = os.path.splitext(img)
        try:
            name = int(name)
        except:
            raise Exception(
                "Images should be named starting from 1 (e.g. 1.jpg)")
        if int(name) != num:
            raise Exception(f"No img has number {num}!")
        assert ext in valid_IMGS, f"File \"{img}\" is not an image!"
        if os.path.exists(os.path.join("static", "images", img)) and CUR_IMG is None:
          CUR_IMG = num-1
        ret.append(os.path.join(folder, img))
        num += 1
    if CUR_IMG is None:
        CUR_IMG = 0
    for img in os.listdir(os.path.join('static', 'images')):
      os.remove(os.path.join('static', 'images', img))
    return ret

def main():
    global IMGS, ANNOTATIONS_PATH

    config = configparser.ConfigParser()
    config.read('config.ini')

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "folder", help="directory of the images that want to be annotated")
    parser.add_argument("--port",
                        help="listen port for web interface",
                        type=int,
                        default=int(config["SERVER"]["PORT"]))
    parser.add_argument("--host",
                        help="listen address for web interface",
                        default=config["SERVER"]["HOST"])
    args = parser.parse_args()
    prod = int(os.getenv("PROD", '1'))
    assert os.path.isdir(
        args.folder), f"Folder \"{args.folder}\" doesn't exist!"

    dir, _ = os.path.split(args.folder)
    if not os.path.isdir(os.path.join(dir, "annotations")):
        os.mkdir(os.path.join(dir, "annotations"))
    ANNOTATIONS_PATH = os.path.join(dir, "annotations")
    if not os.path.isdir(os.path.join('static', 'images')):
      os.mkdir(os.path.join('static', 'images'))
    IMGS = process_IMGS(args.folder)

    print(
        f"***** Starting {'production' if prod else 'development'} web server on {args.host}:{args.port} *****"
    )
    try:
        if prod:
            # https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/
            http_server = WSGIServer((args.host, args.port), app)
            http_server.serve_forever()
        else:
            app.run(host=args.host, port=args.port, debug=True)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
