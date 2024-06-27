from deepfinder.commands import utils
utils.run_with_python_on_windows(__file__)
import sys
from pathlib import Path
import numpy as np
from deepfinder.training import TargetBuilder
import deepfinder.utils.common as cm
import deepfinder.utils.objl as ol
from gooey import Gooey


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

    if not object_list_path.exists():
        raise(Exception(f'The annotation file {object_list_path} does not exist.'))
    
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

utils.ignore_gooey_if_args()

def create_parser(parser=None, command=Path(__file__).stem, prog='Convert annotations to segmentations', description='Convert an annotation file (.xml generated with napari-exodeepfinder) into a segmentation.'):
    return utils.create_parser(parser, command, prog, description)

def add_args(parser):
    parser.add_argument('-m', '--movie', help='Path to the input movie.', default='movie.h5', type=Path, widget='FileChooser')
    parser.add_argument('-a', '--annotation', help='Path to the corresponding annotation (.xml generated with napari-exodeepfinder.', default='expert_annotation.xml', type=Path, widget='FileChooser')
    parser.add_argument('-s', '--segmentation', help='Path to the output segmentation.', default='expert_segmentation.h5', type=Path, widget='FileChooser')
    parser.add_argument('-b', '--batch', help='Path to the root folder containing all folders to process.', default=None, type=Path, widget='FileChooser')


@Gooey
def main(args=None):

    args = utils.parse_args(args, create_parser, add_args)
    
    folder_paths = Path(args.movie).parent if args.batch is None else sorted([d for d in args.batch.iterdir() if d.is_dir()])

    for folder_path in folder_paths:
        # path to object list containing annotated positions
        movie_path = folder_path / args.movie if args.batch is not None else args.movie
        object_list_path = folder_path / args.annotation if args.batch is not None else args.annotation
        output_path = folder_path / args.segmentation if args.batch is not None else args.segmentation
        generate_segmentation(movie_path, object_list_path, output_path)


if __name__ == '__main__':
    main()