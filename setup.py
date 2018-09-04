from setuptools import setup,find_packages
import os, glob, re

packs=find_packages()
scripts_list=glob.glob('./bin/*.py')
install_req=[
    'scipy>=0.17.1',
    'numpy>=1.10.0',    
    'pydicom>=0.9.9',
    'pynrrd>=0.2.1',
    'scikit-image>=0.12.3',
    'scikit-learn>=0.18',
    'nose>=1.3.7',
    'SimpleITK>=0.10.0',
    'tabulate>=0.7.7',
    'openpyxl>=2.4.0',
    'ipython<6',
    'qtconsole'
]

# with open("README.md", "r") as fh:
#     long_description = fh.read()

PKG = "dicom_tools"
VERSIONFILE = os.path.join(PKG, "__init__.py")
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))
    

setup(name=PKG,
      version=verstr,
      description='Package for DICOM medical images analysis.',
      long_description="dicom_tools is a library with a Graphical User Interface (GUI), dicom_tool.py, to analyze medical images. It is possible to apply filters, perform automatic segmentation and compute several texture parameters, of both the first and second order. All the functions are available via the GUI, developed with the Qt libraries and compatible with Qt4 and Qt5. The GUI shows to the user the medical image once imported as a numpy array tensor with 3 indices. The lightness of the GUI allows an agile use of the software remotely, via an SSH connection. It is also possible to open an interactive python shell that have access to all the memory of the GUI instance and the functions of the package and can interact with the GUI. The package is interfaced with the most powerful libraries for images and medical images analysis, ensuring the opportune conversions of data types.",
      url='http://www.roma1.infn.it/~mancinit/Software/dicom_tools',
      download_url = 'https://github.com/carlomt/dicom_tools/archive/'+verstr+'.tar.gz',
      author='Carlo Mancini Terracciano',
      author_email='carlo.mancini.terracciano@roma1.infn.it',
      license='MIT',
      scripts=scripts_list,
      install_requires=install_req,
      packages=packs,
      keywords = ['medical','image-analysis'],
      classifiers = ["Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
)
