requirements:
	pip freeze | grep -v "^-e" > requirements-dev.txt
	grep -Ev "^(nose==|scripttest==)" requirements-dev.txt > requirements.txt
test:
	nosetests
