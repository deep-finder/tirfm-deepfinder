from deepfinder.commands import utils
utils.run_with_python_on_windows(__file__)
import sys
import shlex
import shutil
from pathlib import Path
import subprocess
from deepfinder.commands.convert_tiff_to_h5 import convert_tiff_to_h5

def detect_spots(tiffs_path, detector_path, command, output_path):
    output_path = Path(str(output_path).replace('{movie.name}', tiffs_path.name).replace('{movie.parent}', str(tiffs_path.parent)))
    output_folder = output_path.with_suffix('')
    output_folder.mkdir(exist_ok=True, parents=True)
    command = command.replace('{detector}', str(detector_path))
    command = command.replace('{input}', str(tiffs_path))
    command = command.replace('{output}', str(output_folder))
    subprocess.run(shlex.split(command), check=True)
    convert_tiff_to_h5(output_folder, output_path, make_subfolder=False)
    shutil.rmtree(output_folder)
    return

utils.ignore_gooey_if_args()

def create_parser(parser=None, command=Path(__file__).stem, prog='Detect spots', description='Detect spots and convert resulting segmentation to h5.'):
    return utils.create_parser(parser, command, prog, description)

def add_args(parser):
    parser.add_argument('-m', '--movie', help='Path to the input folder containing one tiff file per frame.', default='tiff/', type=Path, widget='DirChooser')
    parser.add_argument('-dp', '--detector_path', help='Path to the detector.', default='path/to/atlas', type=Path, widget='DirChooser')
    parser.add_argument('-dc', '--detector_command', help='Command to detect spots. If used, the {detector} string will be replaced by the --detector_path argument. {input} will be replaced by the input folder, {output} by the output segmentation.', default='python "{detector}/compute_segmentations.py" --atlas "{detector}/build/" --dataset "{input}" --output "{output}"', type=str)
    parser.add_argument('-o', '--output', help='Path to the output segmentations. If used, the {movie.name} string will be replaced by the --movie file name, and {movie.parent} by the movie parent folder.', default='{movie.parent}/detector_segmentation.h5', type=Path, widget='FileSaver')
    parser.add_argument('-b', '--batch', help='Path to the root folder containing all folders to process. If given, the --movie argument must be relative to the folder to process.', default=None, type=Path, widget='DirChooser')

@utils.Gooey
def main(args=None):

    args = utils.parse_args(args, create_parser, add_args)

    movie_paths = sorted([d for d in args.batch.iterdir() if d.is_dir()]) if args.batch is not None else [args.movie]

    for movie_path in movie_paths:
        print('Process', movie_path)
        tiff_path = movie_path / args.movie if args.batch is not None else args.movie
        detect_spots(tiff_path, args.detector_path, args.detector_command, args.output)

if __name__ == '__main__':
    main()