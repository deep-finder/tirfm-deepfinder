# Deep Finder

This is a fork of DeepFinder customized for use in TIRF microscopy, designed for detecting exocytosis events. 

## Contents
- [System requirements](##System requirements)
- [Installation guide](##Installation guide)
- [Instructions for use](##Instructions for use)
- [Documentation](https://cryoet-deepfinder.readthedocs.io/en/latest/)
- [Google group](https://groups.google.com/g/deepfinder)

## System requirements
**Deep Finder** has been implemented using **Python 3** and is based on the **Tensorflow** package. It has been tested on Linux (Debian 10), and should also work on Mac OSX as well as Windows.

### Package dependencies
Deep Finder depends on following packages. The package versions for which our software has been tested are displayed in brackets:
```
tensorflow   (2.11.1)
lxml         (4.9.3)
mrcfile      (1.4.3)
scikit-learn (1.3.2)
scikit-image (0.22.0)
matplotlib   (3.8.1)
PyQt5        (5.13.2)
pyqtgraph    (0.13.3 )
openpyxl     (3.1.2)
pycm         (4.0)
```

## Installation guide
Before installation, you need a python environment on your machine. 
If this is not the case, we advise installing [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

(Optional) Before installation, we recommend first creating a virtual environment that will contain your DeepFinder installation:
```
conda create --name dfinder python=3.9
conda activate dfinder
```

Now, you can install DeepFinder with pip:
```
pip install -e /path/to/tirfm-deepfinder
```

Also, in order for Tensorflow to work with your Nvidia GPU, you need to install CUDA. 
An alternative could be to install the python packages `cudatoolkit` and `cudnn`.
Once these steps have been achieved, the user should be able to run DeepFinder.

## Instructions for use
### Using the scripts
Instructions for using Deep Finder are contained in folder examples/. The scripts contain comments on how the toolbox should be used. To run a script, first place yourself in its folder. For example, to run the target generation script:
```
cd examples/training/
python step1_generate_target.py
```

### Using the GUI
TODO: Napari plugin