.PHONY: activate clean clean-test clean-pyc clean-build deactivate docs help
.DEFAULT_GOAL := help
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

activate: ## activate a pyenv virtualenv
	! [ -d "$$HOME/.pyenv/versions/jobcalc" ] && \
		pyenv virtualenv jobcalc && \
		pyenv local jobcalc || \
		pyenv local jobcalc

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

deactivate: ## deactivate the virutal env
	pyenv local --unset

ensure-dev-image:  ## ensure's docker dev image is built
	[ "$$(docker images -q jobcalc:dev)" == "" ] && \
		docker build -t jobcalc:dev \
		--file Dockerfile.dev . || \
	echo "Dev image already exists"

lint: ## check style with flake8
	flake8 jobcalc

ensure-test-image:  ## ensure's docker test image is built
	[ "$$(docker images -q jobcalc:test)" == "" ] && \
		docker build -t jobcalc:test \
		--file Dockerfile.dev . || \
	echo "Test image already exists"

test:   ## activate  ## run tests quickly with the default Python
	py.test -vv --cov-report term-missing --cov jobcalc
	
test-all: clean deactivate ## run tests on every Python version with tox
	tox

run-all-tests: ensure-test-image ## run tox tests in docker container
	docker run -it -v "$$PWD":/usr/src/app --rm jobcalc:test make test-all

run-tests: clean ensure-dev-image ## run tests quickly inside docker container with the default Python
	docker run -it -v "$$PWD":/usr/src/app --rm -e PYENV_VERSION= jobcalc:dev \
		make test

coverage: ## check code coverage quickly with the default Python
	coverage run --source jobcalc py.test
	
		coverage report -m
		coverage html
		$(BROWSER) htmlcov/index.html

docs: install  ## generate Sphinx HTML documentation, including API docs
	rm -f docs/jobcalc.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ jobcalc
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

release: clean ## package and upload a release
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install
