import re
import skimage
import argparse
from pathlib import Path
import h5py
import numpy as np
import os

# Writes data in h5 file, to specified h5 dataset. Is also adapted for labelmaps: saved as int8 to gain disk space.
# INPUTS:
#   array    : numpy array
#   filename : string '/path/to/file.h5'
#   dset_name: string dataset name
def write_h5array(array, filename, dset_name='dataset'):
    h5file = h5py.File(filename, 'w')
    if array.dtype == np.int8:
        dset = h5file.create_dataset(dset_name, array.shape, dtype='int8')
        dset[:] = np.int8(array)
    else:
        dset = h5file.create_dataset(dset_name, array.shape, dtype='float16')
        dset[:] = np.float16(array)
    h5file.close()

def convert_tiff_to_h5(tiff_path:Path, output_path:Path|None, make_subfolder:bool):
    if not tiff_path.exists():
        raise Exception(f'The input tiff path {tiff_path} does not exist.')
    if make_subfolder:
        subfolder = tiff_path / 'tiff'
        subfolder.mkdir(exist_ok=True)
        for file in sorted(list(tiff_path.iterdir())):
            if file != subfolder: file.rename(subfolder / file.name)
        output_path = tiff_path / 'movie.h5' if output_path is None else tiff_path / output_path.name
        tiff_path = subfolder
    else:
        output_path = tiff_path.with_suffix('.h5') if output_path is None else Path(output_path)

    output_path.parent.mkdir(exist_ok=True, parents=True)

    frames = list(tiff_path.glob('*.tiff'))

    # load 1st frame to get image dimensions
    first_frame = skimage.io.imread(str(frames[0]))
    # Instanciate volume
    nframes = len(frames)
    vol = np.zeros((nframes, first_frame.shape[0], first_frame.shape[1]), dtype='uint8')
    
    for frame in frames:
        img = skimage.io.imread(str(frame))

        slice_idx = re.findall('[0-9]+', frame.name)  # get numbers from fname
        slice_idx = int(slice_idx[-1])  # last number in fname is slice idx    
        vol[slice_idx-1,:,:] = img

    write_h5array(vol, output_path)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser('Convert tiff to h5', description='Convert a movie made of tiff files to a single h5 file.')

    parser.add_argument('-t', '--tiff', help='Path to the tiff input folder. This must contain one tiff file per frame, their names must end with the frame number.', required=True, type=Path)
    parser.add_argument('-ms', '--make_subfolder', action='store_true', help='Put all tiffs in a tiff/ subfolder in the [--tiff] input folder, and saves the output h5 file beside.')
    parser.add_argument('-o', '--output', help='Output path to the h5 file. Default is [--tiff].h5, or movie.h5 if the [--make_subfolder] argument is set.', default=None, type=Path)
    parser.add_argument('-b', '--batch', help='Path to the root folder containing all folders to process.', default=None, type=Path)

    args = parser.parse_args()

    tiffs = sorted(list(args.batch.iterdir())) if args.batch is not None else [args.tiff]
    
    for tiff in tiffs:
        convert_tiff_to_h5(tiff, args.output, args.make_subfolder)