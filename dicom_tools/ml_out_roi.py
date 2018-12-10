#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 09:46:37 2018

@author: andrea
"""

from __future__ import division, print_function

import cv2
import numpy as np

try:
    from keras import backend as K
    K.set_image_data_format('channels_last')
    keras_found = True
except ImportError:
    keras_found = False
    print("WARNING ml_out_roi.py: keras not found")
import SimpleITK as sitk
from skimage.transform import resize
from skimage.exposure import equalize_adapthist

from dicom_tools.ml_models import *
#from metrics import *

def check_import_keras():
    return keras_found

def get_model(img_rows, img_cols):
    #model = UNet((img_rows, img_cols,1), start_ch=16, depth=5, batchnorm=True, dropout=0.5, maxpool=True, residual=False,upconv=True)
    model = AllDropOut((img_rows, img_cols,1), out_ch=1, start_ch=64, activation='relu', dropout=0.1, batchnorm=True, residual=False)
    #model= InvertedNet((img_rows, img_cols,1), out_ch=1, start_ch=256, activation='elu', dropout=0.1, batchnorm=True, residual=False)
    model.load_weights('weights.h5')
    #model.compile(  optimizer=Adam(), loss=dice_coef_loss, metrics=[dice_coef])
    return model

def single_img_resize(img, img_rows, img_cols, equalize=True):

    new_img = np.zeros([img_rows,img_cols])
    
    if equalize:
        img = equalize_adapthist( img, clip_limit=0.05 )
            # img = clahe.apply(cv2.convertScaleAbs(img))

    new_img = cv2.resize( img, (img_rows, img_cols), interpolation=cv2.INTER_NEAREST )

    return new_img

def smooth_images(imgs, t_step=0.125, n_iter=5):
    """
    Curvature driven image denoising.
    In my experience helps significantly with segmentation.
    """

    for mm in range(len(imgs)):
        img = sitk.GetImageFromArray(imgs[mm])
        img = sitk.CurvatureFlow(image1=img,
                                        timeStep=t_step,
                                        numberOfIterations=n_iter)

        imgs[mm] = sitk.GetArrayFromImage(img)


    return imgs

def pre_process_img(numpy_imgs):
    
    img_rows=256
    img_cols=256
    numpy_imgs=numpy_imgs[:,:,:,0]
    numpy_imgs=(numpy_imgs-numpy_imgs.min())/(numpy_imgs.max()-numpy_imgs.min())
    
    images=[]
    for i in range(numpy_imgs.shape[0]):
        
        imgs= single_img_resize(numpy_imgs[i,:,:], img_rows, img_cols, equalize=True)
        images.append( imgs )

    images=np.array(images).reshape(-1, img_rows, img_cols, 1)
    images = smooth_images(images)
    mu = np.mean(images)
    sigma = np.std(images)
    images = (images - mu)/sigma
    
    return images
    
def post_process_img(numpy_imgs,img_rows,img_cols):
    
    
    numpy_imgs=numpy_imgs[:,:,:,0]
    
    images=[]
    for i in range(numpy_imgs.shape[0]):
        
        imgs= single_img_resize(numpy_imgs[i,:,:], img_rows, img_cols, equalize=False)
        images.append( imgs )

    images=np.array(images)
    
    
    
    
    return images

def use_net( X_test,regenerate=True ):

    img_rows = X_test.shape[1]
    img_cols = X_test.shape[2]

    model = get_model(img_rows, img_cols)

    if regenerate:
        y_pred = model.predict( X_test, verbose=1,batch_size=4)
    else:
        y_pred=np.load('last_prediction.npy')
    return y_pred

# if __name__=='__main__':
def ml_out_roi(data):
    # X_test_dt = np.load('X_test_dt.npy')
    X_test_dt = data
    X_test_dt=np.transpose(X_test_dt[:,:,::-1,:], (0, 2, 1,3))
    imgs=pre_process_img(X_test_dt)
    
    pred = use_net( imgs,regenerate=True )
    #np.save('last_prediction.npy',pred)
    
    x=post_process_img(pred,X_test_dt.shape[1],X_test_dt.shape[2])        
    # x=np.transpose(x[:,:,::-1,:], (0, 2, 1,3))
    x=np.transpose(x[:,::-1,:], (0, 2, 1))

    return x
    
#NON necessario
#    import scipy.misc
#    for i in range(pred.shape[0]):
#       
#        scipy.misc.toimage( x[i,:,:], cmin=0.0, cmax=1.0).save('pred/outfile_'+str(i)+'.jpg')
    
    
