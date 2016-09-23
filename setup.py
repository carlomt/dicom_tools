from setuptools import setup,find_packages
import glob

packs=find_packages()
scripts_list=glob.glob('./bin/*.py')
install_req=[
    'pydicom>=0.9.9',
    'numpy>=1.10.0',
    'scipy>=0.17.1'
]

setup(name='dicom_tools',
      version='0.1',
      description='',
      url='https://github.com/carlomt/dicom_tools',
      author='Carlo Mancini Terracciano',
      author_email='carlo.mancini.terracciano@roma1.infn.it',
      license='MIT',
      scripts=scripts_list,
      install_requires=install_req,
      packages=packs)
