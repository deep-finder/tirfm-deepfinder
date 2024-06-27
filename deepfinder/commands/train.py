from deepfinder.commands import utils
utils.run_with_python_on_windows(__file__)
from pathlib import Path
from gooey import Gooey


def train(dataset_path, output_path, n_epochs, steps_per_epoch):
    from deepfinder.training import Train
    from deepfinder.utils.dataloader import Dataloader

    # Load dataset:
    path_data, path_target, objl_train, objl_valid = Dataloader(ext='.h5')(dataset_path)

    # Input parameters:
    Nclass = 3
    dim_in = 48  # patch size

    # Initialize training task:
    trainer = Train(Ncl=Nclass, dim_in=dim_in)
    trainer.path_out         = output_path # output path
    trainer.h5_dset_name     = 'dataset' # if training data is stored as h5, you can specify the h5 dataset
    trainer.batch_size       = 8
    trainer.epochs           = n_epochs
    trainer.steps_per_epoch  = steps_per_epoch
    trainer.Nvalid           = 10 # steps per validation
    trainer.flag_direct_read     = False
    trainer.flag_batch_bootstrap = True
    trainer.Lrnd             = 32 # random shifts when sampling patches (data augmentation)
    trainer.class_weights = None # keras syntax: class_weights={0:1., 1:10.} every instance of class 1 is treated as 10 instances of class 0

    Path(trainer.path_out).mkdir(exist_ok=True, parents=True)

    # Use following line if you want to resume a previous training session:
    #trainer.net.load_weights('out/round1/net_weights_FINAL.h5')

    # Finally, launch the training procedure:
    trainer.launch(path_data, path_target, objl_train, objl_valid)


utils.ignore_gooey_if_args()

def create_parser(parser=None, command=Path(__file__).stem, prog='Train ExoDeepFinder', description='Train a model from the given dataset.'):
    return utils.create_parser(parser, command, prog, description)

def add_args(parser):
    parser.add_argument('-d', '--dataset', help='Path to the input dataset', required=True, widget='FileChooser')
    parser.add_argument('-ne', '--n_epochs', help='Number of epochs', default=1000, type=int)
    parser.add_argument('-ns', '--n_steps', help='Number of steps per epochs', default=100, type=int)
    parser.add_argument('-o', '--output', help='Output path where the model will be stored', widget='FileChooser')

@Gooey
def main(args=None):

    args = utils.parse_args(args, create_parser, add_args)
    
    train(args.dataset, args.output, args.n_epochs, args.n_steps)

if __name__ == '__main__':
    main()