import numpy as np
import scipy as sp

from sklearn.feature_extraction.image import grid_to_graph
from sklearn.cluster import AgglomerativeClustering
from sklearn.utils.testing import SkipTest
from sklearn.utils.fixes import sp_version

import time as time

import matplotlib.pyplot as plt

def wardHierarchical(img):
    connectivity = grid_to_graph(*img.shape)
    print("Compute structured hierarchical clustering...")
    st = time.time()
    n_clusters = 15  # number of regions
    ward = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward',
                                   connectivity=connectivity)
    
    face = sp.misc.imresize(img, 0.10) / 255.
    X = np.reshape(img, (-1, 1))
    ward.fit(X)
    label = np.reshape(ward.labels_, face.shape)
    print("Elapsed time: ", time.time() - st)
    print("Number of pixels: ", label.size)
    print("Number of clusters: ", np.unique(label).size)


    plt.figure(figsize=(5, 5))
    plt.imshow(face, cmap=plt.cm.gray)
    for l in range(n_clusters):
        plt.contour(label == l, contours=1,
                    colors=[plt.cm.spectral(l / float(n_clusters)), ])
    plt.xticks(())
    plt.yticks(())
    plt.show()
