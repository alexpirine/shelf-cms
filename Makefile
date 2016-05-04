NAME := $(shell python setup.py --name)
NAME_NORMALIZED := $(shell echo ${NAME} | sed s/-/_/)
VERSION := $(shell python setup.py --version)
DEV_TOOLS := ($(shell python -c 'import setup; print "|".join(setup.DEV_TOOLS)'))
IS_INSTALLED := $(shell if [[ `pip show ${NAME}` != "" ]]; then echo yes; else echo no; fi)

help:
	@echo "${NAME}-${VERSION} (currently installed: ${IS_INSTALLED})"
	@echo "make install       - Install on local system"
	@echo "make develop       - Install on local system in development mode"
	@echo "make sdist         - Create python source packages"
	@echo "make pypi          - Update PyPI package"
	@echo "make requirements  - Update requirements files"
	@echo "make test          - Run tests"
	@echo "make clean         - Get rid of scratch and byte files"
	@echo "make uninstall     - Uninstall from local system"

install:
	pip install .

develop:
	pip install -e .[dev]

sdist:
	python setup.py sdist --formats=gztar,zip

wheel:
	python setup.py bdist_wheel

dist: sdist wheel

sign_wheel:
	wheel sign dist/${NAME_NORMALIZED}-${VERSION}-*.whl

sign:
	wheel verify dist/${NAME_NORMALIZED}-${VERSION}-*.whl
	sh -c 'read -s -p "Enter GPG passphrase: " pwd && \
	gpg --detach-sign --batch --yes --armor --passphrase $$pwd dist/${NAME}-${VERSION}.tar.gz && \
	gpg --detach-sign --batch --yes --armor --passphrase $$pwd dist/${NAME}-${VERSION}.zip && \
	gpg --detach-sign --batch --yes --armor --passphrase $$pwd dist/${NAME_NORMALIZED}-${VERSION}-*.whl'
	@echo

pypi: dist sign
	twine upload dist/{${NAME},${NAME_NORMALIZED}}-${VERSION}*

requirements_std: install
	pip freeze | grep -vE "^${NAME}=" > requirements.txt

requirements_dev: develop
	pip freeze | grep -vE "^-e " > requirements-dev.txt

requirements: uninstall requirements_std requirements_dev

test: develop
	coverage erase
	coverage run --source=shelf -p --concurrency=multiprocessing setup.py test
	coverage combine

uninstall:
ifeq ($(IS_INSTALLED),yes)
	pip uninstall -y ${NAME}
endif
	pip freeze | grep -vE "^-e " | xargs pip uninstall -y

clean:
	python setup.py clean
	rm -fr build/ dist/ .eggs/
	rm -fr *.egg-info/
	find . -name '*.py[co]' -delete
