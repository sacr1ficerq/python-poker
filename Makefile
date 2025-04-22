.PHONY: build test test-base install 

build:
	pip install -e . 

install:
	pip install --force-reinstall .

test:
	pytest -svx

test-all:
	pip install -e . && pytest -svx

test-base:
	pip install -e . && pytest -svx tests/test_table.py tests/test_deck.py

