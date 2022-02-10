import time
import os

from flask import Flask, request
from flask_cors import CORS

from thread import thread_model

app = Flask(__name__)
CORS(app)

URL = "https://earthengine.googleapis.com/v1alpha/projects/earthengine-legacy/" \
      "maps/b153ef01dae468946a436c5ddd0a4f19-9a25fb1901b23fa711da1a5a9aa8b36d/" \
      "tiles/{z}/{x}/{y}"

@app.route('/api/URL', methods=["PUT"])
def get_current_url():
    return {'url': URL}

