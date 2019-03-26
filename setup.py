#!/usr/bin/env python2

from setuptools import setup, find_packages

setup(
    zip_safe=True,
    name='indy_blacklist_verify',
    version="0.1",
    license='APLv2',
    packages = find_packages(),
    install_requires=[
        'requests',
        'ruamel.yaml'
    ],
)

