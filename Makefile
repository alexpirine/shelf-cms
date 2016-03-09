VERSION :=$(shell python setup.py --version )

all:
	python setup.py build
clean:
	python setup.py clean
	rm -fr build
	rm -fr dist
	rm -fr ShelfCMS.egg-info/
develop:
	python setup.py develop
sdist:
	python setup.py sdist --formats=gztar,zip
pypi: sdist
	sh -c 'read -s -p "Enter GPG passphrase: " pwd && echo && echo $$pwd > .gpg.passphrase.tmp'
	gpg --detach-sign --batch --yes --armor --passphrase-file .gpg.passphrase.tmp dist/ShelfCMS-${VERSION}.tar.gz
	gpg --detach-sign --batch --yes --armor --passphrase-file .gpg.passphrase.tmp dist/ShelfCMS-${VERSION}.zip
	rm .gpg.passphrase.tmp
	twine upload dist/ShelfCMS-${VERSION}*
requirements:
	pip freeze | grep -v "^-e" > requirements-dev.txt
	grep -Ev "^(nose=|scripttest=|selenium=)" requirements-dev.txt > requirements.txt
test:
	nosetests
