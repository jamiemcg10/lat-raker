from flask import Flask
from flask_talisman import Talisman
import os

try:
    from flask_cors import CORS, cross_origin
except:
    print("can't import flask_cors")
import os

app = Flask(__name__)

# if (os.environ['ENV'] == 'prod'):
#     ## set access
#     csp = {
#         'default-src': [
#             '\'self\'',
#             'https://cdn.jsdelivr.net'
#         ],
#         'script-src': [
#             '\'self\'',
#             'https://ajax.googleapis.com', 
#             'https://cdn.lr-ingest.io'
#         ],
#         'style-src': '*'
#     }
#     Talisman(
#         app, 
#         content_security_policy=csp,
#         content_security_policy_nonce_in=['script-src'])

try:
    cors = CORS(app, resources=r'/*')
    app.config['CORS_HEADERS'] = 'Content-Type'
except:
    print("flask_cors not imported")

app.secret_key = os.environ['SECRET_KEY']

from app import routes