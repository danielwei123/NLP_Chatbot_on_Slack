import cv2
import numpy as np
import sys
sys.path.insert(0,'/Users/internship111/Library/Python/2.7/bin/')

import skimage.exposure
import os
import matplotlib.pyplot as plt

def retrieve_img(file_path, img_name):
    complete_path = file_path + img_name
    print(complete_path)
    return cv2.imread(complete_path, 1)

def adapthist_normalize(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_rgb = skimage.exposure.equalize_adapthist(img_rgb)
    img_rgb = skimage.img_as_ubyte(img_rgb)
    img_bgr =  cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    return img_bgr

def create_modified_stitcher():
    stitcher = cv2.createStitcher(False) #don't use GPU
    stitcher.setPanoConfidenceThresh(.05)  # changed from .5, basically makes it a 'make a panorama at any cost, even if it's terrible' function
    stitcher.setRegistrationResol(.6)  # changed from .5, expands the image a little bit, might change later
    stitcher.setCompositingResol(-1)  # doesnt really make a difference, left at default
    stitcher.setSeamEstimationResol(.1)  # this is supposed to smooth out seam connections, but doesn't seem to really matter. also heavily increases computation time
    return stitcher

def binary_image_stitcher(img_directory):
    all_imgs = [img for img in os.listdir(img_directory) if img.endswith('.jpg')]
    all_imgs.sort(key=lambda x: int(x.split('.')[0])) #sort by last number of the file
    print(all_imgs)
    all_imgs = [np.array(retrieve_img(img_directory, img_name)) for img_name in all_imgs if img_name.endswith('jpg')]
    stitcher = create_modified_stitcher()
    stich_groups = []
    while len(all_imgs) != 1:
        if len(all_imgs) == 2:
            cv2.imwrite(img_directory + "pano1.jpg", all_imgs[0])
            cv2.imwrite(img_directory + "pano2.jpg", all_imgs[1])
        if any([img is None for img in all_imgs]):
            return None
        all_imgs = [adapthist_normalize(img) for img in all_imgs] #histogram normalization
        all_imgs = [all_imgs[i:i + 2] for i in range(0, len(all_imgs), 2)] #divide into subgroups of two
        print('Len of all_imgs: ' + str(len(all_imgs)))
        for grouping_num in range(0, len(all_imgs)): #for each subgroup
            num, all_imgs[grouping_num] = stitcher.stitch((all_imgs[grouping_num][0], all_imgs[grouping_num][1])) #combine elements in both subgroups
            print(grouping_num)
            stich_groups.append(all_imgs[grouping_num])
    if all_imgs[0] is None:
        return None
    return all_imgs[0]