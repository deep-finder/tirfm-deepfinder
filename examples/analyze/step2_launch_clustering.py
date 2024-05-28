from pathlib import Path
from deepfinder.inference import Cluster
import deepfinder.utils.common as cm
import deepfinder.utils.objl as ol

# Input parameters:
path_labelmap = Path('out/image1/labelmap.mrc')
cluster_radius = 5  # should correspond to average radius of target objects (in voxels)

# Load data:
labelmap = cm.read_array(str(path_labelmap))

# Next, only keep the class of interest. In the experiments of the paper, class 0 is background,
# class 1 is constant spot (docked vesicle), and class 2 is blinking spot (exocytosis event).
# Below we convert to an array with only class 0 as background and class 1 as constant spot:
labelmap.setflags(write=1)
labelmap[labelmap == 1] = 0
labelmap[labelmap == 2] = 1  # keep only exo class, else clustering too slow

# Initialize clustering task:
clust = Cluster(clustRadius=5)

# Launch clustering (result stored in objlist): can take some time (37min on i7 cpu)
objlist = clust.launch(labelmap)

# # Optionally, we can filter out detections that are too small, considered as false positives.
# lbl_list = [1]
# thr_list = [50]
# objlist_thr = ol.above_thr_per_class(objlist, lbl_list, thr_list)

# Save object lists:
ol.write_xml(objlist    , path_labelmap.parent / 'objl.xml')