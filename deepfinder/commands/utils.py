import sys, argparse
from gooey import GooeyParser

def ignore_gooey_if_args():
    if len(sys.argv) > 1 and '--ignore-gooey' not in sys.argv:
        sys.argv.append('--ignore-gooey')

def remove_ignore_gooey():
    if '--ignore-gooey' in sys.argv:
        sys.argv.remove('--ignore-gooey')

def create_parser(parser, command, prog, description):
    if parser is None:
        return GooeyParser(prog=prog, description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    return parser.add_parser(command, description=description, help=description)

def parse_args(args, create_parser, add_args):
    if args is None:
        parser = create_parser()
        add_args(parser)
        remove_ignore_gooey()
        args = parser.parse_args()
    return args