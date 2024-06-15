import argparse
import sys
from pathlib import Path
import numpy as np
from deepfinder.training import TargetBuilder
import deepfinder.utils.common as cm
import deepfinder.utils.objl as ol

# path_output.mkdir(exist_ok=True, parents=True)

# First, define the (t,y,x) mask for exocytosis event:
def get_exo_mask():
    # Here we construct the mask frame per frame
    # The mask is a cone whose radius has exponential decay
    # 1st frame is disk with r=4,
    # 2nd frame is disk with r=2,
    # 3rd and last frame is disk with r=1
    r = 4
    mask_shape = [2 * r + 1, 2 * r + 1, 2 * r + 1]

    # 1st frame (to create a disk mask we exploit a function that creates spheres)
    mask_sphere = cm.create_sphere(mask_shape, r)  # result here is a binary map of a 3d sphere
    mask_t0 = mask_sphere[r, :, :]  # result here is a binary map of a 2D disk

    # 3nd frame
    mask_sphere = cm.create_sphere(mask_shape, np.round(r / 2))
    mask_t1 = mask_sphere[r, :, :]

    # 3rd frame
    mask_t2 = np.zeros((mask_shape[0], mask_shape[1]))
    mask_t2[r, r] = 1

    # Merge frames
    mask = np.zeros(mask_shape)
    mask[r, :, :] = mask_t0
    mask[r + 1, :, :] = mask_t1
    mask[r + 2, :, :] = mask_t2

    return mask

def generate_segmentation(image_path, object_list_path, output_path):

    image = cm.read_array(str(image_path))
    data_shape = image.shape  # shape of image sequence [t,y,x]

    mask_exo = get_exo_mask()

    # Next, read object list:
    objl = ol.read_xml(object_list_path)

    for i, obj in enumerate(objl):
        if obj['label']>1:
            sys.exit(f'Error: object {i} has label greater than 1: ', obj['label'])

    # Then, initialize target generation task:
    tbuild = TargetBuilder()

    # Initialize target array. Here, we initialize it with an empty array. But it could be initialized with a segmentation map containing other (non-overlapping) classes.
    initial_vol = np.zeros(data_shape)

    # Run target generation:

    target = tbuild.generate_with_shapes(objl, initial_vol, [mask_exo])
    # cm.plot_volume_orthoslices(target, str(path_output / 'orthoslices_target.png'))

    # Save target:
    cm.write_array(target, str(output_path))

if __name__ == '__main__':

    parser = argparse.ArgumentParser('Convert annotations to segmentations', description='Convert an annotation file (.xml generated with napari-exodeepfinder) into a segmentation.')

    parser.add_argument('-i', '--image', 'Path to the input image. If the path is a folder, all .h5 images will be processed expect the ones ending with "_segmentation.h5" ; and the --annotation and --segmentation inputs will be ignored.')
    parser.add_argument('-a', '--annotation', 'Path to the corresponding annotation (.xml generated with napari-exodeepfinder). Default is "[input_image]_expert_annotations.xml".', default=None)
    parser.add_argument('-s', '--segmentation', 'Path to the output segmentation. Default is "[input_image]_expert_segmentation.h5".', default=None)

    args = parser.parse_args()

    image_path = Path(args.image)
    image_paths = list(set(image_path.glob('*.h5')) - set(image_path.glob('*_segmentation.h5'))) if image_path.is_dir() else [image_path]

    for image_path in image_paths:
        # path to object list containing annotated positions
        object_list_path = image_path.parent / f'{image_path.stem}_expert_annotations.xml' if args.annotation is None or image_path.is_dir() else args.annotation
        output_path = image_path.parent / f'{image_path.stem}_expert_segmentation.h5' if args.segmentation is None or image_path.is_dir() else args.segmentation
        generate_segmentation(image_path, object_list_path, output_path)

