import re
import skimage
import argparse
from pathlib import Path
import h5py
import numpy as np
import os
from deepfinder.utils.common import write_h5array

def get_tiff_files(path):
    return sorted([f for f in path.iterdir() if f.suffix.lower() in ['.tif', '.tiff']])

def convert_tiff_to_h5(tiff_path:Path, output_path:Path|None, make_subfolder:bool):
    if not tiff_path.exists():
        raise Exception(f'The input tiff path {tiff_path} does not exist.')
    if make_subfolder:
        subfolder = tiff_path / 'tiff'
        subfolder.mkdir(exist_ok=True)
        # Put all files in the subfolder (except the subfolder itself)
        for file in sorted(list(set(tiff_path.iterdir())-set([subfolder]))):
            file.rename(subfolder / file.name)
        output_path = tiff_path / output_path
        tiff_path = subfolder
    else:
        output_path = Path(output_path)

    output_path.parent.mkdir(exist_ok=True, parents=True)

    frames = get_tiff_files(tiff_path)

    # load 1st frame to get image dimensions
    first_frame = skimage.io.imread(str(frames[0]))

    # Instanciate volume
    nframes = len(frames)
    vol = np.zeros((nframes, first_frame.shape[0], first_frame.shape[1]), dtype=first_frame.dtype)
    
    for frame in frames:
        img = skimage.io.imread(str(frame))

        slice_idx = re.findall('[0-9]+', frame.name)  # get numbers from fname
        slice_idx = int(slice_idx[-1])  # last number in fname is slice idx    
        vol[slice_idx-1,:,:] = img

    write_h5array(vol, output_path)

def main():
    parser = argparse.ArgumentParser('Convert tiff to h5', description='Convert a movie made of tiff files to a single h5 file.')

    parser.add_argument('-t', '--tiff', help='Path to the tiff input folder. This must contain one tiff file per frame, their names must end with the frame number. If the [--batch] argument is set, this argument will be ignored and all folders in [--batch] will be processed.', default=None, type=Path)
    parser.add_argument('-ms', '--make_subfolder', action='store_true', help='Put all tiffs in a tiff/ subfolder in the [--tiff] input folder, and saves the output h5 file beside.')
    parser.add_argument('-o', '--output', help='Output path to the h5 file. Default is [--tiff].h5, or movie.h5 if the [--make_subfolder] argument is set.', default='movie.h5', type=Path)
    parser.add_argument('-b', '--batch', help='Path to the root folder containing all folders to process.', default=None, type=Path)

    args = parser.parse_args()

    tiffs = sorted([d for d in args.batch.iterdir() if d.is_dir()]) if args.batch is not None else [args.tiff]

    for tiff in tiffs:
        print('Process', tiff)
        convert_tiff_to_h5(tiff, args.output, args.make_subfolder)

if __name__ == '__main__':
    main()