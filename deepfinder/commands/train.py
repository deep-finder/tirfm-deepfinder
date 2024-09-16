import json
from deepfinder.commands import utils
utils.run_with_python_on_windows(__file__)
from pathlib import Path

def train(dataset_path, output_path, patch_sizes, random_shifts, batch_sizes, ns_epochs, ns_steps_per_epoch):
    from deepfinder.training import Train
    from deepfinder.utils.dataloader import Dataloader

    # Load dataset:
    path_data, path_target, objl_train, objl_valid = Dataloader(ext='.h5')(dataset_path)

    last_weights_path = None
    for patch_size, random_shift, batch_size, n_epochs, n_steps_per_epoch in zip(patch_sizes, random_shifts, batch_sizes, ns_epochs, ns_steps_per_epoch):
        
        print(f'Launch training with: patch_size: {patch_size}, random_shift: {random_shift}, batch_size: {batch_size}, n_epochs: {n_epochs}, n_steps_per_epoch: {n_steps_per_epoch}')
        # Input parameters:
        Nclass = 3
        dim_in = patch_size  # patch size

        # Initialize training task:
        trainer = Train(Ncl=Nclass, dim_in=dim_in)
        trainer.path_out         = f'{output_path}_weights_patch_size_{patch_size}_' # output path
        trainer.h5_dset_name     = 'dataset' # if training data is stored as h5, you can specify the h5 dataset
        trainer.batch_size       = batch_size
        trainer.epochs           = n_epochs
        trainer.steps_per_epoch  = n_steps_per_epoch
        trainer.Nvalid           = 10 # steps per validation
        trainer.flag_direct_read     = False
        trainer.flag_batch_bootstrap = True
        trainer.Lrnd             = random_shift # random shifts when sampling patches (data augmentation)
        trainer.class_weights = None # keras syntax: class_weights={0:1., 1:10.} every instance of class 1 is treated as 10 instances of class 0

        Path(trainer.path_out).parent.mkdir(exist_ok=True, parents=True)

        if last_weights_path is not None:
            trainer.net.load_weights(f'{last_weights_path}net_weights_FINAL.h5')

        # Finally, launch the training procedure:
        trainer.launch(path_data, path_target, objl_train, objl_valid)
        last_weights_path = trainer.path_out

utils.ignore_gooey_if_args()

def create_parser(parser=None, command=Path(__file__).stem, prog='Train ExoDeepFinder', description='Train a model from the given dataset.'):
    return utils.create_parser(parser, command, prog, description)

def add_args(parser):
    parser.add_argument('-d', '--dataset', help='Path to the input dataset', required=True, widget='DirChooser')
    parser.add_argument('-ps', '--patch_sizes', help='Patch sizes. Can be an integer or a list of the form [patchSizeModel1, patchSizeModel2, ...]. A list enables to train multiple models, each using the previous weights as initialization. For example, with --patch_sizes "[8, 16]": Model1 will use patches of size 8 voxels and Model2 will use patches of 16 voxels and initialize with the Model1 weights. The longest list of the parameters --patch_sizes, --batch_sizes, --random_shifts, --n_epochs and --n_steps will be use to determine the number of trainings ; and shorter lists will be extended with duplicates of their last values (integer parameters are similarly duplicated) to match the number of trainings.', default='[8, 16, 32, 48]', type=str)
    parser.add_argument('-bs', '--batch_sizes', help='Batch sizes. Can be an integer or a list of the form [batchSizeModel1, batchSizeModel2, ...].', default='[256, 128, 32, 10]', type=str)
    parser.add_argument('-rs', '--random_shifts', help='Random shifts. Can be an integer or a list of the form [randomShiftsModel1, randomShiftsModel2, ...].', default='[4, 8, 16, 32]', type=str)
    parser.add_argument('-ne', '--n_epochs', help='Number of epochs. Can be an integer or a list of the form [nEpochsModel1, nEpochsModel2, ...].', default='100', type=str)
    parser.add_argument('-ns', '--n_steps', help='Number of steps per epochs. Can be an integer or a list of the form [nStepsModel1, nStepsModel2, ...].', default='100', type=str)
    parser.add_argument('-o', '--output', help='Path to the output folder where the model will be stored', widget='DirChooser')

@utils.Gooey
def main(args=None):

    args = utils.parse_args(args, create_parser, add_args)
    # Convert arguments --patch_sizes, --n_epochs, --n_steps, _random_shifts and --batch_sizes to lists with json.loads()
    params = [json.loads(str(getattr(args, arg_name))) for arg_name in ['patch_sizes', 'random_shifts', 'batch_sizes', 'n_epochs', 'n_steps']]
    # Convert ints to lists
    params = [p if isinstance(p, list) else [p] for p in params]
    # Set the number of trainings to the longest list length
    n_trainings = max([len(p) for p in params])
    # Duplicate the last value of each list to exetend it so that it has one value for each training
    params = [p + [p[-1]]*(n_trainings-len(p)) for p in params]
    patch_sizes, random_shifts, batch_sizes, n_epochs, n_steps = params
    train(args.dataset, args.output, patch_sizes, random_shifts, batch_sizes, n_epochs, n_steps)

if __name__ == '__main__':
    main()