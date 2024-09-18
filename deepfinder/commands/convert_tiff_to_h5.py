import sys
from deepfinder.commands import utils
utils.run_with_python_on_windows(__file__)
import re
import skimage
from pathlib import Path
import numpy as np
from deepfinder.utils.common import write_h5array

def get_tiff_files(path):
    return sorted([f for f in path.iterdir() if f.suffix.lower() in ['.tif', '.tiff']])

def convert_tiff_to_h5(tiff_path:Path, output_path:Path, make_subfolder:bool):
    if not tiff_path.exists():
        raise Exception(f'The input tiff path {tiff_path} does not exist.')
    
    output_path = Path(str(output_path).replace('{movie.name}', tiff_path.name).replace('{movie}', str(tiff_path)))
    output_path.parent.mkdir(exist_ok=True, parents=True)

    if make_subfolder:
        subfolder = tiff_path / 'tiff'
        subfolder.mkdir(exist_ok=True)
        # Put all files in the subfolder (except the subfolder itself)
        for file in sorted(list(set(tiff_path.iterdir())-set([subfolder]))):
            file.rename(subfolder / file.name)
        tiff_path = subfolder

    frames = get_tiff_files(tiff_path)
    nframes = len(frames)
    if nframes==0:
        raise Exception(f'The input tiff folder path {tiff_path} does not contain any tiff file (no frames).')

    # load 1st frame to get image dimensions
    first_frame = skimage.io.imread(str(frames[0]))

    # Instanciate volume
    vol = np.zeros((nframes, first_frame.shape[0], first_frame.shape[1]), dtype=first_frame.dtype)
    
    root_name = None

    for frame in frames:
        img = skimage.io.imread(str(frame))

        slice_idx = re.findall('[0-9]+', frame.name)  # get numbers from fname
        slice_idx = int(slice_idx[-1])  # last number in fname is slice idx
        if root_name is None:
            root_name = re.sub(r'\d+(?!.*\d)', '', frame.name)
        if root_name != re.sub(r'\d+(?!.*\d)', '', frame.name):
            raise Exception(f'Warning, two or more tiff frames have different name formatting ("{root_name}" and "{frame.name}").\nPlease make sure all frames are formatted in the same way, with the last number in the file name being the frame number.')
        vol[slice_idx-1,:,:] = img

    print(f'Saving image file "{output_path.resolve()}"...')
    write_h5array(vol, output_path)

utils.ignore_gooey_if_args()

def create_parser(parser=None, command=Path(__file__).stem, prog='Convert tiff to h5', description='Convert a movie made of tiff files to a single h5 file.'):
    return utils.create_parser(parser, command, prog, description)

def add_args(parser):
    parser.add_argument('-t', '--tiff', help='Path to the input movie folder. It must contain one tiff file per frame, their names must end with the frame number. If the --batch argument is set, this argument will be ignored and all folders in --batch will be processed.', default=None, type=Path, widget='DirChooser')
    parser.add_argument('-ms', '--make_subfolder', action='store_true', help='Put all tiffs in a tiff/ subfolder in the --tiff input folder, and saves the output h5 file beside.')
    parser.add_argument('-o', '--output', help='Output path to the h5 file. If used, the string {movie} will be replaced by the movie folder, and {movie.name} will be replaced by its name.', default='{movie}/movie.h5', type=Path, widget='FileSaver')
    parser.add_argument('-b', '--batch', help='Path to the root folder containing all folders to process.', default=None, type=Path, widget='DirChooser')

@utils.Gooey
def main(args=None):
    
    args = utils.parse_args(args, create_parser, add_args)
    
    if args.batch is not None and args.tiff is not None:
        sys.exit('Error: the tiff argument should not be set when the batch argument is used. Please remove the tiff argument to process all folders in the batch path ; or the batch argument to only process the tiff path.')
    
    tiffs = sorted([d for d in args.batch.iterdir() if d.is_dir()]) if args.batch is not None else [args.tiff]

    for tiff in tiffs:
        print('Process', tiff)
        convert_tiff_to_h5(tiff, args.output, args.make_subfolder)

if __name__ == '__main__':
    main()