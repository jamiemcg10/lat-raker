from flask import Flask
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.secret_key = os.environ['SECRET_KEY']

from app import routes