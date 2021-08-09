test: lint-check
	pipenv run test

lint-check:
	pipenv run black --check **/*.py

lint:
	pipenv run black **/*.py

setup:
	pip install pipenv
	pipenv install --dev --three

clean:
	rm -rf dist build requirements.txt requirements-dev.txt notionsci.egg-info AUTHORS ChangeLog

#---- Packaging ----

package: requirements.txt clean **/*.py
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

publish-travis: check-package
	pipenv run twine upload dist/* -u $$PYPI_USERNAME -p $$PYPI_PASSWORD
