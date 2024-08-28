import sys, argparse, platform, subprocess, functools
from pathlib import Path
import importlib.util

try:
    import gooey
    Gooey = gooey.Gooey
except:
    # Create a fake Gooey decorator if Gooey is not installed
    def Gooey(_func=None, *, program_name=None, menu=None):
        def decorator_Gooey(func):
            @functools.wraps(func)
            def wrapper_main(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper_main
        return decorator_Gooey if _func is None else decorator_Gooey(_func)

def get_gooey():
    return Gooey

# On windows, the command GUIs cannot be used directly, they must be called with python and full path to the command (because of [a known Gooey issue](https://github.com/chriskiehl/Gooey/issues/907))
# So, if called from the command: rerun the same file but with python and full path
def run_with_python_on_windows(file):
    if platform.system() == 'Windows' and len(sys.argv) == 1 and not sys.argv[0].endswith('.py') and not getattr(sys, 'frozen', False):
        subprocess.call([sys.executable, file])
        sys.exit()

def ignore_gooey_if_args():
    if len(sys.argv) > 1 and '--ignore-gooey' not in sys.argv and importlib.util.find_spec("gooey") is not None:
        sys.argv.append('--ignore-gooey')

def remove_ignore_gooey():
    if '--ignore-gooey' in sys.argv:
        sys.argv.remove('--ignore-gooey')

class CustomArgumentParser(argparse.ArgumentParser):
    
    def add_argument(self, *args, **kwargs):
        if 'widget' in kwargs:
            del kwargs['widget']
        return super().add_argument(*args, **kwargs)

def create_parser(parser, command, prog, description):
    if parser is None:
        # Try creating a GooeyParser for a nice GUI if Gooey is installed, otherwise create a regular parser
        try:
            from gooey import GooeyParser
            return GooeyParser(prog=prog, description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        except ModuleNotFoundError:
            return CustomArgumentParser(prog=prog, description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    return parser.add_parser(command, description=description, help=description)

def parse_args(args, create_parser, add_args):
    if args is None:
        parser = create_parser()
        add_args(parser)
        remove_ignore_gooey()
        args = parser.parse_args()
    return args

def get_bundle_path():
    return Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).parent.resolve()