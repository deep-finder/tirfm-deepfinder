import deepfinder.commands.utils
deepfinder.commands.utils.run_with_python_on_windows(__file__)
import argparse
import deepfinder.commands.convert_tiff_to_h5
import deepfinder.commands.segment
import deepfinder.commands.generate_annotation
import deepfinder.commands.generate_segmentation
import deepfinder.commands.detect_spots
import deepfinder.commands.detect_spots_with_atlas
import deepfinder.commands.merge_detector_expert
import deepfinder.commands.structure_training_dataset
import deepfinder.commands.train
import inspect

deepfinder.commands.utils.ignore_gooey_if_args()

def get_description(function):
    return inspect.signature(function).parameters["description"].default

@deepfinder.commands.utils.Gooey(
    program_name='ExoDeepFinder',
    menu=[{
        'name': 'Help',
        'items': [{
            'type': 'AboutDialog',
            'menuTitle': 'About',
            'name': 'ExoDeepFinder',
            'description': 'ExoDeepFinder is an exocytosis event detection tool.',
            'version': '0.2.4',
            'copyright': '2024',
            'website': 'https://github.com/deep-finder/tirfm-deepfinder',
            'developer': 'Emmanuel Moebel, Arthur Masson',
            'license': 'GNU General Public License v3.0'
        },{
            'type': 'Link',
            'menuTitle': 'Documentation',
            'url': 'https://github.com/deep-finder/tirfm-deepfinder'
        }]
    }])
def main():
    # parser = GooeyParser(prog='', description=f'''Detect exocytose events\n
    #                     convert_tiff_to_h5: {get_description(deepfinder.commands.convert_tiff_to_h5.create_parser)}\n
    #                     segment: {get_description(deepfinder.commands.segment.create_parser)}\n
    #                     generate_annotation: {get_description(deepfinder.commands.generate_annotation.create_parser)}\n
    #                     generate_segmentation: {get_description(deepfinder.commands.generate_segmentation.create_parser)}\n
    #                     detect_spots: {get_description(deepfinder.commands.detect_spots.create_parser)}\n
    #                     detect_spots_with_atlas: {get_description(deepfinder.commands.detect_spots_with_atlas.create_parser)}\n
    #                     merge_detector_expert: {get_description(deepfinder.commands.merge_detector_expert.create_parser)}\n
    #                     structure_training_dataset: {get_description(deepfinder.commands.structure_training_dataset.create_parser)}\n
    #                     train: {get_description(deepfinder.commands.train.create_parser)}\n''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    description = f'''Detect exocytose events\n
                    see https://github.com/deep-finder/tirfm-deepfinder for more information'''
    try:
        from gooey import GooeyParser
        parser = GooeyParser(prog='', description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    except ModuleNotFoundError:
        parser = deepfinder.commands.utils.CustomArgumentParser(prog='ExoDeepFinder', description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    subparsers = parser.add_subparsers(required=True)

    subparser = deepfinder.commands.convert_tiff_to_h5.create_parser(subparsers)
    deepfinder.commands.convert_tiff_to_h5.add_args(subparser)
    subparser.set_defaults(func=deepfinder.commands.convert_tiff_to_h5.main)

    subparser = deepfinder.commands.segment.create_parser(subparsers)
    deepfinder.commands.segment.add_args(subparser)
    subparser.set_defaults(func=deepfinder.commands.segment.main)

    subparser = deepfinder.commands.generate_annotation.create_parser(subparsers)
    deepfinder.commands.generate_annotation.add_args(subparser)
    subparser.set_defaults(func=deepfinder.commands.generate_annotation.main)

    subparser = deepfinder.commands.generate_segmentation.create_parser(subparsers)
    deepfinder.commands.generate_segmentation.add_args(subparser)
    subparser.set_defaults(func=deepfinder.commands.generate_segmentation.main)

    subparser = deepfinder.commands.detect_spots.create_parser(subparsers)
    deepfinder.commands.detect_spots.add_args(subparser)
    subparser.set_defaults(func=deepfinder.commands.detect_spots.main)

    subparser = deepfinder.commands.detect_spots_with_atlas.create_parser(subparsers)
    deepfinder.commands.detect_spots_with_atlas.add_args(subparser)
    subparser.set_defaults(func=deepfinder.commands.detect_spots_with_atlas.main)

    subparser = deepfinder.commands.merge_detector_expert.create_parser(subparsers)
    deepfinder.commands.merge_detector_expert.add_args(subparser)
    subparser.set_defaults(func=deepfinder.commands.merge_detector_expert.main)

    subparser = deepfinder.commands.structure_training_dataset.create_parser(subparsers)
    deepfinder.commands.structure_training_dataset.add_args(subparser)
    subparser.set_defaults(func=deepfinder.commands.structure_training_dataset.main)

    subparser = deepfinder.commands.train.create_parser(subparsers)
    deepfinder.commands.train.add_args(subparser)
    subparser.set_defaults(func=deepfinder.commands.train.main)

    args = parser.parse_args()
    args.func(args)
    return

if __name__ == '__main__':
    main()