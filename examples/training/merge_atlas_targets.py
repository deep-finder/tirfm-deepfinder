import numpy as np
import os
import h5py
import SimpleITK as sitk
import xml.etree.ElementTree as ET
import random

# no equivalent in python for clear all and close all
# changing directory structure
prefix = '/Users/amasson/Remotes/serpico-fs2/emoebel'

# path_atlas_segmaps = os.path.join(prefix, 'tirfm_exocytose/paper/data/atlas/segmentations_h5')
path_atlas_segmaps = os.path.join('/Users/amasson/Documents/tirfm_exocytose/segmentations_h5')

listing = sorted(list(os.listdir(path_atlas_segmaps)))

path_dset = os.path.join(prefix, 'tirfm_exocytose/paper/data/for_deepfinder/dataset')
output_path = '/Users/amasson/Documents/tirfm_exocytose/segmentations_merged_h5'

if not os.path.exists(output_path):
    os.mkdir(output_path)

def objlist2motl(objlist_path):
    """Translate function from MATLAB. Returns the motive list filled up with particle information from xml file.

    Args:
    objlist_path: path to objective list xml file

    Returns:
    motl: the motive list filled up with particle informations from xml file

    """
    # Parsing the xml file
    tree = ET.parse(objlist_path)
    root = tree.getroot()

    Npart = len(root)
    motl = np.zeros((20, Npart))

    for idx, child in enumerate(root):
        attributes = child.attrib
  
        # TomoID (first test if field exists)
        if 'tomo_idx' in attributes:
            motl[4, idx] = int(attributes['tomo_idx'])
  
        # Cluster size (first test if field exists)
        if 'cluster_size' in attributes:
            motl[6, idx] = int(attributes['cluster_size'])

        # Position
        if 'x' in attributes:
            motl[7, idx] = float(attributes['x']) + 1  # +1 because of idx difference between python and matlab
  
        if 'y' in attributes:
            motl[8, idx]  = float(attributes['y']) + 1
  
        if 'z' in attributes:
            motl[9, idx] = float(attributes['z']) + 1  # with actual deepfind [x,y,z] order is now like this
        
        # Class
        if 'class_label' in attributes:
            motl[19, idx] = int(attributes['class_label'])
      
    return motl

# def motl_compare(motl_exo, motl, value):
#     # Implement this function as in Matlab
#     pass

from scipy.spatial import distance

def motl_compare(motlA, motlB, R):
    """Gives back a list of particles that motlA and motlB have in common, given a distance error R.

    Args:
    motlA, motlB: the two motive lists to compare
    R: the allowed position error (in pixels)

    Returns:
    D: matrix where first column contains motlA idx, second column contains motlB idx

    """
    # Getting the coordinates
    coordsA = motlA[7:10, :].T
    coordsB = motlB[7:10, :].T

    # Computing pairwise distance between two sets
    D = distance.cdist(coordsA, coordsB, 'euclidean')

    # Keep only distances<R
    D = D <= R

    return D

def motl2objlist(motl, filename):
    """Writes a .xml object list from a motive list.

    Args:
    motl: the motive list
    filename: where to write xml file

    """
    # Creating root element
    obj_list = ET.Element('objlist')

    for idx in range(motl.shape[1]):
        
        # Getting the properties
        tomoID = str(int(motl[4, idx]))
        x = str(motl[7, idx]-1)
        y = str(motl[8, idx]-1)
        z = str(motl[9, idx]-1)
        phi = str(motl[16, idx])
        psi = str(motl[17, idx])
        the = str(motl[18, idx])
        class_label = str(int(motl[19, idx]))

        # Creating 'object' element with attributes
        object_element = ET.SubElement(obj_list, 'object')
        object_element.attrib['tomo_idx'] = tomoID
        object_element.attrib['class_label'] = class_label
        object_element.attrib['x'] = x
        object_element.attrib['y'] = y
        object_element.attrib['z'] = z
        object_element.attrib['phi'] = phi
        object_element.attrib['psi'] = psi
        object_element.attrib['the'] = the

    # Creating the xml tree and write to file
    tree = ET.ElementTree(obj_list)
    ET.indent(tree)
    tree.write(filename)


for IDX in range(0, 2):# 60): # starts from 3 because python list indexing starts from 0
    folder_name = listing[IDX]
    print(f'{IDX} ============= {folder_name} ....')
    
    print('Read inputs')
    motl_exo = objlist2motl(os.path.join(path_dset, folder_name, 'objl.xml'))
    
    with h5py.File(os.path.join(path_atlas_segmaps, folder_name, 'segmap_atlas.h5'), 'r') as hf:
        seg = np.array(hf.get('dataset'), dtype=np.int8)
    
    # % this operation is needed to get correct orientation:
    # %seg = permute(seg, [2 1 3]);
    print('Atlas segmentation has size:', seg.shape)

    print('Computing connected components in atlas segmentation...')
    # - Remove exocytose events from atlas segmentation seg <- custom
    # - Create a motl_normal with all other events
    # - Merge motl_normal and exocytose events and subsample
    
    image = sitk.GetImageFromArray(seg)
    label = sitk.ConnectedComponent(image, True)
    label_array = sitk.GetArrayFromImage(label)

    # lsif = sitk.LabelStatisticsImageFilter()
    # lsif.Execute(image, label)

    # N = lsif.GetNumberOfLabels()

    lssif = sitk.LabelShapeStatisticsImageFilter()
    lssif.Execute(label)
    N = lssif.GetNumberOfLabels()
    
    # # Get 3D CC, and erase CCs that correspond to annotated exo spots:
    # CC3d = measure.label(seg, connectivity=2)

    target = seg
    # #
    # S = measure.regionprops(CC3d)
    # N  = len(S)
    
    print('Creating movie list from detected centroids...')

    motl = np.zeros((20,N))
    for idx in range(1, N+1):
        # bb = lsif.GetBoundingBox(idx)
        # center = [(bb[2*i] + bb[2*i+1]) / 2 for i in range(3)]
        centroid = lssif.GetCentroid(idx)
        motl[5, idx-1] = idx
        motl[6, idx-1] = lssif.GetNumberOfPixels(idx)
        motl[7, idx-1] = centroid[0]+1 # SimpleIKT y -> numpy y
        motl[8, idx-1] = centroid[1]+1 # SimpleIKT x -> numpy z
        motl[9, idx-1] = centroid[2]+1 # SimpleITK z -> numpy x
    
    print('Comparing detected centroid with exocytose events...')
    D = motl_compare(motl_exo, motl, 5)
    vect_corresp = np.sum(D, axis=0) # only considered as TP if =1
    # Erase all spots that correspond to exocytosis
    print('Erasing exocytosis spots from atlas segmentation...')
    target[np.isin(label_array, [i+1 for i in np.where(vect_corresp==1)])] = 0
    
    print('Creating a movie list from all remaining spots, slice by slice...')
    # Now get 2D CC to get coordinates of "normal" spots.
    # We use 2D CC because the spot detector (Atlas) operates in 2D
    motl_normal = []
    for s in range(target.shape[2]):
        # CC2d = measure.label(target[s,:,:], connectivity=2)
        # S = measure.regionprops(CC2d)
        # N = len(S)
        # for idx in range(N):
        #     m = np.zeros(20)
        #     m[5] = idx + 1
        #     m[6] = np.count_nonzero(CC2d == S[idx].label)
        #     m[7] = S[idx].centroid[1]
        #     m[8] = S[idx].centroid[0]
        #     m[9] = s

        if s%100==0:
            print('Slice', s, 'of', target.shape[2])
        image = sitk.GetImageFromArray(target[s,:,:])
        label = sitk.ConnectedComponent(image, True)
        label_array = sitk.GetArrayFromImage(label)
        lssif = sitk.LabelShapeStatisticsImageFilter()
        lssif.Execute(label)
        N = lssif.GetNumberOfLabels()
        for idx in range(1, N+1):
            m = np.zeros(20)
            m[5] = idx
            m[6] = np.count_nonzero(label_array == idx)
            centroid = lssif.GetCentroid(idx)
            m[7] = centroid[0] + 1 # S[idx].centroid[1]
            m[8] = centroid[1] + 1 # S[idx].centroid[0]
            m[9] = s + 1
            
            motl_normal.append(m)
    
    motl_normal = np.column_stack(motl_normal)
    

    # Fuse object lists and seg target
    N = 9800 # % motl_normal is way too big (~70k) therefore subsample
    print(f'Sampling {N} detections among {motl_normal.shape[1]}...')
    motl_normal = random.sample(range(motl_normal.shape[1]), N)
    # idx_rnd = range(N)
    # motl_normal = motl_normal[:,idx_rnd]
    
    print(f'Merging normal (class 1) and exocytose (class 2) events...')
    motl_normal[19,:] = 1 # % 'normal' spot is class1;
    motl_exo[19,:] = 2 # % 'exo' spot is class2;
    
    motl_final = np.column_stack((motl_exo, motl_normal))
    
    print(f'   Reading exocytose segmentation...')
    # Fuse targets
    with h5py.File(os.path.join(path_dset, folder_name, 'target.h5'), 'r') as hf:
        target_exo = np.array(hf.get('dataset'))
    
    print(f'   Overwriting final segmentation...')
    target[target_exo==1] = 2
    
    print('Writing results...')
    # Commented out as h5py doesn't have a direct equivalent for h5create. h5py automatically creates datasets.

    if not os.path.exists(os.path.join(output_path, folder_name)):
        os.mkdir(os.path.join(output_path, folder_name))
    
    # Save data:
    with h5py.File(os.path.join(output_path, folder_name, 'target_wAtlas.h5'), 'w') as hf:
        hf.create_dataset('/dataset', data=target, dtype='i8')
    
    motl2objlist(motl_final, os.path.join(output_path, folder_name, 'objl_with_atlas.xml'))

