#!/usr/bin/env python 

from setuptools import setup, find_packages

setup(name='weasel',
      version='1.0',
      description='Weasel Botnet Engine',
      author='Dan Garant',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['ply', 'psycopg2', 'flask', 'flask-login']
     )
