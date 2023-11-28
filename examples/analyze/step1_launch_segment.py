from deepfinder.inference import Segment
import deepfinder.utils.common as cm
import deepfinder.utils.smap as sm

# Input parameters:
path_data    = '/path/to/image/sequence/data.h5' # image sequence to be segmented
path_weights = '/path/to/weights/net_weights_FINAL.h5' # weights for neural network (obtained from training)
Nclass       = 3  # including background class
patch_size   = 160 # must be multiple of 4

# Output parameter:
path_output = 'out/'

# Load data:
data = cm.read_array(path_data)

# Initialize segmentation task:
seg  = Segment(Ncl=Nclass, path_weights=path_weights, patch_size=patch_size)

# Segment tomogram:
scoremaps = seg.launch(data)

# Get labelmap from scoremaps:
labelmap = sm.to_labelmap(scoremaps)

# Save labelmaps:
cm.write_array(labelmap , path_output+'labelmap.mrc')

# Print out visualizations of the test tomogram and obtained segmentation:
cm.plot_volume_orthoslices(data    , path_output+'data.png')
cm.plot_volume_orthoslices(labelmap, path_output+'prediction.png')
