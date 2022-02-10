.PHONY: install test

install:
	python3 -m pip install -r requirements.txt

test:
	python3 ./check404.py


