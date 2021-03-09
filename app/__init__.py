from flask import Flask
try:
    from flask_cors import CORS, cross_origin
except:
    print("can't import flask_cors")
import os

app = Flask(__name__)
try:
    cors = CORS(app, resources=r'/*')
    app.config['CORS_HEADERS'] = 'Content-Type'
except:
    print("flask_cors not imported")

app.secret_key = os.environ['SECRET_KEY']

from app import routes