VERSION := $(shell python setup.py --version)
DEV_TOOLS := ($(shell python -c 'import setup; print "|".join(setup.DEV_TOOLS)'))

help:
	@echo "make install       - Install on local system"
	@echo "make develop       - Install on local system in development mode"
	@echo "make sdist         - Create python source packages"
	@echo "make pypi          - Update PyPI package"
	@echo "make requirements  - Update requirements files"
	@echo "make test          - Run tests"
	@echo "make clean         - Get rid of scratch and byte files"

install:
	pip install .

develop:
	pip install -e .[dev]

sdist:
	python setup.py sdist --formats=gztar,zip

pypi: sdist
	sh -c 'read -s -p "Enter GPG passphrase: " pwd && \
	gpg --detach-sign --batch --yes --armor --passphrase $$pwd dist/ShelfCMS-${VERSION}.tar.gz && \
	gpg --detach-sign --batch --yes --armor --passphrase $$pwd dist/ShelfCMS-${VERSION}.zip'
	twine upload dist/ShelfCMS-${VERSION}*

requirements: develop
	pip freeze | grep -E "^${DEV_TOOLS}=" > requirements-dev.txt
	pip freeze | grep -vE "^(-e |${DEV_TOOLS}=)" > requirements.txt

test: develop
	coverage run setup.py test

uninstall:
	pip uninstall -y ShelfCMS
	pip freeze | grep -v "^-e" | xargs pip uninstall -y

clean:
	python setup.py clean
	rm -fr build/ dist/ .eggs/
	rm -fr ShelfCMS.egg-info/
	find . -name '*.pyc' -delete
