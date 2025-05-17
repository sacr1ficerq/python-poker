.PHONY: build test test-base install 

build:
	pip install -e . 

install:
	pip install --force-reinstall .

test:
	pytest -svx 

test-all: build
	pytest -svx --log-cli-level=INFO

test-base: build
	pytest -svx tests/test_table.py tests/test_deck.py --log-cli-level=INFO
