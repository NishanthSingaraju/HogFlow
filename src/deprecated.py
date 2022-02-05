import ee
import thread

def water_flow(image):
    image = image.select("visited")
    pass

def thread_model(boxes, probability):
    NC = thread.get_bounds()
    img = ee.Image("MERIT/Hydro/v1_0_1").clip(NC)
    possible_values = propogate(img, probability)
    pass

def propogate(image, probability):
    NC = thread.get_bounds()
    prob = ee.Image.constant(probability).clip(NC)
    visited = image.select("visited")
    return visited.multiply(prob)

def convert_bb_to_image(bounding_boxes):
    rectangles = []
    for bounding_box in bounding_boxes:
        rectangle = ee.Geometry.Rectangle(bounding_box)
        feature = ee.Feature(rectangle, {"pollution": 1})
        rectangles.append(feature)
    fc = ee.FeatureCollection(ee.List(rectangles))
    roi_image = ee.Image(0).clip(thread.get_bounds())
    feature_image = ee.Image(1).clip(fc)
    binary_image = roi_image.where(test=feature_image,value=feature_image)
    return binary_image
