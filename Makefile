test:
	mypy src
	flake8 src tests
	@cd tests; pytest; rm -rf ./bin ./dll

clean:
	@rm -rf ./*.egg-info ./build ./dist **/__pycache__

