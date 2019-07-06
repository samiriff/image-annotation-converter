import json
import base64
from pathlib import Path
import matplotlib.image as mpimg
from tqdm import tqdm
import argparse
import sys


def get_pascal_json(via_json, path=Path('.'), label_mapper=None):
    pascal_json = {}
    pascal_json['version'] = '3.16.1'
    pascal_json['flags'] = {}
    pascal_json['shapes'] = get_pascal_shapes_json(via_json, label_mapper)
    pascal_json['lineColor'] = [0, 255, 0, 128]
    pascal_json['fillColor'] = [255, 0, 0, 128]
    pascal_json['imagePath'] = via_json['filename']
    with open(path / via_json['filename'], 'rb') as f:
        pascal_json['imageData'] = f.read()
        pascal_json['imageData'] = base64.b64encode(pascal_json['imageData']).decode('utf-8')
    img = mpimg.imread(path / via_json['filename'])
    pascal_json['imageHeight'] = img.shape[0]
    pascal_json['imageWidth'] = img.shape[1]
    return pascal_json


def get_region_attributes_label(via_region_attributes, label_mapper=None, filename='unknown'):
    try:
        if label_mapper is None:
            return str(via_region_attributes)
        else:
            return label_mapper(via_region_attributes)
    except Exception as e:
        print('Unable to find label for', filename, 'with exception', e)
        sys.exit(1)


def get_pascal_shapes_json(via_json, label_mapper=None):
    pascal_shapes = []
    for region, attributes in via_json['regions'].items():
        via_shape_attributes = attributes['shape_attributes']
        via_region_attributes = attributes['region_attributes']
        pascal_shape = {}
        pascal_shape['shape_type'] = via_shape_attributes['name']
        pascal_shape['label'] = get_region_attributes_label(via_region_attributes, label_mapper, via_json['filename'])
        pascal_shape['line_color'] = None
        pascal_shape['fill_color'] = None
        pascal_shape['flags'] = {}

        pascal_shape_points = []
        pascal_shape['points'] = pascal_shape_points
        for x, y in zip(via_shape_attributes['all_points_x'], via_shape_attributes['all_points_y']):
            pascal_shape_points.append([x, y])
        pascal_shapes.append(pascal_shape)
    return pascal_shapes


def generate_pascal_json_file(via_json, path=Path('.'), label_mapper=None):
    pascal_json = get_pascal_json(via_json, path, label_mapper)
    json_filename = ''.join(via_json['filename'].split('.')[:-1] + ['.json'])
    with open(path / json_filename, 'w') as json_file:
        json.dump(pascal_json, json_file, indent=4)


def generate_pascal_json_files(path=Path('.'), jsonPath=Path('.'), label_mapper=None):
    full_via_json = json.loads(open(jsonPath).read())
    for _, via_json in tqdm(full_via_json.items()):
        generate_pascal_json_file(via_json, path, label_mapper)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Convert Image Annotations made with the VIA tool
        into Image Annotations compatible with the LabelMe tool''')
    parser.add_argument('inputdir', type=str, help='Path to Directory containing images annotated with the VIA tool')
    parser.add_argument('inputjson', type=str, help='Path to JSON file containing all annotations')
    args = parser.parse_args()
    generate_pascal_json_files(Path(args.inputdir), Path(args.inputjson))
