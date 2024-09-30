PACKAGE_NAME := OpenHosta
SRC_DIR := src/OpenHosta
TEST_DIR := tests
DOC_DIR := doc
API_KEY =
TAG := "-==[OpenHosta]==- \>\>\>"

ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    NULL_DEVICE := NUL
    PYTHON := python
    PIP := pip
    L_SHELL := powershell -Command
    PYTEST := & C:\\Users\\Merlin\\AppData\\Roaming\\Python\\Python312\\Scripts\\pytest.exe
    ENV := $$env:
    WRITE := "Write-Host
	COLOR := -ForegroundColor DarkMagenta"
	FIND := "Get-ChildItem -Path . -Recurse -Directory -Filter
	RM := Remove-Item -Recurse -Force"
	CLEAR := "clear"
	CLEAR_DATA = type NUL > $(REDIRECT)
	MKDIR := New-Item -ItemType Directory -Force -Path 
else
    DETECTED_OS := Linux
    NULL_DEVICE := /dev/null
    PYTHON := python3
    PIP := pip3
    L_SHELL :=
    PYTEST := pytest
    ENV := export
    WRITE := echo
	COLOR :=
	FIND := find
	RM := rm -rf
	CLEAR := clear
	CLEAR_DATA = > $(REDIRECT)
	MKDIR := mkdir
endif

all: help

help:
	@echo Usage:
	@echo 	make help             Show this help message
	@echo  	make package          Package the project for pip installation
	@echo  	make *tests            Run the tests
	@echo  	make format           Format the code using black
	@echo  	make lint             Check code quality using flake8
	@echo  	make clean            Clean not necessary files

install: all
	@$(L_SHELL) $(WRITE) '$(TAG) [INSTALL]' $(COLOR)
	@$(L_SHELL) $(WRITE) '$(TAG) Installing dependencies...' $(COLOR)
	@$(PIP) install requirements.txt > $(NULL_DEVICE)
	@$(PIP) install requirements-dev.txt > $(NULL_DEVICE)
	@$(L_SHELL) $(WRITE) '$(TAG) Installing package: $(PACKAGE_NAME)...' $(COLOR)
	@$(PIP) install . > $(NULL_DEVICE)
	@$(L_SHELL) $(WRITE) '$(TAG) Succesfully installed $(PACKAGE_NAME) !' $(COLOR)

build: clean
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*

upload: build
	$(PYTHON) -m twine upload dist/* --verbose

ftests: clean
	@$(L_SHELL) $(WRITE) '$(TAG) Installing package: $(PACKAGE_NAME)...' $(COLOR) 
	@$(PIP) install . > $(NULL_DEVICE)
	@$(L_SHELL) $(WRITE) '$(TAG) Running functionnal tests...' $(COLOR) 
	@$(L_SHELL) $(SET_ENV)
	@-$(L_SHELL) "$(PYTEST) .\\tests\\functionnalTests\\test_mandatory.py $(ARGS)"
	@$(L_SHELL) $(UNSET_ENV)
	@$(L_SHELL) $(WRITE) '$(TAG) Uninstalling package: $(PACKAGE_NAME)...' $(COLOR) 
	@$(PIP) uninstall -y OpenHosta > $(NULL_DEVICE)
	@$(L_SHELL) $(WRITE) '$(TAG) Succesfully ran functionnal tests !' $(COLOR)

utests: clean
	@$(L_SHELL) $(WRITE) '$(TAG) Installing package: $(PACKAGE_NAME)...' $(COLOR) 
	@$(PIP) install . > $(NULL_DEVICE)
	@$(L_SHELL) $(WRITE) '$(TAG) Running unit tests...' $(COLOR) 
	@$(L_SHELL) $(SET_ENV)
	@-$(L_SHELL) "$(PYTEST) .\\tests\\unitTests\\test_exec.py $(ARGS)"
	@$(L_SHELL) $(UNSET_ENV)
	@$(L_SHELL) $(WRITE) '$(TAG) Uninstalling package: $(PACKAGE_NAME)...' $(COLOR) 
	@$(PIP) uninstall -y OpenHosta > $(NULL_DEVICE)
	@$(L_SHELL) $(WRITE) '$(TAG) Succesfully ran unit tests !' $(COLOR)


clean:
	@$(L_SHELL) $(WRITE) '$(TAG) [CLEAN]' $(COLOR)
	@$(L_SHELL) $(WRITE) '$(TAG) Cleaning repository...' $(COLOR)
	@$(L_SHELL) $(FIND) '__pycache__' | $(RM)
	@$(L_SHELL) $(FIND) '__hostacache__' | $(RM)
	@$(L_SHELL) $(FIND) 'build' | $(RM)
	@$(L_SHELL) $(FIND) 'dist' | $(RM)
	@$(L_SHELL) $(FIND) 'OpenHosta.egg-info' | $(RM)
	@$(L_SHELL) $(FIND) '.pytest_cache' | $(RM)
	@$(L_SHELL) $(WRITE) '$(TAG) Uninstalling package: $(PACKAGE_NAME)...' $(COLOR) 
	@$(PIP) uninstall -y OpenHosta > $(NULL_DEVICE)
	@$(L_SHELL) $(CLEAR)
	@$(L_SHELL) $(WRITE) '$(TAG) Succesfully cleaned repository !' $(COLOR)

format: clean
	@black $(SRC_DIR) $(ARGS)

lint: format
	@flake8 $(SRC_DIR) $(ARGS)

re: clean
	@$(L_SHELL) $(WRITE) '$(TAG) Uninstalling package: $(PACKAGE_NAME)...' $(COLOR) 
	@$(PIP) uninstall -y OpenHosta > $(NULL_DEVICE)
	@$(L_SHELL) $(WRITE) '$(TAG) Installing package: $(PACKAGE_NAME)...' $(COLOR) 
	@$(PIP) install . > $(NULL_DEVICE)
	@$(L_SHELL) $(WRITE) '$(TAG) Succesfully updated package !' $(COLOR)

.PHONY: all help build upload ftests utests format lint clean re install
