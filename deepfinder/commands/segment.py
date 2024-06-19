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

def main():

    parser = argparse.ArgumentParser('Detect exocytose events.', description='Segment exocytose events in a video.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-m', '--movie', help='Path to the input movie.', default='movie.h5', type=Path)
    parser.add_argument('-mw', '--model_weights', help='Path to the model weigths path.', default='examples/analyze/in/net_weights_FINAL.5')
    parser.add_argument('-ps', '--patch_size', help='Patch size. Must be a multiple of 4.', default=160)
    parser.add_argument('-v', '--visualization', help='Generate visualization images.', action='store_true')
    parser.add_argument('-s', '--segmentation', help='Path to the output segmentation. Default is "[--movie]_segmentation.h5".', default=None)
    parser.add_argument('-b', '--batch', help='Path to the root folder containing all folders to process.', default=None, type=Path)

    args = parser.parse_args()

    movie_paths = [Path(args.movie)] if args.batch is None else sorted([d / args.movie.name for d in args.batch.iterdir() if d.is_dir()])

    for movie_path in movie_paths:

        segment(movie_path, args.model_weights, args.segmentation, args.visualization, args.patch_size)

if __name__ == '__main__':
    main()