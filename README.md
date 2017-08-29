# dicom_tools

PyQt4, sip and SimpleITK have to be installed

on mac you could install them with:

`brew install qt`

`brew install pyqt`

`brew install sip`

`brew install homebrew/science/`

on a debian linux:

`apt-get install python-pip python-qt4  python-sip  python-scipy python-matplotlib`

it could be necessary to upgrade pip before to install the package, as it could not find some dependencies:

`pip install --upgrade pip`

`apt-get install build-essential`


install the package with:

`python setup.py install`

on linux maybe you want to install it only for your user

`python setup.py install --user`
