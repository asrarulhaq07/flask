# Flask app
from flask import Flask, render_template, request, redirect, url_for, session
from importlib import reload
from werkzeug.utils import secure_filename
import sqlite3
import pytesseract
from PIL import ImageFilter, Image
import os
import sys

reload(sys)
# if no media folder, create one
if not os.path.isdir('media'):
    os.mkdir('media')

# if no database, create one
if not os.path.isfile('IITDELHI.db'):
    conn = sqlite3.connect('IITDELHI.db')
    c = conn.cursor()
    # create database that saves hash of image and text
    c.execute('''CREATE TABLE IITDELHI (id,hash text, image text)''')
    conn.commit()
    conn.close()

# if no templates folder, create one
if not os.path.isdir('templates'):
    os.mkdir('templates')
app=Flask(__name__, template_folder='templates', static_folder='static')
app.config['UPLOAD_FOLDER'] = 'media'



# home page
@app.route('/')
def index():
    return render_template('index.html')

# submit page
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    # if no file uploaded, redirect to home page
    if 'file' not in request.files:
        alert='No file uploaded'
        return redirect(url_for('index'))
    file=request.files['file']
    # Allow only images and pdfs
    if file.filename.split('.')[-1] in ['jpg', 'jpeg', 'png', 'pdf']:
        filename=secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # if pdf, convert to image
        if filename.split('.')[-1] == 'pdf':
            os.system('convert media/'+filename+' media/'+filename.split('.')[0]+'.jpg')
            filename=filename.split('.')[0]+'.jpg'
            # save image in database
            conn = sqlite3.connect('IITDELHI.db')
            c = conn.cursor()
            c.execute("INSERT INTO IITDELHI VALUES (?,?,?)", (None, filename.split('.')[0], filename))
            conn.commit()
            conn.close()
        # if image, save in database
        else:
            conn = sqlite3.connect('IITDELHI.db')
            c = conn.cursor()
            c.execute("INSERT INTO IITDELHI VALUES (?,?,?)", (None, filename.split('.')[0], filename))
            conn.commit()
            conn.close()
    filename=secure_filename(file.filename)
    # text segmentation of using unet model
    os.system('python3 text_segmentation.py --image media/'+filename)
    # text recognition using tesseract
    os.system('tesseract media/'+filename.split('.')[0]+'_segmented.jpg media/'+filename.split('.')[0]+'_segmented')
    # read text from file
    with open('media/'+filename.split('.')[0]+'_segmented.txt', 'r') as f:
        text=f.read()
    # if no text, redirect to home page
    if text=='':
        alert='No text detected'
        return redirect(url_for('index'))
    # if text, redirect to result page
    else:
        return redirect(url_for('result', filename=filename))

# result page
@app.route('/result/<filename>')
def result(filename):
    # read text from file
    with open('media/'+filename.split('.')[0]+'_segmented.txt', 'r') as f:
        text=f.read()
    return render_template('result.html', text=text)

# run app
if __name__ == '__main__':
    app.run('0.0.0.0',8000, debug=True)
