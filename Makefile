export PIP_CACHE_DIR=/tmp/pip_cache

PYTHON = python3.10

install:
	$(PYTHON) -m pip install flake8 mypy pygame
	$(PYTHON) -m pip install assets/resources/mazegenerator-00001-py3-none-any.whl

run:
	$(PYTHON) pac-man.py config.json
	
clean:
	$(PYTHON) -m pip uninstall mazegenerator
	rm -rf .mypy_cache src/__pycache__ $(PIP_CACHE_DIR)

debug:
	$(PYTHON) -m pdb pac-man.py config.json

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
