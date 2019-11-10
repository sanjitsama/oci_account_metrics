#! /usr/bin/python3
from setuptools import setup
setup(
    name = 'oci_metrics',
    version = '0.1.0',
    packages = ['oci_metrics'],
    entry_points = {
        'console_scripts': [
            'oci_metrics = oci_metrics.__main__:main'
        ]
    })