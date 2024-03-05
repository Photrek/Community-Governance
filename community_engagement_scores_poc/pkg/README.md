# Python package for CES

This folder contains a Python package for calculating Community Engagement Scores (CES) for Deep Funding. It requires a data export from Swae as input and can generate output in form of a SQLite database, an Excel file or a folder with CSV files.


## Installation

1. Install [Python 3.11 or later](https://docs.python.org/3/using/index.html)
2. Install the package with Python's default package manager [pip](https://pip.pypa.io)
    1. Optional: To keep different installations isolated on your system, you may want to first activate a [virtual environment](https://docs.python.org/3/tutorial/venv.html) with an environment management program like [venv](https://docs.python.org/3/library/venv.html) or [conda](https://conda.io).
    2. Optional: `pip install -r requirements.txt` (or `pip install -r requirements-dev.txt` to include development tools)
        - This installes each dependency in the exact same version as was used during the development of the package. This ensures maximum compatibility, but should not be necessary.
    3. Required: `pip install .`
        - This installs the package on your system. It will also install the latest version of every dependency that is not yet present in the current environment. 


## Usage

1. Start a Python interpreter: `python3`
2. Import the package: `import ces` (or directly import the subpackage for analyzing Swae data: `from ces import swae_analysis as swa`)
3. Use the functions provided in the package as shown in the [examples](examples). If you need more detailed information, each function in this package comes with a [docstring](https://peps.python.org/pep-0257) that can be accessed with Python's [built-in help system](https://docs.python.org/3/library/functions.html#help), e.g. with `help(ces)` or `help(swa.zip_to_sqlite)`. Docstrings can also be read directly in the code, e.g. the function [extract_swae_data(zip_filepath)](https://github.com/robert-haas/ces_test/blob/main/community_engagement_scores/pkg/ces/swae_analysis/extract.py) contains a docstring in its definition.


## Development notes

This package adheres to recommendations by the [Python Packaging Authority (PyPA)](https://www.pypa.io) that can be found in the [Python Packaging User Guide](https://packaging.python.org). The file [setup.py](setup.py) contains the main build specification for [setuptools](https://setuptools.pypa.io), which in turn enables the installation of the package with [pip](https://pip.pypa.io).
