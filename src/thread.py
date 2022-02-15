import logging
import ee
import numpy as np
import rasterio
import os
from google.cloud import storage
import google.auth
import re
import glob
import pandas as pd
import time

credentials, project = google.auth.default()

EXAMPLE_CODE = """
def f(curr, nei):
  return (curr["elv"] > nei["elv"])
formula = f
"""

CONDITIONS = [{"band": ["0_elv"], "rule": EXAMPLE_CODE}]
FILEPATH = "data/flow"
RE_BUCKET = re.compile("gs://([^/]+)/(.*)")
GCP_BUCKET = "nish-earthengine"

ee.Initialize()


def get_bounds():
  stateFilter = ee.Filter.equals("STUSPS", "NC")
  NC = ee.FeatureCollection('TIGER/2016/States').filter(stateFilter)
  return NC


def export_data(img=ee.Image("MERIT/Hydro/v1_0_1"), bands=["elv"]):
  NC = get_bounds()
  dataset = ee.Image(img.clip(NC).select(bands))
  task_config = {
      'description': 'FlowElevation',
      'bucket': GCP_BUCKET,
      'scale': 90,
      'skipEmptyTiles': True,
      "region": NC.geometry().bounds(),
  }
  task = ee.batch.Export.image.toCloudStorage(dataset, **task_config)
  task.start()
  return task


def poll_earthengine(task):
  while task.status()['state'] in ['READY', 'RUNNING']:
    print(task.status())
    time.sleep(10)
  else:
    return task.status()


def download_dataset(collections):
  items = []
  selected_bands = []
  for i, (ee_type, collection, bands) in enumerate(collections):
    for band in bands:
      selected_bands.append(str(i) + "_" + band)
    if ee_type == "image":
      curr_img = ee.Image(collection)
      items.append(curr_img)
    else:
      pass
  ic = ee.ImageCollection(ee.List(items))
  img = ic.toBands()
  return export_data(img, selected_bands)


def parse_condition(condition):
  return condition["band"], condition["rule"]


def get_band_index(bands, band_list):
  indices = []
  try:
    for band in band_list:
      pos = bands.index(band)
      indices.append(pos)
    return indices
  except ValueError as e:
    raise ValueError(f"Band does not exist {band} \n Error: {e}")


def satisfy_conditions(node, nei, layers, bands, conditions):
  for condition in conditions:
    band_list, rule = parse_condition(condition)
    positions = get_band_index(bands, band_list)
    try:
      if rule == "<":
        layer = layers[positions[0]]
        if layer[node[1]][node[0]] > layer[nei[1]][nei[0]]:
          return False
      elif rule == ">":
        layer = layers[positions[0]]
        if layer[node[1]][node[0]] < layer[nei[1]][nei[0]]:
          return False
      else:
        ex_locals = {}
        exec(rule, None, ex_locals)
        curr, nei = dict(), dict()
        for i, band in enumerate(band_list):
          curr[band] = layers[positions[i]][node[1]][node[0]]
          nei[band] = layers[positions[i]][nei[1]][nei[0]]
        if not ex_locals["formula"](curr, nei):
          return False
    except Exception as e:
      return False
  return True


def upload_blob(bucket_name, source_file_name, destination_blob_name):
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(destination_blob_name)
  blob.upload_from_filename(source_file_name)
  print('File {} uploaded to {}.'.format(source_file_name,
                                         destination_blob_name))


def get_data(uri):
  if uri.startswith("gs://"):
    m = RE_BUCKET.search(uri)
    if not m:
      raise ValueError("uri parameter doesn't parse: %s" % uri)
    bucket_name = m.groups()[0]
    blob_name = m.groups()[1]
    bucket = storage.Client().bucket(bucket_name)
    blob = bucket.blob(blob_name)
    # It says string, but in python3, it's really bytes.
    # so convert to a unicode string and return that.
    blob_bytes = blob.download_as_string()
    return blob_bytes
  else:
    raise ValueError("Not GS Path!")
  return data


def files_in_dir(dir_path: str, extension: str = ""):
  paths = []
  if dir_path.startswith("gs://"):
    if dir_path.endswith("/"):
      dir_path = dir_path[:-1]
    m = RE_BUCKET.search(dir_path)
    if not m:
      raise ValueError("directory doesn't parse: %s" % dir_path)
    bucket_name = m.groups()[0]
    internal_path = m.groups()[1]
    bucket = storage.Client().get_bucket(bucket_name)
    for blob in bucket.list_blobs(prefix=internal_path):
      if extension and not blob.name.endswith(extension):
        continue
      paths.append("gs://" + bucket_name + "/" + blob.name)
    if dir_path + "/" in paths:
      paths.remove(dir_path + "/")
  else:
    if os.path.isfile(dir_path):
      return []
    extension_val = extension if extension else ""
    to_import = glob.glob(dir_path + "/**/*" + extension_val, recursive=True)
    paths.extend(to_import)
  return paths


def simulate(layers, state, queue, visited, iterations, bands, tiff_metadata,
             conditions, filepath, threshold):
  for i in range(iterations):
    next_round = set()
    while queue:
      node = queue[-1]
      neighbors = pixel_neighbours(state, node)
      if neighbors is None:
        queue.pop(-1)
        continue
      for nei in neighbors:
        if (nei[0], nei[1]) in visited:
          continue
        if satisfy_conditions(node, nei, layers, bands, conditions):
          state[nei[1]][nei[0]] = max(state[nei[1]][nei[0]],
                                      state[node[1]][node[0]] * threshold)
          if (nei[0], nei[1]) not in next_round:
            next_round.add((nei[0], nei[1]))
      queue.pop(-1)
    queue = list(next_round)
    visited.update(next_round)
    filepath_with_index = os.path.join(filepath, str(i) + ".tif")
    with rasterio.open(filepath_with_index, 'w', **tiff_metadata) as dataset:
      dataset.write(state, 1)
    upload_blob(GCP_BUCKET, filepath_with_index, filepath_with_index)
    # yield filepath_with_index


def pixel_neighbours(im, p):
  rows, cols = im.shape
  i, j = p[1], p[0]
  rmin = i - 1 if i - 1 >= 0 else 0
  rmax = i + 1 if i + 1 < rows else i
  cmin = j - 1 if j - 1 >= 0 else 0
  cmax = j + 1 if j + 1 < cols else j
  neighbours = []
  for x in range(rmin, rmax + 1):
    for y in range(cmin, cmax + 1):
      neighbours.append([y, x])
  try:
    neighbours.remove([p[0], p[1]])
    return neighbours
  except:
    return None


def get_percentage(state):
  return np.sum(state) / (state.shape[0] * state.shape[1])


def thread_model(bounding_boxes,
                 filepath=FILEPATH,
                 conditions=CONDITIONS,
                 tiff="gs://nish-earthengine/FlowElevation.tif"):

  if not os.path.exists(filepath):
    os.makedirs(filepath)
  localtif = os.path.join("tiff", os.path.basename(tiff))
  with open(localtif, "wb") as file_handler:
    file_handler.write(get_data(tiff))
  with rasterio.open(localtif, "r") as reader:
    data = reader.read()
    profile = reader.profile
    descriptions = reader.descriptions
    state = np.zeros(data.shape)[0]
    queue = []
    visited = set()
    for bounding_box in bounding_boxes:
      upper_left, lower_right = bounding_box[0], bounding_box[1]
      ly, lx = reader.index(upper_left[0], upper_left[1])
      ry, rx = reader.index(lower_right[0], lower_right[1])
      state[ly:ry + 1, lx:rx + 1] = 1
      for i in range(lx, rx + 1):
        queue.append((i, ly))
        queue.append((i, ry))
      for i in range(ly, ry + 1):
        queue.append((lx, i))
        queue.append((rx, i))
      for i in range(lx, rx):
        for j in range(ly, ry):
          visited.add((i, j))
    visited.update(queue)
    simulate(layers=data,
             state=state,
             queue=queue,
             visited=visited,
             iterations=5,
             bands=descriptions,
             tiff_metadata=profile,
             conditions=conditions,
             filepath=filepath,
             threshold=0.95)
    return len(files_in_dir(filepath, extension=".tif"))


def create_ic(directory):
  images = []
  for geotiff in files_in_dir(directory, extension=".tif"):
    images.append(ee.Image.loadGeoTIFF(geotiff))
  ic = ee.List(images)
  return ic


def get_ee_layer(image):
  visParams = {
      "min": 0,
      "max": 1,
      "palette": ["white", "CFF7E1", "8CFFC0", "69E2A0", "26A560", "1D6E42"]
  }
  return image.getMapId(visParams)['tile_fetcher'].url_format


def get_tile_url(id, directory="gs://nish-earthengine/data"):
  ic = ee.Image(create_ic(directory).get(id))
  ic = ic.mask(ic)
  return get_ee_layer(ic)


def get_sentinel():

  def maskS2clouds(image):
    qa = image.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(
        qa.bitwiseAnd(cirrusBitMask).eq(0))
    return image.updateMask(mask).divide(10000)

  NC = get_bounds()
  dataset = ee.ImageCollection('COPERNICUS/S2_SR')\
      .filterDate('2020-01-01', '2020-03-30')\
      .filterBounds(NC).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))\
      .map(maskS2clouds)

  viz = {
      "min": 0.0,
      "max": 0.3,
      "bands": ['B4', 'B3', 'B2'],
  }
  image = dataset.median().clip(NC)
  return image.getMapId(viz)['tile_fetcher'].url_format


def create_bounding_boxes(csvFile):
  hogs = pd.read_csv(csvFile, skiprows=2)
  hogs = hogs[hogs["Location Lat Num"].notnull()]

  def get_box(row):
    lat, lon = row["Location Lat Num"], row["Location Long Num"]
    upper_left = lon - 0.01, lat + 0.01
    lower_right = lon + 0.01, lat - 0.01
    return [upper_left, lower_right]

  bounding_boxes = hogs.apply(lambda x: get_box(x), axis=1)
  bbs = []
  for bb in bounding_boxes:
    if all(bb[0]) and all(bb[1]) and bb[0][0] != float('nan'):
      bbs.append(bb)
  return bbs


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  # #[[(-79.81, 35.938), (-79.524, 35.661)]]
  bounding_boxes = create_bounding_boxes("hog.csv")
  # # print(bounding_boxes)
  thread_model(bounding_boxes)
  # # print(get_tile_url(49))
  # collections = [("image", "MERIT/Hydro/v1_0_1", ["elv"])]
  # download_dataset(collections)
