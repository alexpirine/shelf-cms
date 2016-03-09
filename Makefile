VERSION := $(shell python setup.py --version)
DEV_TOOLS := (nose|scripttest|selenium)
all:
	python setup.py build
install:
	pip install .
clean:
	pip freeze | grep -v "^-e" | xargs pip uninstall -y
	python setup.py clean
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr ShelfCMS.egg-info/
develop:
	pip install -e .[dev]
sdist:
	python setup.py sdist --formats=gztar,zip
pypi: sdist
	sh -c 'read -s -p "Enter GPG passphrase: " pwd && echo && echo $$pwd > .gpg.passphrase.tmp'
	gpg --detach-sign --batch --yes --armor --passphrase-file .gpg.passphrase.tmp dist/ShelfCMS-${VERSION}.tar.gz
	gpg --detach-sign --batch --yes --armor --passphrase-file .gpg.passphrase.tmp dist/ShelfCMS-${VERSION}.zip
	rm .gpg.passphrase.tmp
	twine upload dist/ShelfCMS-${VERSION}*
requirements:
	pip freeze | grep -E "^${DEV_TOOLS}=" > requirements-dev.txt
	pip freeze | grep -vE "^(-e |${DEV_TOOLS}=)" > requirements.txt
test:
	python setup.py test
