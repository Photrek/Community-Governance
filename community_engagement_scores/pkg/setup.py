#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Setup script for configuring, packaging, distributing and installing this Python package.

import re
from codecs import open
from os import path

from setuptools import find_packages, setup


def locate_package_directory():
    """Identify directory of the package and its associated files."""
    try:
        return path.abspath(path.dirname(__file__))
    except Exception:
        message = (
            "The directory in which the package and its "
            "associated files are stored could not be located."
        )
        raise ValueError(message)


def read_file(filepath):
    """Read content from an UTF-8 encoded text file"""
    with open(filepath, "r", encoding="utf-8") as file_handle:
        text = file_handle.read()
    return text


def load_long_description(pkg_dir):
    """Load long description from file README.md"""
    try:
        filepath_readme = path.join(pkg_dir, "README.md")
        return read_file(filepath_readme)
    except Exception:
        message = "Long description could not be read from README.md"
        raise ValueError(message)


def is_canonical(version):
    """Check if a version string is in canonical format of PEP 440."""
    # Source: https://www.python.org/dev/peps/pep-0440
    pattern = (
        r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))"
        r"*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))"
        r"?(\.dev(0|[1-9][0-9]*))?$"
    )
    return re.match(pattern, version) is not None


def load_version(pkg_dir, pkg_name):
    """Load version from variable __version__ in file __init__.py"""
    try:
        # Read file
        filepath_init = path.join(pkg_dir, pkg_name, "__init__.py")
        file_content = read_file(filepath_init)
        # Parse version string with regular expression
        re_for_version = re.compile(r"""__version__\s+=\s+['"](.*)['"]""")
        match = re_for_version.search(file_content)
        version_string = match.group(1)
    except Exception:
        message = (
            "Version could not be read from variable " "__version__ in file __init__.py"
        )
        raise ValueError(message)
    # Check validity
    if not is_canonical(version_string):
        message = (
            'The detected version string "{}" is not in canonical '
            "format as defined in PEP 440.".format(version_string)
        )
        raise ValueError(message)
    return version_string


PKG_NAME = "ces"
PKG_DIR = locate_package_directory()

setup(
    # Basic package information
    name=PKG_NAME,
    version=load_version(PKG_DIR, PKG_NAME),
    description=("Community Engagement Scores (CES)"),
    long_description=load_long_description(PKG_DIR),
    # Classifiers: available ones listed at https://pypi.org/classifiers
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    # Included files
    # a) auto-detected Python packages
    packages=find_packages(),
    # b) data files that are specified in the MANIFEST.in file
    include_package_data=True,
    # Dependencies that need to be fulfilled
    python_requires=">=3.11",
    setup_requires=[
        "setuptools>=40",
    ],
    # Dependencies that are downloaded by pip on installation
    install_requires=[
        "setuptools>=40",
        "gravis>=0.1",
        "matplotlib>=3",
        "networkx>=3",
        "numpy>=1.25",
        "pandas>=2",
        "pyexcelerate>=0.10",
    ],
    # Capability of running in compressed form
    zip_safe=False,
)
