import xml.etree.ElementTree as ET

def removeClass2(objl):
    # Parse the input file
    tree = ET.parse(str(objl))
    root = tree.getroot()

    # Remove elements with class_label="1"
    for obj in list(root):
        if obj.attrib.get('class_label') == '1':
            root.remove(obj)

    # Change class_label="2" to class_label="1"
    for obj in root.findall('object'):
        if obj.attrib.get('class_label') == '2':
            obj.set('class_label', '1')

    # Write the modified XML to a new file
    tree.write(objl.parent / f'{objl.stem}_exocytosis_events.xml', encoding='unicode', xml_declaration=True)

from pathlib import Path
# import deepfinder.utils.common as cm
# import numpy as np
# dataset = Path('/home/amasson/storage/exocytosis/exocytose/dataset/dataset/')
dataset = Path('/home/amasson/storage/exocytosis/dataset/valid/')

# for image in sorted(list(dataset.iterdir())):
targets = sorted(list(dataset.glob('*_objl.xml')))
print(len(targets))
for image in targets:
    # target = image / 'target.h5'
    # print(image.name, ':', target.exists())
    print('\n\n\n--------')
    print(image)
    removeClass2(image)