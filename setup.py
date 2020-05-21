from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='dl-cloud',
      version='0.1.14',
      description='Cloud resource management for deep learning applications.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/for-ai/cloud',
      author='FOR.ai',
      author_email='team@for.ai',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
      ],
      keywords='deep learning cloud',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      install_requires=['numpy', 'apache-libcloud', 'toml', "errand-boy", "filelock", "pathlib"])
