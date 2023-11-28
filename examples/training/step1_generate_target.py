import numpy as np
from deepfinder.training import TargetBuilder
import deepfinder.utils.common as cm
import deepfinder.utils.objl as ol

path_output = 'out/'
path_objl = 'in/objl_cell6.xml'  # path to object list containing annotated positions
data_shape = [1001, 317, 317]  # shape of image sequence [t,y,x]


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


mask_exo = get_exo_mask()

# Next, read object list:
objl = ol.read_xml(path_objl)

for idx, obj in enumerate(objl):
    obj[idx][]

# Then, initialize target generation task:
tbuild = TargetBuilder()

# Initialize target array. Here, we initialize it with an empty array. But it could be initialized with a segmentation map containing other (non-overlapping) classes.
initial_vol = np.zeros(data_shape)

# Run target generation:
target = tbuild.generate_with_shapes(objl, initial_vol, [mask_exo])
cm.plot_volume_orthoslices(target, path_output + 'orthoslices_target.png')

# Save target:
cm.write_array(target, path_output + 'target.mrc')