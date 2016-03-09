requirements:
	pip freeze | grep -v "^-e" > requirements-dev.txt
	grep -Ev "^(nose=|scripttest=|selenium=)" requirements-dev.txt > requirements.txt
test:
	nosetests
