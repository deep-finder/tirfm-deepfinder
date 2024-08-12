from deepfinder.commands import utils
utils.run_with_python_on_windows(__file__)
import sys
import shutil
import numpy as np
from pathlib import Path

def structure_training_dataset(input_path:Path, output_path:Path, movie:Path, merged_segmentation:Path, merged_annotation:Path, split:float):
    if output_path.exists() and len(list(output_path.iterdir()))>0:

        answer = input(f'Output training path {output_path} is not empty. Do you want to delete everything inside this path (yes/no)? \n').lower()
        if answer == 'yes' or answer == 'y':
            shutil.rmtree(output_path)
        else:
            sys.exit(f'Please provide an empty training path, {output_path} is not empty.')

    output_path.mkdir(exist_ok=True, parents=True)

    movies = sorted([d for d in input_path.iterdir() if d.is_dir()])
    for movie_folder in movies:
        
        (output_path / f'{movie_folder.name}.h5').symlink_to((movie_folder / movie).resolve())
        (output_path / f'{movie_folder.name}_target.h5').symlink_to((movie_folder / merged_segmentation).resolve())
        (output_path / f'{movie_folder.name}_objl.xml').symlink_to((movie_folder / merged_annotation).resolve())
    
    if split>0:
        rng = np.random.default_rng()
        rng.shuffle(movies)
        split_index = int(split * len(movies) / 100.0)
        training_set = movies[:split_index]
        validation_set = movies[split_index:]
        (output_path / 'train').mkdir(exist_ok=True)
        (output_path / 'valid').mkdir(exist_ok=True)
        for movie in training_set:
            for file in output_path.glob(movie.name + '*'):
                file.rename(output_path / 'train' / file.name)
        for movie in validation_set:
            for file in output_path.glob(movie.name + '*'):
                file.rename(output_path / 'valid' / file.name)
        # compact version is less readable
        # for name, dataset in [('train', training_set), ('valid', validation_set)]:
        #     for movie in dataset:
        #         for file in output_path.glob(movie.name + '*'):
        #             file.rename(output_path / name / file.name)

# Dataset structure:
#   exocytose_data/
#   ├── movie1/
#   │   ├──── movie.h5
#   │   ├──── expert_segmentation.h5
#   │   ├──── expert_annotation.xml
#   │   ├──── atlas_segmentation.h5
#   │   ├──── atlas_annotation.xml
#   │   ├──── merged_segmentation.h5
#   │   └──── merged_annotation.xml
#   ├── movie2/
#   │   ├──── movie.h5
#   │   ├──── expert_segmentation.h5
#   │   ├──── expert_annotation.xml
#   │   ├──── atlas_segmentation.h5
#   │   ├──── atlas_annotation.xml
#   │   ├──── merged_segmentation.h5
#   │   └──── merged_annotation.xml
#   ├── ...
#
# Training structure:
#   data/
#   ├── movie1.h5
#   ├── movie1_objl.xml
#   ├── movie1_target.h5
#   ├── movie2.h5
#   ├── movie2_objl.xml
#   ├── movie2_target.h5
#   ...
# 


utils.ignore_gooey_if_args()

def create_parser(parser=None, command=Path(__file__).stem, prog='Structure training dataset', description='Convert the default dataset structure to the training file structure.'):
    return utils.create_parser(parser, command, prog, description)

def add_args(parser):
    parser.add_argument('-i', '--input', help='Path to the input dataset folder', type=Path, required=True, widget='DirChooser')
    parser.add_argument('-o', '--output', help='Path to the output folder', type=Path, required=True, widget='DirChooser')
    parser.add_argument('-s', '--split', help='Splits the dataset in two random sets for training and validation, with --split %% of the movies in the training set, and the rest in the validation set (creates train/ and valid/ folders). Does not split if 0.', default=70, type=float)

    parser.add_argument('-m', '--movie', help='Path to the movie (relative to the movie folder).', default='movie.h5', type=Path, widget='FileChooser')
    parser.add_argument('-ms', '--merged_segmentation', help='Path to the merged segmentation (relative to the movie folder).', default='merged_segmentation.h5', type=Path, widget='FileSaver')
    parser.add_argument('-ma', '--merged_annotation', help='Path to the merged annotation (relative to the movie folder).', default='merged_annotation.xml', type=Path, widget='FileSaver')

@utils.Gooey
def main(args=None):
    
    args = utils.parse_args(args, create_parser, add_args)
    
    structure_training_dataset(args.input, args.output, args.movie, args.merged_segmentation, args.merged_annotation, args.split)

if __name__ == '__main__':
    main()