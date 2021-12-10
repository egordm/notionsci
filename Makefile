.PHONY: test clean

test: lint-check
	python -m unittest discover -s test -p "Test*.py"

lint-check:
	black --check **/*.py

lint:
	black **/*.py

setup:
	pip install -r requirements.txt

setup-ci: setup
	pip install -r requirements-dev.txt

clean:
	rm -rf dist build notionsci.egg-info

config:
	python -m notionsci config -f config.yml

#---- Packaging ----

package: **/*.py
	python setup.py bdist_wheel

#---- Publishing ----

check-package: package
	twine check dist/*

publish-test: check-package
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish-prod: check-package
	twine upload dist/*
