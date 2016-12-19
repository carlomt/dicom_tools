from dicom_tools.pyqtgraph.Qt import QtCore, QtGui
# from dicom_tools.MyLightWidget import MyLightWidget

        
class MyStatusBar(QtGui.QWidget):

    # def __init__(self, parent=None):
    def __init__(self):        
        # super(MyStatusBar,self).__init__(self, parent)
        # QtGui.QWidget .__init__(parent)
        QtGui.QWidget.__init__(self)                
        self.layout = QtGui.QHBoxLayout(self)
        self.lights = []
        # self.setSize(size)
        
    def setSize(self, size):
        for i in xrange(0,size):
            # thisLight = MyLightWidget()
            thisLight = QtGui.QPushButton()
            thisLight.setStyleSheet("background-color: red")
            thisLight.setFixedSize(3,3)
            # thisLight.setGeometry(QtCore.QRect(1, 1, 0, 0))
            self.lights.append(thisLight)
            self.layout.addWidget(thisLight)


    def setOn(self, i):
        self.lights[i].setOn()

    def setOff(self, i):
        self.lights[i].setOff()                      
        
