import time
import os

from flask import Flask, request
from flask_cors import CORS

import thread

app = Flask(__name__)
CORS(app)

DIRECTORY = "gs://" + os.path.join(thread.GCP_BUCKET, thread.FILEPATH)


@app.route('/api/process', methods=["PUT"])
def process():
  conditions = eval(request.get_json()["conditions"])
  thread.thread_model(bounding_boxes=thread.create_bounding_boxes(),
                      conditions=conditions)
  return {"message": "SUCCESS"}


@app.route('/api/URL', methods=["PUT"])
def get_current_url():
  return {"url": thread.get_tile_url(id=2, directory=DIRECTORY)}


@app.route('/api/sentinel', methods=["GET"])
def get_sentinel_url():
  return {"url": thread.get_sentinel()}
