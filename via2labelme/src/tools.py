import json
import base64
from pathlib import Path
import matplotlib.image as mpimg
from tqdm import tqdm
import argparse


def get_pascal_json(via_json, path=Path('.')):
    pascal_json = {}
    pascal_json['version'] = '3.16.1'
    pascal_json['flags'] = {}
    pascal_json['shapes'] = get_pascal_shapes_json(via_json)
    lineColor_json = [0, 255, 0, 128]
    pascal_json['lineColor'] = lineColor_json
    fillColor_json = [255, 0, 0, 128]
    pascal_json['fillColor'] = fillColor_json
    pascal_json['imagePath'] = via_json['filename']
    with open(path / via_json['filename'], 'rb') as f:
        pascal_json['imageData'] = f.read()
        pascal_json['imageData'] = base64.b64encode(pascal_json['imageData']).decode('utf-8')
    img = mpimg.imread(path / via_json['filename'])
    pascal_json['imageHeight'] = img.shape[0]
    pascal_json['imageWidth'] = img.shape[1]
    return pascal_json


def get_pascal_shapes_json(via_json):
    pascal_shapes = []
    for region, attributes in via_json['regions'].items():
        via_shape_attributes = attributes['shape_attributes']
        via_region_attributes = attributes['region_attributes']
        pascal_shape = {}
        pascal_shape['shape_type'] = via_shape_attributes['name']
        pascal_shape['label'] = via_region_attributes['anomaly']
        pascal_shape['line_color'] = None
        pascal_shape['fill_color'] = None
        pascal_shape['flags'] = {}

        pascal_shape_points = []
        pascal_shape['points'] = pascal_shape_points
        for x, y in zip(via_shape_attributes['all_points_x'], via_shape_attributes['all_points_y']):
            pascal_shape_points.append([x, y])
        pascal_shapes.append(pascal_shape)
    return pascal_shapes


def generate_pascal_json_file(via_json, path=Path('.')):
    pascal_json = get_pascal_json(via_json, path)
    json_filename = ''.join(via_json['filename'].split('.')[:-1] + ['.json'])
    with open(path / json_filename, 'w') as json_file:
        json.dump(pascal_json, json_file, indent=4)


def generate_pascal_json_files(path=Path('.'), jsonPath=Path('.')):
    full_via_json = json.loads(open(jsonPath).read())
    for _, via_json in tqdm(full_via_json.items()):
        generate_pascal_json_file(via_json, path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Convert Image Annotations made with the VIA tool
        into Image Annotations compatible with the LabelMe tool''')
    parser.add_argument('inputdir', type=str, help='Path to Directory containing images annotated with the VIA tool')
    parser.add_argument('inputjson', type=str, help='Path to JSON file containing all annotations')
    args = parser.parse_args()
    generate_pascal_json_files(args.inputdir, args.inputjson)
