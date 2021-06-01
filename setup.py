#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import io
import os


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

extras = {}
with open("requirements-dev.txt") as f:
    extras["dev"] = f.read().splitlines()

version = {}  # type: dict
with io.open(os.path.join("scanflow", "_version.py")) as fp:
    exec(fp.read(), version)


setup(
    name = "scanflow",
    description="An MLOps Platform",
    keywords='scanflow, kubernetes, mlflow, argo, seldon',

    author="BSC Scanflow Team",
    author_email='peini.liu@bsc.es',
    license="MIT license",

    version=version["__version__"],
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras,
    python_requires=">=3.6",
    packages=find_packages(exclude=["*test*"]),
    package_data={"": ["requirements.txt"]},
)
