# =============================================================================================
# DeepFinder - a deep learning approach to detect exocytose events.
# =============================================================================================
# Copyright (C) Inria,  Emmanuel Moebel, Charles Kervrann, All Rights Reserved, 2015-2021, v1.0
# License: GPL v3.0. See <https://www.gnu.org/licenses/>
# =============================================================================================

from deepfinder.commands import utils
utils.run_with_python_on_windows(__file__)
from pathlib import Path
from deepfinder.inference import Cluster
import deepfinder.utils.common as cm
import deepfinder.utils.objl as ol
import numpy as np
import sys
from gooey import Gooey


def cluster(segmentation_path, cluster_radius, output_path=None, keep_labels_unchanged=False):
    output_path.parent.mkdir(exist_ok=True, parents=True)

    # Load data:
    labelmap = cm.read_array(str(segmentation_path))

    # Next, only keep the class of interest. In the experiments of the paper, class 0 is background,
    # class 1 is constant spot (docked vesicle), and class 2 is blinking spot (exocytosis event).
    # Below we convert to an array with only class 0 as background and class 1 as constant spot:
    labelmap.setflags(write=1)
    if not keep_labels_unchanged:
        labelmap[labelmap == 1] = 0
        labelmap[labelmap == 2] = 1  # keep only exo class, else clustering too slow
        
    if np.sum(labelmap)==0:
        sys.exit('Error: the given segmentation has no exocytose event (no voxel of value 2).')

    # Initialize clustering task:
    clust = Cluster(clustRadius=cluster_radius)

    # Launch clustering (result stored in objlist): can take some time (37min on i7 cpu)
    objlist = clust.launch(labelmap)

    # # Optionally, we can filter out detections that are too small, considered as false positives.
    # lbl_list = [1]
    # thr_list = [50]
    # objlist_thr = ol.above_thr_per_class(objlist, lbl_list, thr_list)

    # Save object lists:
    ol.write_xml(objlist, output_path)

utils.ignore_gooey_if_args()

def create_parser(parser=None, command=Path(__file__).stem, prog='Detect spots', description='Detect spots and convert resulting segmentation to h5. The clustering groups and labels the voxels so that all voxels of the same event share the same label, and each event gets a different label. Only exocytose events (voxels of value 2) are considered, ones are ignored.'):
    return utils.create_parser(parser, command, prog, description)

def add_args(parser):
    parser.add_argument('-s', '--segmentation', help='Path to the input segmentation.', default='detector_segmentation.h5', type=Path, widget='FileChooser')
    parser.add_argument('-cr', '--cluster_radius', help='Approximate size in voxel of the objects to cluster. 5 is a good value for events of 400nm on films with a pixel size of 160nm.', default=5, type=int)
    parser.add_argument('-a', '--annotation', help='Path to the output annotation file.', default='annotation.xml', type=Path, widget='FileSaver')
    parser.add_argument('-klu', '--keep_labels_unchanged', help='By default, bright spots are removed (labels 1 are set to 0) and exocytose events (labels 2) are set to 1. This option skip this step, so labels are kept unchanged.', action='store_true')
    parser.add_argument('-b', '--batch', help='Path to the root folder containing all folders to process.', default=None, type=Path, widget='DirChooser')

@Gooey
def main(args=None):

    args = utils.parse_args(args, create_parser, add_args)

    segmentation_paths = [Path(args.segmentation)] if args.batch is None else sorted([d / args.segmentation.name for d in args.batch.iterdir() if d.is_dir()])
    
    for segmentation_path in segmentation_paths:

        cluster(segmentation_path, args.cluster_radius, args.annotation, args.keep_labels_unchanged)

if __name__ == '__main__':
    main()