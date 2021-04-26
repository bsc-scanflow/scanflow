#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

requirements = ['docker', 'pandas', 'scikit-learn']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Gusseppe Bravo",
    author_email='gusseppebravo@gmail.com',
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords='scanflow',
    name='scanflow',
    packages=find_packages(include=['scanflow']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/gusseppe/scanflow',
    version='0.1.0',
    zip_safe=False,
)
