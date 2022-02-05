import logging
import ee
import numpy as np
import rasterio
import os
from google.cloud import storage
import google.auth
import re
import glob
import time


credentials, project = google.auth.default()

ee.Initialize()
CONDITIONS = [
    "elv;<"
]
FILEPATH = "data/flow"
RE_BUCKET = re.compile("gs://([^/]+)/(.*)")
URL = ""

def get_bounds():
    stateFilter = ee.Filter.equals("STUSPS", "NC")
    NC = ee.FeatureCollection('TIGER/2016/States').filter(stateFilter)
    return NC

def export_data():
    NC = get_bounds()
    dataset = ee.Image(ee.Image("MERIT/Hydro/v1_0_1").clip(NC).select(["elv"]))
    task_config = {
        'description': 'FlowElevation',
        'scale': 90,
        'skipEmptyTiles': True,
        "region": NC.geometry().bounds(),
    }
    task = ee.batch.Export.image.toDrive(dataset, **task_config)
    task.start()

def parse_condition(condition):
     band, rule = condition.split(";")
     return band, rule

def get_band_index(bands, band):
    try:
        pos = bands.index(band)
        return pos
    except ValueError as e:
        raise ValueError("Band does not exist")

def satisfy_conditions(node, nei, layers, bands, conditions):
    for condition in conditions:
        band,rule = parse_condition(condition)
        pos = get_band_index(bands,band)
        layer = layers[pos]
        if rule == "<":
            if layer[node[1]][node[0]] > layer[nei[1]][nei[0]]:
                return False
        elif rule == ">":
            if layer[node[1]][node[0]] < layer[nei[1]][nei[0]]:
                return False
        else:
            continue
    return True

def upload_blob(bucket_name, source_file_name, destination_blob_name):
  storage_client = storage.Client()
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(destination_blob_name)
  blob.upload_from_filename(source_file_name)
  print('File {} uploaded to {}.'.format(
      source_file_name,
      destination_blob_name))

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

def simulate(layers, state, queue, iterations, bands, tiff_metadata, conditions, filepath,  threshold):
    visited = set()
    visited.update(queue)
    for i in range(iterations):
        next_round = set()
        while queue:
            node = queue[-1]
            neighbors = pixel_neighbours(state, node)
            for nei in neighbors:
                if (nei[0], nei[1]) in visited:
                    continue
                if satisfy_conditions(node, nei, layers, bands, conditions):
                    state[nei[1]][nei[0]] = max(state[nei[1]][nei[0]], state[node[1]][node[0]] * threshold)
                    if (nei[0], nei[1]) not in next_round:
                        next_round.add((nei[0], nei[1]))
            queue.pop(-1)
        queue = list(next_round)
        visited.update(next_round)
        filepath_with_index = os.path.join(filepath, str(i) + ".tif")
        with rasterio.open(filepath_with_index, 'w', **tiff_metadata) as dataset:
            dataset.write(state, 1)
        upload_blob("nish-earthengine", filepath_with_index, filepath_with_index)

def pixel_neighbours(im, p):
    rows, cols = im.shape
    i, j = p[0], p[1]
    rmin = i - 1 if i - 1 >= 0 else 0
    rmax = i + 1 if i + 1 < rows else i
    cmin = j - 1 if j - 1 >= 0 else 0
    cmax = j + 1 if j + 1 < cols else j
    neighbours = []
    for x in range(rmin, rmax + 1):
        for y in range(cmin, cmax + 1):
            neighbours.append([x, y])
    neighbours.remove([p[0], p[1]])
    return neighbours

def get_percentage(state):
    return np.sum(state)/(state.shape[0] * state.shape[1])

def thread_model(bounding_boxes, conditions=CONDITIONS):
    with rasterio.open("FlowElevation.tif", "r") as reader:
        data = reader.read()
        profile = reader.profile
        descriptions = reader.descriptions
        state = np.zeros(data.shape)[0]
        queue = []
        for bounding_box in bounding_boxes:
            upper_left, lower_right = bounding_box[0], bounding_box[1]
            ly, lx = reader.index(upper_left[0], upper_left[1])
            ry, rx = reader.index(lower_right[0], lower_right[1])
            state[ly:ry, lx:rx] = 1
            for i in range(lx,rx):
                queue.append((i, ly))
                queue.append((i, ry))
            for i in range(ly,ry):
                queue.append((lx, i))
                queue.append((ly, i))
        simulate(layers=data,
                 state=state,
                 queue=queue,
                 iterations=3,
                 bands=descriptions,
                 tiff_metadata=profile,
                 conditions=conditions,
                 filepath=FILEPATH,
                 threshold=0.95)
        return len(files_in_dir(FILEPATH, extension=".tif"))

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

def get_tile_url(id):
    ic = ee.Image(create_ic("gs://nish-earthengine/data").get(id))
    return get_ee_layer(ic)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    bounding_boxes = [[(-79.81, 35.938), (-79.524, 35.661)]]
    thread_model(bounding_boxes)







