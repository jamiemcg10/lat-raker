from flask import Flask
from flask_talisman import Talisman
import os

try:
    from flask_cors import CORS, cross_origin
except:
    print("can't import flask_cors")
import os

app = Flask(__name__)

if (os.environ['ENV'] == 'prod'):
    Talisman(app,content_security_policy=None)

try:
    cors = CORS(app, resources=r'/*')
    app.config['CORS_HEADERS'] = 'Content-Type'
except:
    print("flask_cors not imported")

app.secret_key = os.environ['SECRET_KEY']

from app import routes