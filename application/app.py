from flask import Flask
from flask import send_from_directory, render_template, redirect, request
import os
import base64
import datetime
import re

SRC = os.path.dirname(os.path.abspath(__file__)) + '/images'
app = Flask(__name__, static_folder='images')


@app.route('/')
def index():
    return render_template('index.htm')


@app.route('/images')
def list_images():
    names = os.listdir(SRC)
    sizes = [os.path.getsize(f'{SRC}/' + x) for x in names]
    sizes = [s/1e3 for s in sizes]

    times = [os.path.getmtime(f'{SRC}/' + x) for x in names]
    times = [datetime.datetime.fromtimestamp(ts) for ts in times]

    image_info = [dict(zip(['name', 'size_b', 't_modif'], tup)) for tup in zip(names, sizes, times)]
    image_info = sorted(image_info, key=lambda x: x['name'], reverse=True)
    return render_template("index.htm", image_info=image_info)


@app.route('/images/<path:filename>', methods=['GET', 'POST'])
def open_image(filename):
    return send_from_directory(directory='SRC', filename=filename)


@app.route('/images/rm<filename>', methods=['POST'])
def remove_image(filename):
    os.remove(SRC + '/' + filename)
    print(f'{filename} has been removed')
    return redirect('/images')


@app.route('/images/upload', methods=['POST'])
def convert_from_base64():
    string_data = request.form.get('string_image')
    new_name = get_next_imagename()
    try:
        fh = open(f"{SRC}/{new_name}", "wb")
        fh.write(base64.b64decode(string_data))
    except Exception:
        remove_image(new_name)
        return render_template('index.htm', error_msg='Wrong string format')
    finally:
        fh.close()
    return redirect('/images')


def get_next_imagename():
    names = os.listdir(SRC)
    matches = [re.search('img(\d{3}).jpg', s) for s in names]
    numbers = sorted([int(m.group(1)) for m in matches])
    return 'img'+str(numbers[-1]+1).zfill(3)+'.jpg'


if __name__ == '__main__':
    app.run(host="0.0.0.0")
