from pathlib import Path
import os

import deepfinder.utils.common as cm
import numpy as np
# dataset = Path('/home/amasson/storage/exocytosis/exocytose/dataset/dataset/')
dataset = Path('/home/amasson/storage/exocytosis/dataset/valid/')

# for image in sorted(list(dataset.iterdir())):
targets = sorted(list(dataset.glob('*_target.h5')))
print(len(targets))
for image in targets:
    # target = image / 'target.h5'
    # print(image.name, ':', target.exists())
    print('\n\n\n--------')
    print(image)
    ee = image.parent / f'{image.stem}_exocytosis_events.h5'
    # ee.rename(image.parent / f'{image.stem}_exocytosis_events.h5')
    # print( os.path.getsize(str(image.parent / f'{image.stem}_exocitosis_events.h5')) )
    # if not (image.parent / f'{image.stem}_exocitosis_events.h5').exists():
    #     raise Exception('bad')


    labelmap = cm.read_array(str(image))
    # print('shape:', labelmap.shape)
    # print('non zeros:', np.count_nonzero(labelmap))
    # print('0:', np.count_nonzero(labelmap==0))
    # print('1:', np.count_nonzero(labelmap==1))
    # print('2:', np.count_nonzero(labelmap==2))
    print('max:', labelmap.max())
    print('dtype:', labelmap.dtype)

    # labelmap[labelmap == 1] = 0
    # labelmap[labelmap == 2] = 1
    cm.write_array(labelmap.astype(np.uint8), str(ee))