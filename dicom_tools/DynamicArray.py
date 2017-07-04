from __future__ import print_function
import numpy as np
from dicom_tools.convertTypes import convertTypes
from dicom_tools.convertTypes import convertTypesROOT

class DynamicArray(object):
    def __init__(self, dtype, size=10, stride=10):
        self.dtype = np.dtype(dtype)
        self.length = 0
        self.size = size
        self.STRIDE = stride
        self._data = np.empty(self.size, dtype=self.dtype)

    def __len__(self):
        return self.length

    def append(self, val):
        if self.length == self.size:
            self.size += self.STRIDE
            self._data = np.resize(self._data, self.size)
        self._data[self.length] = val
        self.length +=1

    def __getitem__(self,key):
        if isinstance(key,int):
            i = key
            if i<0:
                i = self.length + i 
            if i<self.length and i>=0:
                return self._data[i]
            else:
                raise IndexError('index',key,' is out of bounds. Size:',self.length)
        else:
            return self._data[key][0:self.length]
            
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

    def savetxt(self, filename, delimiter=' ', header='',comments='#'):
        types = self.getTypes()
        sformat = ""
        for this_type in types:
            sformat+= convertTypes(this_type)+" "
        np.savetxt(filename, self._data[:self.length], sformat, delimiter=delimiter, header=header, comments=comments)

    def savetxtROOT(self, filename):
        # types = self.getTypes()
        # sformat = ""
        branchDescriptor = ""
        for var in self._data.dtype.names:
            this_type = type(self._data[var][0])
            # sformat+= convertTypes(this_type)+" "
            branchDescriptor += var+"/"+convertTypesROOT(this_type)+":"
        # np.savetxt(filename, self._data[:self.length], sformat, header=branchDescriptor[:-1], comments='')
        self.savetxt(filename, header=branchDescriptor[:-1], comments='')        

    def savecsv(self, filename, delimiter=', '):
        varnames = ""
        for var in self._data.dtype.names:
            varnames += var+delimiter
        self.savetxt(filename, header=varnames, delimiter=delimiter, comments='')
        

    def getTypes(self):
        res = []
        for var in self._data.dtype.names:
            res.append(type(self._data[var][0]))
        return res
        
    @property
    def data(self):
        return self._data[:self.length]    
