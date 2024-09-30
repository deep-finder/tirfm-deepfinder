from deepfinder.commands import utils
utils.run_with_python_on_windows(__file__)
import csv
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

def getv(object, name):
    return object[name] if name in object else None

def read_csv(object_list_path):
    required_headers = ['tomo_idx', 'class_label', 'x', 'y', 'z']
    accepted_headers = ['tomo_idx', 'class_label', 'x', 'y', 'z', 'obj_id', 'psi', 'phi', 'the', 'cluster_size']
    with open(object_list_path, 'r', encoding='utf-8-sig') as csvfile:
        lines = list(csv.reader(csvfile))
        header = lines[0]
        for h in required_headers:
            if h not in header:
                sys.exit(f'Error: CSV file is missing header {h}')
        for h in header:
            if h not in accepted_headers:
                print(f'Warning! CSV file has unknown header {h}')
        objl = []
        for line in lines[1:]:
            vs = {header[i]:line[i] for i in range(len(header))}
            ol.add_obj(objl, tomo_idx=getv(vs, 'tomo_idx'), obj_id=getv(vs, 'obj_id'), label=int(getv(vs, 'class_label')), coord=(float(getv(vs, 'z')), float(getv(vs, 'y')), float(getv(vs, 'x'))), orient=(getv(vs, 'psi'),getv(vs, 'phi'),getv(vs, 'the')), cluster_size=getv(vs, 'cluster_size'))
        # objl = [{header[i]:line[i] for i in range(len(header))} for line in lines[1:]]
    return objl

def generate_segmentation(image_path, object_list_path, output_path):
    if output_path.suffix != '.h5':
        raise Exception(f'Error: {output_path} must end with .h5 since it will be saved in this format.')

    output_path = Path(str(output_path).replace('{movie.stem}', image_path.stem).replace('{movie.parent}', str(image_path.parent)))
    output_path.parent.mkdir(exist_ok=True, parents=True)

    if not object_list_path.exists():
        raise Exception(f'The annotation file {object_list_path} does not exist.')
    
    image = cm.read_array(str(image_path))
    data_shape = image.shape  # shape of image sequence [t,y,x]

    mask_exo = get_exo_mask()

    # Next, read object list:
    if object_list_path.suffix not in ['.xml', '.csv']:
        raise Exception(f'The annotation file {object_list_path} must be a .xml or .csv file.')

    objl = ol.read_xml(object_list_path) if object_list_path.suffix == '.xml' else read_csv(object_list_path)

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
    print(f'Saving segmentation file "{output_path.resolve()}"...')
    cm.write_array(target, str(output_path))

utils.ignore_gooey_if_args()

def create_parser(parser=None, command=Path(__file__).stem, prog='Convert annotations to segmentations', description='Convert an annotation file (.xml generated with napari-exodeepfinder) into a segmentation.'):
    return utils.create_parser(parser, command, prog, description)

def add_args(parser):
    parser.add_argument('-m', '--movie', help='Path to the input movie.', default='movie.h5', type=Path, widget='FileChooser')
    parser.add_argument('-a', '--annotation', help='Path to the corresponding annotation (.xml generated with napari-exodeepfinder or equivalent, can also be a .csv file).', default='expert_annotation.xml', type=Path, widget='FileChooser')
    parser.add_argument('-s', '--segmentation', help='Path to the output segmentation (in .h5 format). If used, the {movie.stem} string will be replaced by the --movie file name (without extension), and {movie.parent} by its parent folder.', default='{movie.parent}/expert_segmentation.h5', type=Path, widget='FileSaver')
    parser.add_argument('-b', '--batch', help='Path to the root folder containing all folders to process. If given, the --movie and --annotation arguments must be relative to the folder to process.', default=None, type=Path, widget='DirChooser')


@utils.Gooey
def main(args=None):

    args = utils.parse_args(args, create_parser, add_args)
    
    folder_paths = [Path(args.movie).parent] if args.batch is None else sorted([d for d in args.batch.iterdir() if d.is_dir()])

    for folder_path in folder_paths:
        # path to object list containing annotated positions
        movie_path = folder_path / args.movie if args.batch is not None else args.movie
        object_list_path = folder_path / args.annotation if args.batch is not None else args.annotation
        generate_segmentation(movie_path, object_list_path, args.segmentation)


if __name__ == '__main__':
    
    main()