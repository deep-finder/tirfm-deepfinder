# ExoDeepFinder

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

## Usage

To detect exocytose events, you can either use the pretrained model to generate segmetations, or you can train your own model from your annotated images.

In all case, the first step is to convert your input tiff files into h5 files with the `convert_tiff_to_h5` command.

### Exocytose events segmentation

To generate segmentations, you can either use the `napari-exodeepfinder` plugin which provide a simple graphical interface, or you can run the following command lines.

To segment an image, use:
`segment --image path/to/image.h5 --model_weights examples/analyze/in/net_weights_FINAL.h5 --patch_size 160 --visualization`

This will generate a segmentation named `path/to/image_semgmentation.h5` with the pretrained weigths in `examples/analyze/in/net_weights_FINAL.h5` and patches of size 160. It will also generate visualization images.

See `segment --help` for more information about the input arguments.

To cluster a segmentation and create an annotation file from it, use:
`cluster --segmentation path/to/image_segmentation.h5 --cluster_radius 5`

An example script for evaluating the results can be found in `examples/analyze/step3_launch_evaluation.py`.

#### Using the GUI

The [napari-deepfinder](https://github.com/deep-finder/napari-deepfinder) plugin can be used to perform perictions.
Open the image you want to segment in napari.
In the menu, choose `Plugins > Napari DeepFinder > Segment`  to open the segmentation tools.
Choose the image layer you want to segment.
Select the `examples/analyze/in/net_weights_FINAL.h5` net weights ; or the path of the model weights you want to use for the segmentation.
Use 3 for the number of class, and 160 for the patch size.
Choose an output image name (with the .h5 extension), then launch the segmentation.

### Training

To train a model, you need annotated movies, split in two sets: a training set and a validation set.

Organise your movies in the following way:

```
exocytose_data
├── train
│   ├── movie1.h5
│   ├── movie2.h5
│   ├── ...
└── valid
    ├── movieN.h5
    ├── ...
```

Annotate the exocytose events in the movies with the [napari-deepfinder](https://github.com/deep-finder/napari-deepfinder) plugin.
Follow the install instructions, and open napari.
In the menu, choose `Plugins > Napari DeepFinder > Annotation`  to open the annotation tools.
Open the first training movie.
Create a new points layer, and name it `movie1_1` (name of the movie with the `_1` suffix, since we want to annotate with the class 1).
You can use the Orthoslice view to easily navigate in the volume, by using the `Plugins > Napari DeepFinder > Orthoslice view` menu.
Scroll in the movie until you find and exocytose event.
Click on an exocytose event to put the red cursor at its location, then click the "Add points" button to annotate the event.
When you annotated all events, save your annotations to xml by choosing the `File > Save selected layer(s)...` menu, or by using ctrl+S (command+S on a mac), **and choose the *Napadi DeepFinder (\*.xml)* format**. Save the file beside the movie, and name it `movie1_expert_annotations.xml` (name of the movie with the `_expert_annotations.xml` suffix).
Annotate all training and validation movies with this procedure ; you should end up with the following folder structure:

```
exocytose_data
├── train
│   ├── movie1.h5
│   ├── movie1_expert_annotations.xml
│   ├── movie2.h5
│   ├── movie2_expert_annotations.xml
│   ├── ...
└── valid
    ├── movieN.h5
    ├── movieN_expert_annotations.xml
    ├── ...
```

Use the `generate_segmentations` command to convert the annotations to segmentations:

`generate_segmentations -i exocytose_data/train/`

then 

`generate_segmentations -i exocytose_data/valid/`

You will end up with the following structure:

```
exocytose_data
├── train
│   ├── movie1.h5
│   ├── movie1_expert_annotations.xml
│   ├── movie1_expert_segmentation.h5
│   ├── movie2.h5
│   ├── movie2_expert_annotations.xml
│   ├── movie2_expert_segmentation.h5
│   ├── ...
└── valid
    ├── movieN.h5
    ├── movieN_expert_annotations.xml
    ├── movieN_expert_segmentation.h5
    ├── ...
```

Then, the other non-exocytose spots (spots with no exponential decay, whose luminescence remains constant through frames) must be detected with a spot detector such as [Atlas](https://gitlab.inria.fr/serpico/atlas) (or any spot detector). The Atlas installation instructions are detailed in the repository.

Once Atlas is installed, you can generate the spots segmentations and convert them to the h5 format with the following commands:
- `python compute_segmentations.py -a build/atlas -d path/to/dataset/ -o path/to/output/segmentations/`
- `python convert_tiff_to_h5.py -s path/to/output/segmentations/ -o path/to/output/segmentations_h5/`

Use `python compute_segmentations.py --help` and `python convert_tiff_to_h5.py --help` for more information about those tools.



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
- the exocytose events, delineated by experts (class 2),
- the other bright spots, which are not exocytose events, and are detected by the [Atlas](https://gitlab.inria.fr/serpico/atlas) spot detector (class 1).

Once the experts have annotated the training and validation images by creating the `objl.xml` files describing the exocytose events, the corresponding segmentations must be generated with the `step1_generate_target.py` script (`cd examples/training/`, then `python step1_generate_target.py`). This will create a segmentation from all events, each with the predefined exocytose shape.

Then, the other non-exocytose events must be detected with [Atlas](https://gitlab.inria.fr/serpico/atlas). The installation instructions are detailed in the repository.

Once Atlas is installed, you can generate the bright spots segmentations and convert them to the h5 format with the following commands:
- `python compute_segmentations.py -a build/atlas -d path/to/dataset/ -o path/to/output/segmentations/`
- `python convert_tiff_to_h5.py -s path/to/output/segmentations/ -o path/to/output/segmentations_h5/`

Use `python compute_segmentations.py --help` and `python convert_tiff_to_h5.py --help` for more information about those tools.

Then, the experts segmentations must be merged with the Atlas detections with the `step2_merge_atlas_targets.py` script.

Finally, the training can be launched with `step3_launch_training.py`.

