# Makefile to automate recurring tasks in app development


.DEFAULT: help
.PHONY: help
help:
	@echo "--------------------------------------------------------------------------------------------"
	@echo
	@echo "How to use this Makefile with a \"Make tool\" like GNU Make"
	@echo
	@echo "  Help"
	@echo "    make help          show this help message"
	@echo
	@echo "  Usage"
	@echo "    make run           launch a Python shell and import the installed package"
	@echo
	@echo "  Development"
	@echo "    make clean         delete everything that can be generated"
	@echo "    make style-black   style formatting with black (modify code, ensure consistent style)"
	@echo "    make style-isort   style check with isort (check import order)"
	@echo "    make style-flake8  style check with flake8 (check basic code conventions, detect bugs)"
	@echo "    make style-pydoc   style check with pydocstyle (check docstring conventions)"
	@echo "    make todo          check for TODO comments in source code with pylint"
	@echo
	@echo "--------------------------------------------------------------------------------------------"


# Usage

.PHONY: run
run:
	python manage.py migrate
	DEBUG=True python manage.py runserver


# Development

.PHONY: clean
clean:
	# Directories
	-@rm -rf swae_temp_dir
	-@find . -type d \
	    \( \
	    -name "__pycache__" \
	    -or -name "*.egg-info" \
	    -or -name ".cache" \
	    -or -name ".pytest_cache" \
	    -or -name ".ipynb_checkpoints" \
	    \) \
	    -exec rm -rf {} \; 2> /dev/null || true
	# Files
	-@find . \( -name '*.pyc' -or -name '*.pyd' -or -name '*.pyo' -or -name '*~' \) \
	    -exec rm --force {} + 2> /dev/null || true
	@echo "Deleted all unnecessary files and directories."

.PHONY: style-black
style-black:
	black .

.PHONY: style-isort
style-isort:
	@isort --diff .

.PHONY: style-flake8
style-flake8:
	flake8 .

.PHONY: style-pydoc
style-pydoc:
	pydocstyle --convention=numpy .

.PHONY: todo
todo:
	pylint . --disable=all --enable=W0511
