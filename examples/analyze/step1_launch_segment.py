from pathlib import Path
from deepfinder.inference import Segment
import deepfinder.utils.common as cm
import deepfinder.utils.smap as sm

# Input parameters:
path_data    = Path('/path/to/image/sequence/data.h5') # image sequence to be segmented
path_weights = Path('/path/to/weights/net_weights_FINAL.h5') # weights for neural network (obtained from training, or can be the default model examples/analyze/in/net_weights_FINAL.h5)
Nclass       = 3  # including background class
patch_size   = 160 # must be multiple of 4

# Output parameter:
path_output = Path('out/')
image_name = 'image1'

(path_output / image_name).mkdir(exist_ok=True, parents=True)

# Load data:
data = cm.read_array(str(path_data))

# Initialize segmentation task:
seg  = Segment(Ncl=Nclass, path_weights=str(path_weights), patch_size=patch_size)

# Segment tomogram:
scoremaps = seg.launch(data)

# Get labelmap from scoremaps:
labelmap = sm.to_labelmap(scoremaps)

# Save labelmaps:
cm.write_array(labelmap , str(path_output / image_name / 'labelmap.mrc'))

# Print out visualizations of the test tomogram and obtained segmentation:
cm.plot_volume_orthoslices(data    , str(path_output / image_name / 'data.png'))
cm.plot_volume_orthoslices(labelmap, str(path_output / image_name / 'prediction.png'))
