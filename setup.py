# -*- coding:utf-8 -*-
"""
setup.py (ucanSystec)
Author: SMFSW

SystecUSBCAN setup file
"""

__version__ = "0.2.2"

# from distutils.core import setup
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='ucanSystec',
    packages=find_packages(exclude=['build', 'contrib', 'doc', 'docs', 'tests']),
    version=__version__,
    url='https://github.com/SMFSW/python-ucanSystec',
    license='MIT',
    author='SMFSW',
    author_email='xgarmanboziax@gmail.com',
    description='Systec usb/can dll bindings',
    keywords=['Communication', 'CAN', 'Systec', 'DLL'],
    long_description=open('README.md').read(),
    classifiers=[
            'License :: OSI Approved :: MIT License',

            'Development Status :: 5 - Production/Stable',

            'Intended Audience :: Developers',
            'Topic :: Utilities',

            'Natural Language :: English',

            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
    ],
)
