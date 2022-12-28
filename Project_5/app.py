import os
from flask import Flask, render_template, request
from wand.image import Image
from PyPDF2 import PdfFileReader, PdfFileWriter

__author__ = 'EME'

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Function for preparing images from pdf
def prepare_images(pdf_path):
    # Output dir
    output_dir = os.path.join(APP_ROOT, 'static/pdf_image/')

    with(Image(filename=pdf_path, resolution=300, width=600)) as source:
        images = source.sequence
        pages = len(images)
        for i in range(pages):
            Image(images[i]).save(filename=output_dir + str(i) + '.png')

# App routing
@app.route('/')
def main():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    pdf_target = os.path.join(APP_ROOT, 'static/pdf')

    # Preparing directory
    if not os.path.isdir(pdf_target):
        os.mkdir(pdf_target)

    # Uploading File
    for file in request.files.getlist('file'):
        filename = file.filename
        destination = "/".join([pdf_target,filename])
        file.save(destination)

        # Creating images
        if os.path.isfile(destination):
            prepare_images(destination)

    return render_template('completed.html')


if __name__ == '__main__':
    app.run()