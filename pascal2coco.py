import xmltodict
import json
import tqdm
from glob import glob
import os

def xml_to_coco(xml_files):
    coco_format = {
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    category_set = set()
    annotation_id = 1
    image_id = 1
    
    for xml_file in tqdm.tqdm(xml_files):
        with open(xml_file) as fd:
            doc = xmltodict.parse(fd.read())
            image_info = {
                "id": image_id,
                "file_name": doc['annotation']['filename'],
                "width": int(float(doc['annotation']['size']['width'])),  # Convert to integer
                "height": int(float(doc['annotation']['size']['height']))  # Convert to integer
            }
            coco_format['images'].append(image_info)
            
            if isinstance(doc['annotation']['object'], list):
                objects = doc['annotation']['object']
            else:
                objects = [doc['annotation']['object']]
            
            for obj in objects:
                category_name = obj['name']
                category_set.add(category_name)
                
                annotation_info = {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": None,  # To be updated after categories are added
                    "bbox": [
                        int(float(obj['bndbox']['xmin'])),
                        int(float(obj['bndbox']['ymin'])),
                        int(float(obj['bndbox']['xmax'])) - int(float(obj['bndbox']['xmin'])),
                        int(float(obj['bndbox']['ymax'])) - int(float(obj['bndbox']['ymin']))
                    ],
                    "area": (int(float(obj['bndbox']['xmax'])) - int(float(obj['bndbox']['xmin']))) * (int(float(obj['bndbox']['ymax'])) - int(float(obj['bndbox']['ymin']))),
                    "iscrowd": 0
                }
                coco_format['annotations'].append(annotation_info)
                annotation_id += 1
            
            image_id += 1
    
    # Add categories to coco_format
    for i, category_name in enumerate(category_set, start=1):
        coco_format['categories'].append({"id": i, "name": category_name})
    
    # Update category IDs in annotations
    category_name_to_id = {category['name']: category['id'] for category in coco_format['categories']}
    for annotation in coco_format['annotations']:
        annotation['category_id'] = category_name_to_id[obj['name']]
    
    return coco_format

# Specify your directory containing XML files
# xml_files_directory = 'path/to/your/xml/files'
xml_files_directory = 'Annotations'
xml_files = glob(os.path.join(xml_files_directory, '*.xml'))

coco_data = xml_to_coco(xml_files)

# Save to JSON
with open('output_coco_format.json', 'w') as json_file:
    json.dump(coco_data, json_file, indent=4)
