PACKAGE_NAME = OpenHosta
SRC_DIR = src/OpenHosta
TEST_DIR = tests
DOC_DIR = doc

all: help

help:
	@echo Usage:
	@echo 	make help             Show this help message
	@echo  	make package          Package the project for pip installation
	@echo  	make tests            Run the tests
	@echo  	make format           Format the code using black
	@echo  	make lint             Check code quality using flake8
	@echo  	make clean            Clean not necessary files

build:
	python -m build
	python -m twine check dist/*

upload:
	python -m twine upload dist/*

tests:
	pip install . 
	C:\Users\Merlin\AppData\Roaming\Python\Python312\Scripts\pytest.exe .\tests\functionnalTests\test_mandatory.py -v
	pip uninstall -y OpenHosta

format:
	black $(SRC_DIR)

lint:
	flake8 $(SRC_DIR) $(TEST_DIR)

clean:
	rm -rf build dist *.egg-info
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "__hostacache__" -exec rm -rf {} +

fclean: clean
	rm -rf .pytest_cache .mypy_cache

make re:
	pip uninstall -y OpenHosta
	pip install ..

.PHONY: all help build tests format lint clean fclean re
