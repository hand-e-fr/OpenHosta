PACKAGE_NAME = OpenHosta
SRC_DIR = src
TEST_DIR = tests
DOC_DIR = Documentation

all: help

help:
	@echo Usage:
	@echo 	make help             Show this help message
	@echo  	make package          Package the project for pip installation
	@echo  	make test             Run the tests
	@echo  	make format           Format the code using black
	@echo  	make lint             Check code quality using flake8

package:
	python setup.py sdist bdist_wheel

test_light:
	python -m unittest discover $(TEST_DIR)

test_medium:
	python -m unittest discover $(TEST_DIR)

test_complete:
	python -m unittest discover $(TEST_DIR)


format:
	black $(SRC_DIR) $(TEST_DIR)

lint:
	flake8 $(SRC_DIR) $(TEST_DIR)

clean:
	rm -rf build dist *.egg-info
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name ".openhosta" -exec rm -rf {} +

fclean: clean
	rm -rf .pytest_cache .mypy_cache

.PHONY: all help package test format lint clean fclean
