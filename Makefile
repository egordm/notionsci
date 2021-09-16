.PHONY: test clean

test: lint-check
	pipenv run test

lint-check:
	pipenv run black --check **/*.py

lint:
	pipenv run black **/*.py

setup:
	pip install -U pip setuptools==57.1.0
	pip install pipenv
	pipenv install --three --dev

setup-ci:
	pip install pipenv
	pipenv install --dev --deploy

clean:
	rm -rf dist build requirements.txt requirements-dev.txt notionsci.egg-info

#---- Packaging ----

package: requirements.txt **/*.py
	pipenv run python setup.py bdist_wheel

requirements.txt: Pipfile Pipfile.lock
	pipenv run pipenv_to_requirements

#---- Publishing ----

check-package: package
	pipenv run twine check dist/*

publish-test: check-package
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish-prod: check-package
	pipenv run twine upload dist/*
