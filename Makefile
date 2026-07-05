install:
	pip install flake8 mypy pygame
	pip install assets/resources/mazegenerator-00001-py3-none-any.whl

run:
	python3 pac-man.py config.json
	
clean:
	rm -rf .mypy_cache src/__pycache__
	pip uninstall mazegenerator

debug:
	python3 -m pdb pac-man.py config.json

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
