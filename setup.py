from setuptools import setup,find_packages
import glob

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

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='dicom_tools',
      version='2.2',
      description='Package for DICOM medical images analysis.',
      url='http://www.roma1.infn.it/~mancinit/Software/dicom_tools',
      download_url = 'https://github.com/carlomt/dicom_tools/archive/1.0.tar.gz',
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
