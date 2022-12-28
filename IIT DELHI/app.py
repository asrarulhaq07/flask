# Flask app
from flask import Flask, render_template, request, redirect, url_for, session
import MySQLdb.cursors
import os
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
from PIL import Image as PI