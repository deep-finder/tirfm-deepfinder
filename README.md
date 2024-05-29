# Deep Finder

This is a fork of [DeepFinder](https://github.com/deep-finder/cryoet-deepfinder) customized for use in TIRF microscopy, designed for detecting exocytosis events. 

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

Instructions for using Deep Finder are contained in folder examples/. The scripts contain comments on how the tool should be used.

### Training


To run the training, you should have a folder containing your data organised in the following way:

```
data/
├── train
│   ├── movie1.h5
│   ├── movie1_objl.xml
│   ├── movie1_target.h5
│   ├── movie2.h5
│   ├── movie2_objl.xml
│   ├── movie2_target.h5
...
└── valid
    ├── movie3.h5
    ├── movie3_objl.xml
    ├── movie3_target.h5
...
```

The targets must contain 2 classes:
- the exocytose events, delineated by experts,
- the other brigth spots, which are not exocytose events, and are detected by the [Atlas](https://gitlab.inria.fr/serpico/atlas) spot detector.

Once the experts have annotated the training and validation images by creating the `objl.xml` files describing the exocytose events, the corresponding segmentations must be generated with the `step1_generate_target.py` script (`cd examples/training/`, then `python step1_generate_target.py`). This will create a segmentation from all events, each with the predefined exocytose shape.

Then, the other non-exocytose events must be detected with [Atlas](https://gitlab.inria.fr/serpico/atlas). The installation instructions are detailed in the Atlas repository.

Once Atlas is installed, you can generate the bright spots segmentations and convert them to the h5 format with the following commands:
- `python compute_segmentations.py -a build/atlas -d path/to/dataset/ -o path/to/output/segmentations/`
- `python convert_tiff_to_h5.py -s path/to/output/segmentations/ -o path/to/output/segmentations_h5/`

Use `python compute_segmentations.py --help` and `python convert_tiff_to_h5.py --help` for more information about those tools.

Then, the experts segmentations must be merged with the Atlas detections with the `step2_merge_atlas_targets.py` script.

Finally, the training can be launched with `step3_launch_training.py`.

### Prediction

Predictions can be generated with the `step1_launch_segment.py` script. 

This will generate binary segmentations ; the `step2_launch_clustering.py` script can convert them to distinct spots, so that each event gets a unique label.

Finally, the results can be evaluated with the `step3_launch_evaluation.py` (which will make use of the `evaluate.py` tool).

#### Using the GUI

TODO: Napari plugin