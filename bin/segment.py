import argparse
from pathlib import Path
from deepfinder.inference import Segment
import deepfinder.utils.common as cm
import deepfinder.utils.smap as sm

def segment(image_path, weights_path, output_path=None, visualization=False, patch_size=160):
    if output_path is None:
        output_path = image_path.parent / f'{image_path.stem}_segmentation.h5'

    output_path.parent.mkdir(exist_ok=True, parents=True)

    # Load data:
    data = cm.read_array(str(image_path))

    # Initialize segmentation task:
    Nclass       = 3  # including background class
    seg  = Segment(Ncl=Nclass, path_weights=str(weights_path), patch_size=patch_size)

    # Segment tomogram:
    scoremaps = seg.launch(data)

    # Get labelmap from scoremaps:
    labelmap = sm.to_labelmap(scoremaps)

    # Save labelmaps:
    cm.write_array(labelmap , str(output_path))

    if visualization:
        # Print out visualizations of the test tomogram and obtained segmentation:
        cm.plot_volume_orthoslices(data    , str(output_path.parent / f'{image_path.stem}_data.png'))
        cm.plot_volume_orthoslices(labelmap, str(output_path.parent / f'{image_path.stem}_prediction.png'))

if __name__ == '__main__':

    parser = argparse.ArgumentParser('Detect exocytose events.', description='Segment exocytose events in a video.')

    parser.add_argument('-i', '--image', help='Path to the input image. If the path is a folder, all .h5 images will be processed, expect the ones ending with "_segmentation.h5".')
    parser.add_argument('-mw', '--model_weights', help='Path to the model weigths path.', default='../examples/analyze/in/net_weights_FINAL.5')
    parser.add_argument('-ps', '--patch_size', help='Patch size. Must be a multiple of 4.', default=160)
    parser.add_argument('-v', '--visualization', help='Generate visualization images.', action='store_true')
    parser.add_argument('-s', '--segmentation', help='Path to the output segmentation. Default is "[input_image]_segmentation.h5". If input_image is a folder, output names will be generated from input image names.', default=None)

    args = parser.parse_args()

    image_path = Path(args.image)
    image_paths = list(set(image_path.glob('*.h5')) - set(image_path.glob('*_segmentation.h5'))) if image_path.is_dir() else [image_path]
    
    for image_path in image_paths:

        segment(image_path, args.model_weights, args.segmentation, args.visualization, args.patch_size)
