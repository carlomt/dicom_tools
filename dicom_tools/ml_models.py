
from keras.models import Model
from keras.layers import Input, concatenate, Conv2D, MaxPooling2D, Conv2DTranspose
from keras.layers import  merge, UpSampling2D, Dropout, Cropping2D, BatchNormalization
from keras.initializers import RandomNormal, VarianceScaling
import numpy as np
import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"]="1"
from keras import backend as K
K.set_image_data_format('channels_last')

#Adopted from https://github.com/pietz/unet-keras
#Added kernel initializers based on VarianceScaling
def conv_block(m, dim, acti, bn, res, do=0, stride=1 ):

    init = VarianceScaling(scale=1.0/9.0 )
    n = Conv2D(dim, 3,strides=1 ,activation=acti, padding='same', kernel_initializer=init )(m)
    n = BatchNormalization()(n) if bn else n
    n = Dropout(do)(n) if do else n
    #n = Conv2D(dim, 3,strides=stride, activation=acti, padding='same', kernel_initializer=init)(n)
    n = Conv2D(dim, 3,strides=stride, activation=acti, padding='same', kernel_initializer=init)(n)
    n = BatchNormalization()(n) if bn else n

    return concatenate([n, m], axis=3) if res else n

def level_block(m, dim, depth, inc, acti, do, bn, mp, up, res):
	if depth > 0:
		n = conv_block(m, dim, acti, bn, res)
		m = MaxPooling2D()(n) if mp else Conv2D(dim, 3, strides=2, padding='same')(n)
		m = level_block(m, int(inc*dim), depth-1, inc, acti, do, bn, mp, up, res)#chiamata ricorsiva a level_block
		if up:
			m = UpSampling2D()(m)
			m = Conv2D(dim, 2, activation=acti, padding='same')(m)
		else:
			m = Conv2DTranspose(dim, 3, strides=2, activation=acti, padding='same')(m)
		n = concatenate([n, m], axis=3)
		m = conv_block(n, dim, acti, bn, res)
	else:
		m = conv_block(m, dim, acti, bn, res, do)
	return m


def UNet(img_shape, out_ch=1, start_ch=64, depth=4, inc_rate=2., activation='relu',
		 dropout=0.0, batchnorm=False, maxpool=True, upconv=False, residual=False):

	i = Input(shape=img_shape)
	o = level_block(i, start_ch, depth, inc_rate, activation, dropout, batchnorm, maxpool, upconv, residual)
	o = Conv2D(out_ch, 1, activation='sigmoid')(o)
	return Model(inputs=i, outputs=o)



#added inverted-net from novikov 02-18 see biblio for details
# when to concatenate? [up,conv] or [conv,conv]

def InvertedNet(img_shape, out_ch=1, start_ch=256, activation='relu', dropout=0.1, batchnorm=False, residual=False):
    
    
    i = Input(shape=img_shape)
    
#    cb1 = conv_block(i, start_ch, activation, batchnorm, residual, dropout,stride=1)
#    m1 = MaxPooling2D(strides=(1,1))(cb1)
#    cb2 = conv_block(m1, int(start_ch/2), activation, batchnorm, residual, dropout,stride=1)
#    m2 = MaxPooling2D(strides=(1,1))(cb2)
#    cb3 = conv_block(m2, int(start_ch/4), activation, batchnorm, residual, dropout,stride=2)
#    m3 = MaxPooling2D(strides=(1,1))(cb3)
#    cb4 = conv_block(m3, int(start_ch/8), activation, batchnorm, residual, dropout,stride=2)
#    m4 = MaxPooling2D(strides=(1,1))(cb4)
#    cb5 = conv_block(m4, int(start_ch/16), activation, batchnorm, residual, dropout,stride=2)
#    up1 = UpSampling2D()(cb5)
#   
#    cb6 = conv_block(up1, int(start_ch/8), activation, batchnorm, residual, dropout,stride=1)
#    up2 = UpSampling2D()(cb6)
#    up2 = concatenate([up2, cb4], axis=3)
#    cb7 = conv_block(up2, int(start_ch/4), activation, batchnorm, residual, dropout,stride=1)
#    up3 = UpSampling2D()(cb7)
#    up3 = concatenate([up3, cb3], axis=3)
#    cb8 = conv_block(up3, int(start_ch/2), activation, batchnorm, residual, dropout,stride=1)
#    deConv1 = Conv2DTranspose(img_shape, 3, strides=2, activation=activation, padding='same')(cb8)
#    #deConv1 = concatenate([deConv1, cb1], axis=3)
#    cbLast = conv_block(deConv1, int(start_ch), activation, batchnorm, residual, dropout,stride=1)
    # 256
    l1 = conv_block(i, int(start_ch/2), activation, batchnorm, residual, dropout,stride=1)
   #128
    l2 = MaxPooling2D(strides=1,padding='same')(l1)
    l2 = conv_block(l2, int(start_ch/2), activation, batchnorm, residual, dropout,stride=1)
   #64 
    l3 = MaxPooling2D(strides=1,padding='same')(l2)
    l3 = conv_block(l3, int(start_ch/4), activation, batchnorm, residual, dropout,stride=2)
    #32
    l4 = MaxPooling2D(strides=1,padding='same')(l3)
    l4 = conv_block(l4, int(start_ch/8), activation, batchnorm, residual, dropout,stride=2)
    #16
    l5 = MaxPooling2D(strides=1,padding='same')(l4)
    l5 = conv_block(l5, int(start_ch/16), activation, batchnorm, residual, dropout,stride=2)
   #32
    l6 = UpSampling2D()(l5)
    l6 = conv_block(l6, int(start_ch/8), activation, batchnorm, residual, dropout,stride=1)
    #l6 = concatenate([l6, l4], axis=3)
    #64
    l7 = UpSampling2D()(l6)
    l7 = conv_block(l7, int(start_ch/4), activation, batchnorm, residual, dropout,stride=1)
    l7 = concatenate([l7, l3], axis=3)
    #128
    l8 = UpSampling2D()(l7)
    l8 = conv_block(l8, int(start_ch/2), activation, batchnorm, residual, dropout,stride=1)
    l8 = concatenate([l8, l2], axis=3)
    #256
    #l9 = UpSampling2D()(l8)
    l9 = conv_block(l8, int(start_ch/2), activation, batchnorm, residual, dropout,stride=1)
    l9= concatenate([l9, l1], axis=3)
 
    
    o = Conv2D(out_ch, 1, activation='sigmoid')(l9)
    
    
    return Model(inputs=i, outputs=o)
    
def AllDropOut(img_shape, out_ch=1, start_ch=64, activation='relu', dropout=0.1, batchnorm=False, residual=False):
    
    
    i = Input(shape=img_shape)
    
#    cb1 = conv_block(i, start_ch, activation, batchnorm, residual, dropout,stride=1)
#    m1 = MaxPooling2D()(cb1)
#    cb2 = conv_block(m1, int(start_ch*2), activation, batchnorm, residual, dropout,stride=1)
#    m2 = MaxPooling2D()(cb2)
#    cb3 = conv_block(m2, int(start_ch*4), activation, batchnorm, residual, dropout,stride=1)
#    m3 = MaxPooling2D()(cb3)
#    cb4 = conv_block(m3, int(start_ch*8), activation, batchnorm, residual, dropout,stride=1)
#    m4 = MaxPooling2D()(cb4)
#    cb5 = conv_block(m4, int(start_ch*16), activation, batchnorm, residual, dropout,stride=1)
#    up1 = UpSampling2D()(cb5)
#    up1 = concatenate([up1, cb4], axis=3)
#    cb6 = conv_block(up1, int(start_ch*8), activation, batchnorm, residual, dropout,stride=1)
#    
#    up2 = UpSampling2D()(cb6)
#    up2 = concatenate([up2, cb3], axis=3)
#    cb7 = conv_block(up2, int(start_ch*4), activation, batchnorm, residual, dropout,stride=1)
#    
#    up3 = UpSampling2D()(cb7)
#    up3 = concatenate([up3, cb2], axis=3)
#    cb8 = conv_block(up3, int(start_ch*2), activation, batchnorm, residual, dropout,stride=1)
#    
#    up4 = UpSampling2D()(cb8)
#    up4 = concatenate([up4, cb1], axis=3)
#    cbLast = conv_block(up4, start_ch, activation, batchnorm, residual, dropout,stride=1)
    
    cb1 = conv_block(i, 64, activation, False, residual, dropout,stride=1)#no batch norm at first layer
    m1 = MaxPooling2D()(cb1)
    cb2 = conv_block(m1, 64, activation, batchnorm, residual, dropout,stride=1)
    m2 = MaxPooling2D()(cb2)
    cb3 = conv_block(m2, 128, activation, batchnorm, residual, dropout,stride=1)
    m3 = MaxPooling2D()(cb3)
    cb4 = conv_block(m3, 128, activation, batchnorm, residual, dropout,stride=1)
    m4 = MaxPooling2D()(cb4)
    cb5 = conv_block(m4, 128, activation, batchnorm, residual, dropout,stride=1)
    up1 = UpSampling2D()(cb5)
    up1 = concatenate([up1, cb4], axis=3)
    cb6 = conv_block(up1, 256, activation, batchnorm, residual, dropout,stride=1)
    
    up2 = UpSampling2D()(cb6)
    up2 = concatenate([up2, cb3], axis=3)
    cb7 = conv_block(up2, 128, activation, batchnorm, residual, dropout,stride=1)
    
    up3 = UpSampling2D()(cb7)
    up3 = concatenate([up3, cb2], axis=3)
    cb8 = conv_block(up3, 128, activation, batchnorm, residual, dropout,stride=1)
    
    up4 = UpSampling2D()(cb8)
    up4 = concatenate([up4, cb1], axis=3)
    cbLast = conv_block(up4, 128, activation, batchnorm, residual, dropout,stride=1)
   
    
    o = Conv2D(out_ch, 1, activation='sigmoid')(cbLast)
    
    
    return Model(inputs=i, outputs=o)


if  __name__=='__main__':
    img_shape=(256, 256,1)
    #model = UNet(img_shape, start_ch=16, depth=5, batchnorm=True, dropout=0.5, maxpool=True, residual=False,upconv=True)
    model = AllDropOut((256, 256,1), out_ch=1, start_ch=64, activation='relu', dropout=0.1, batchnorm=True, residual=False)
    #model= InvertedNet(img_shape, out_ch=1, start_ch=256, activation='elu', dropout=0.1, batchnorm=True, residual=False)
    model.summary()
