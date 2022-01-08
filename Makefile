.PHONY: all venv pep run clean

APP=app.py
VENV_NAME?=.venv
PYTHON=$(VENV_NAME)/bin/python3

all:run

run:pep clean
	${PYTHON} $(APP)

venv:
	@if [ -e $(VENV_NAME)/bin/activate ]; then rm -r $(VENV_NAME); fi
	if [ ! -e $(VENV_NAME)/bin/activate ]; then python3 -m venv ${VENV_NAME}; fi
	${PYTHON} -m pip install -r requirements.txt
	${PYTHON} -m pip freeze > requirements.txt

append:
	if [ ! -e $(VENV_NAME)/bin/activate ]; then python3 -m venv ${VENV_NAME}; fi
	${PYTHON} -m pip install -r requirements.txt
	${PYTHON} -m pip freeze > requirements.txt

pep:
	find . -maxdepth 2 -type f -name "*.py" -exec ${PYTHON} -m autopep8 --in-place --aggressive {} \;

clean:pep
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -type d | xargs rm -fr
	@echo "cache clear"

install:
	sudo apt-get install python3-venv -y
	pip3 install autopep8 virtualenv
