from setuptools import setup,find_packages
import glob

packs=find_packages()
scripts_list=glob.glob('./bin/*.py')

setup(name='dicom_tools',
      version='0.1',
      description='',
      url=' ',
      author='Carlo Mancini Terracciano',
      author_email='carlo.mancini.terracciano@roma1.infn.it',
      license='MIT',
      scripts=scripts_list,
      packages=packs)
