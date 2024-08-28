from deepfinder.commands import utils
utils.run_with_python_on_windows(__file__)
from pathlib import Path
from deepfinder.inference import Segment
import deepfinder.utils.common as cm
import deepfinder.utils.smap as sm

def segment(image_path, weights_path, output_path, visualization=False, patch_size=160, batch=None):

    if image_path.suffix != '.h5':
        raise Exception(f'Error: {image_path} must be in h5 format.')
    if output_path.suffix != '.h5':
        raise Exception(f'Error: {output_path} must be in h5 format.')

    if weights_path is None:
        weights_path = Path('_internal/net_weights_FINAL.h5')
        if not weights_path.exists():
            weights_path = utils.get_bundle_path() / 'net_weights_FINAL.h5'
        if not weights_path.exists():
            weights_path = Path('examples/analyze/in/net_weights_FINAL.h5')
    if not weights_path.exists():
        raise Exception(f'Model weights {weights_path} not found.')
    
    output_path = Path(str(output_path).replace('{movie.stem}', image_path.stem).replace('{movie.parent}', str(image_path.parent)))
    output_path.parent.mkdir(exist_ok=True, parents=True)

    # Load data:
    data = cm.read_array(str(image_path))

    # Initialize segmentation task:
    Nclass       = 3  # including background class
    seg  = Segment(Ncl=Nclass, path_weights=str(weights_path), patch_size=patch_size)

    # Segment tomogram:
    scoremaps = seg.launch(data, verbose=0)

    # Get labelmap from scoremaps:
    labelmap = sm.to_labelmap(scoremaps)

    # Save labelmaps:
    print(f'Saving segmentation file "{output_path.resolve()}"...')
    cm.write_array(labelmap , str(output_path))

    if visualization:
        # Print out visualizations of the test tomogram and obtained segmentation:
        cm.plot_volume_orthoslices(data    , str(output_path.parent / f'{image_path.stem}_data.png'))
        cm.plot_volume_orthoslices(labelmap, str(output_path.parent / f'{image_path.stem}_prediction.png'))

utils.ignore_gooey_if_args()

def create_parser(parser=None, command=Path(__file__).stem, prog='Detect exocytose events.', description='Segment exocytose events in a video.'):
    return utils.create_parser(parser, command, prog, description)

def add_args(parser):
    parser.add_argument('-m', '--movie', help='Path to the input movie (in .h5 format).', default='movie.h5', type=Path, widget='FileChooser')
    parser.add_argument('-mw', '--model_weights', help='Path to the model weigths path (in .h5 format). If none is given, default locations will be used ("_internal/net_weights_FINAL.h5" or "examples/analyze/in/net_weights_FINAL.h5").', default=None, type=Path, widget='FileChooser')
    parser.add_argument('-ps', '--patch_size', help='Patch size (the movie is split in cubes of --patch_size before being processed). Must be a multiple of 4.', default=160, type=int)
    parser.add_argument('-v', '--visualization', help='Generate visualization images.', action='store_true')
    parser.add_argument('-s', '--segmentation', help='Path to the output segmentation (in .h5 format). If used, the string {movie.stem} will be replaced by the movie file name (without extension), and {movie.parent} will be replaced by its parent folder.', default='{movie.parent}/{movie.stem}_segmentation.h5', type=Path, widget='FileSaver')
    parser.add_argument('-b', '--batch', help='Optional path to the root folder containing all folders to process. If given, the --movie argument must be relative to the folder to process.', default=None, type=Path, widget='DirChooser')

@utils.Gooey
def main(args=None):

    args = utils.parse_args(args, create_parser, add_args)

    movie_paths = [Path(args.movie)] if args.batch is None else sorted([d / args.movie.name for d in args.batch.iterdir() if d.is_dir()])

    for movie_path in movie_paths:

        segment(movie_path, args.model_weights, args.segmentation, args.visualization, args.patch_size, args.batch)

if __name__ == '__main__':
    main()