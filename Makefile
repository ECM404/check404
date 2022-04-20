test:
	mypy src
	flake8 src tests
	@cd tests; pytest; rm -rf ./bin ./dll
