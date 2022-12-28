from flask import Flask
from importlib import reload
from flask import request,redirect,render_template,url_for
from werkzeug.utils import secure_filename
import sqlite3
import pytesseract
from PIL import Image
import os

import sys
reload(sys)
# sys.setdefaultencoding('utf8')

app = Flask(__name__, static_url_path='', static_folder='media')
app.config['UPLOAD_FOLDER'] = './media'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submitImage/',methods=['POST',])
def submitImage():
    image = request.files['ocrImage']
    text = ''
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    text = pytesseract.image_to_string(img)
    f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename)+'.txt','w')
    f.write(text)
    f.close()
    conn = sqlite3.connect('TextExtractor.db')
    c = conn.cursor()
    c.execute("INSERT INTO TextExtractor (filename,text) VALUES (?,?)",(filename,text))
    conn.commit()
    conn.close()
    return render_template('textFile.html',text=text,filename=f)

@app.route('/history',methods=['GET',])
def history():
    conn = sqlite3.connect('TextExtractor.db')
    c = conn.cursor()
    c.execute("SELECT * FROM TextExtractor")
    data = c.fetchall()
    return render_template('history.html',data=data)


if __name__ == '__main__':
    app.run('0.0.0.0',8000, debug=True)
