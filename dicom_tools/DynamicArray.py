from __future__ import print_function
import numpy as np

class DynamicArray(object):
    def __init__(self, dtype, size=10):
        self.dtype = np.dtype(dtype)
        self.length = 0
        self.size = size
        self.STRIDE = size
        self._data = np.empty(self.size, dtype=self.dtype)

    def __len__(self):
        return self.length

    def append(self, val):
        if self.length == self.size:
            self.size += self.STRIDE
            self._data = np.resize(self._data, self.size)
        self._data[self.length] = val
        self.length +=1

    def __getitem__(self,index):
        i = index
        if index<0:
            i = self.length + index 
        if i<self.length and i>=0:
            return self._data[i]
        else:
            raise IndexError('index',index,' is out of bounds. Size:',self.length)

    def __setitem__(self,index,val):
        self._data[index] = val

    # def __delitem__(self,...

    
    def __iter__(self):
        for i in xrange(0,self.length):
            yield self._data[i]

    def __reversed__(self):
        for i in xrange(self.length-1,-1,-1):
            yield self._data[i]

            
    def push_back(self, val):
        self.append(val)
        
    def pop_back(self):
        self.length -=1

    def size(self):
        return self.length

    def capacity(self):
        return self.size

    def reserve(self, size):
        self.size = size
        self._data = np.resize(self._data, self.size)


    @property
    def data(self):
        return self._data[:self.length]    
