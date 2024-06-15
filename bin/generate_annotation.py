# =============================================================================================
# DeepFinder - a deep learning approach to detect exocytose events.
# =============================================================================================
# Copyright (C) Inria,  Emmanuel Moebel, Charles Kervrann, All Rights Reserved, 2015-2021, v1.0
# License: GPL v3.0. See <https://www.gnu.org/licenses/>
# =============================================================================================

import argparse
from pathlib import Path
from deepfinder.inference import Cluster
import deepfinder.utils.common as cm
import deepfinder.utils.objl as ol

def cluster(segmentation_path, cluster_radius, output_path=None):
    if output_path is None:
        output_path = segmentation_path.parent / f'{segmentation_path.stem}.xml'
    
    output_path.parent.mkdir(exist_ok=True, parents=True)

    # Load data:
    labelmap = cm.read_array(str(segmentation_path))

    # Next, only keep the class of interest. In the experiments of the paper, class 0 is background,
    # class 1 is constant spot (docked vesicle), and class 2 is blinking spot (exocytosis event).
    # Below we convert to an array with only class 0 as background and class 1 as constant spot:
    labelmap.setflags(write=1)
    labelmap[labelmap == 1] = 0
    labelmap[labelmap == 2] = 1  # keep only exo class, else clustering too slow

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

if __name__ == '__main__':

    parser = argparse.ArgumentParser('Generate Annotation', description='Cluster exocytose events to generate an annotation file from a segmentation file.')

    parser.add_argument('-s', '--segmentation', help='Path to the input segmentation. If the path is a folder, all *_segmentation.h5 images will be processed.')
    parser.add_argument('-cr', '--cluster_radius', help='Size of the radius, in voxel.', default=5)
    parser.add_argument('-a', '--annotations', help='Path to the output annotations. Default is "[input_segmentation].xml". If input_image is a folder, output names will be generated from input image names.', default=None)

    args = parser.parse_args()

    image_path = Path(args.segmentation)
    image_paths = list(image_path.glob('*_segmentation.h5')) if image_path.is_dir() else [image_path]
    
    for image_path in image_paths:

        cluster(image_path, args.cluster_radius, args.annotations)