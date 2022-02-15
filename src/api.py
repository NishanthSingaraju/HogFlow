import os
import json
import rasterio
import random

from flask import Flask, request
from flask_cors import CORS
import thread
import threading
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

DIRECTORY = "gs://" + os.path.join(thread.GCP_BUCKET, thread.FILEPATH)
UPLOAD_FOLDER = 'data'
CLOUDTIFF = "gs://nish-earthengine/FlowElevation.tif"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
exporting_jobs = dict()


@app.route('/api/process', methods=["PUT"])
def process():
  file = request.files['file']
  if file:
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
  else:
    return {"message": "No File Upload"}

  conditions = json.loads(request.form.get('conditions'))
  filepath = os.path.join(thread.FILEPATH, str(random.randint(0, 1000)))
  spreadThread = SpreadThread(4, filepath)
  exporting_jobs["process"] = spreadThread
  exporting_jobs["process"].start()
  thread.thread_model(bounding_boxes=thread.create_bounding_boxes(
      os.path.join(app.config['UPLOAD_FOLDER'], filename)),
                      conditions=conditions,
                      filepath=filepath)

  return {"message": "SUCCESS"}


@app.route('/api/progress', methods=["GET"])
def process_progress():
  global exporting_jobs
  return {"progress": exporting_jobs["process"].progress}


@app.route('/api/bands', methods=["GET"])
def get_bands():
  localtif = os.path.join("tiff", os.path.basename(CLOUDTIFF))
  with open(localtif, "wb") as file_handler:
    file_handler.write(thread.get_data(CLOUDTIFF))
  with rasterio.open(localtif, "r") as reader:
    descriptions = reader.descriptions
  return {"bands": descriptions}


@app.route('/download/data', methods=["GET"])
def download_dataset():
  global exporting_jobs
  # collections = json.loads(request.data)["collections"]
  task = thread.download_dataset([("image", "MERIT/Hydro/v1_0_1", ["elv"])])
  downloadThread = DownloadThread(task)
  exporting_jobs["download"] = downloadThread
  exporting_jobs["download"].start()
  return {"message": "SUCCESS"}


@app.route('/download/progress', methods=["GET"])
def download_progress():
  global exporting_jobs
  return {"progress": str(exporting_jobs["download"].progress)}


@app.route('/api/URL', methods=["PUT"])
def get_current_url():
  if request.get_json().get("id", 0):
    id = request.get_json()["id"]
  else:
    id = 4
  return {"url": thread.get_tile_url(id=id, directory=DIRECTORY)}


@app.route('/api/sentinel', methods=["GET"])
def get_sentinel_url():
  return {"url": thread.get_sentinel()}


class DownloadThread(threading.Thread):

  def __init__(self, task):
    self.progress = 'STARTING'
    self.task = task
    super().__init__()

  def run(self):
    # Your exporting stuff goes here ...
    while self.progress in ['STARTING', 'READY', 'RUNNING']:
      self.progress = self.task.status()['state']


class SpreadThread(threading.Thread):

  def __init__(self, num_images, dir_path):
    self.progress = 0
    self.num_images = num_images - 1
    self.dir_path = dir_path
    super().__init__()

  def run(self):
    # Your exporting stuff goes here ...
    while self.progress < self.num_images - 1:
      try:
        self.progress = int(
            os.path.splitext(
                os.path.basename(
                    thread.files_in_dir(dir_path=self.dir_path,
                                        extension=".tif")[-1]))[0])
      except:
        self.progress = 0

    self.progress = -1
