setup:
	pip install -r requirements_dev.txt

test:
	python -m unittest discover

build-dist:
	python setup.py sdist

upload-pypi: build-dist
	twine upload --skip-existing dist/*

upload-pypitest: build-dist
	twine upload --skip-existing --repository-url https://test.pypi.org/legacy/ dist/*
