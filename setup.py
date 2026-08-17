#!/usr/bin/env python


## Copyright (C)  2026   Hawk Berry


from setuptools import find_packages, setup


setup(
    name='finra',
    packages=find_packages(include=['finra']),
    package_dir={'finra': 'finra'},
    )
