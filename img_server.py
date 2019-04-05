# -*- coding: utf-8 -*-
#!/bin/python

import os
from flask import Flask, Response, request, abort, render_template_string, send_from_directory
from PIL import Image
import StringIO
import cv2
import sys

app = Flask(__name__)
reload(sys)
sys.setdefaultencoding('utf8')

dir_path = os.path.dirname(os.path.abspath(__file__))
print(dir_path)

file_format = 'jpeg'

WIDTH = 400
HEIGHT = 200

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
<title></title>
<meta charset="utf-8" />
<style>
body {
margin: 0;
background-color: #333;
}
.image {
display: inline-block;
margin: 3em 14px;
background-color: #444;
box-shadow: 0 0 10px rgba(0,0,0,0.3);
}
img {
display: block;
}
</style>
<script src="https://code.jquery.com/jquery-1.10.2.min.js" charset="utf-8"></script>

</head>
<body>
{% for image in images %}
    <a class="image" href="{{ image.src }}" style="width: {{ image.width }}px; height: {{ image.height }}px; color:#d0d0d0; background-color:#0000a0;">
        <img src="{{ image.image_src }}" data-src="{{ image.src }}?w={{ image.width }}&amp;h={{ image.height }}" width="{{ image.width }}" height="{{ image.height }}" />
        {{image.src}}
    </a>
{% endfor %}
</body>
'''


def generate_thumbnail(filename):
    vidcap = cv2.VideoCapture(filename)
    success, image = vidcap.read()
    count = 0

    while count < 25:
        cv2.imwrite("%s.%s" % (filename.replace('#', '%23').replace('.mp4', ''), file_format), image)  # save frame
        success, image = vidcap.read()
        count += 1
    print("all done")


@app.route('/<path:filename>')
def image(filename):
    print(filename)
    try:
        w = int(request.args['w'])
        h = int(request.args['h'])
    except (KeyError, ValueError):
        return send_from_directory('.', filename)

    try:
        im = Image.open(filename)
        im.thumbnail((w, h), Image.ANTIALIAS)
        io = StringIO.StringIO()
        im.save(io, format='gif')
        return Response(io.getvalue(), mimetype='image/gif')

    except IOError:
        abort(404)

    return send_from_directory('.', filename)


@app.route('/')
def index():
    images = []
    for root, dirs, files in os.walk('.'):
        for filename in [os.path.join(root, name) for name in files]:
            if not filename.endswith('.mp4'):
                continue
            if not os.path.isfile(filename.replace('#', '%23').replace('mp4', '%s' % file_format)):
                # generate the image
                print("need to generate")
                generate_thumbnail(filename=filename)

            im = Image.open(filename.replace('#', '%23').replace('mp4', '%s' % file_format))
            w, h = im.size
            aspect = 1.0*w/h
            if aspect > 1.0*WIDTH/HEIGHT:
                width = min(w, WIDTH)
                height = width/aspect
            else:
                height = min(h, HEIGHT)
                width = height*aspect
            images.append({
                'width': int(width),
                'height': int(height),
                'image_src': filename.replace('#', '%23').replace('mp4', '%s' % file_format),
                'src': filename.replace('#', '%23')
            })

    return render_template_string(TEMPLATE, **{
        'images': images
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True)
