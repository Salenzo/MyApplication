.PHONY: all venv pep run clean

APP=app.py
VENV_NAME?=.venv
REQUIREMENTS=autopep8
PYTHON=$(VENV_NAME)/bin/python3

all:run

venv:
	if [ ! -e $(VENV_NAME)/bin/activate ]; then python3 -m venv ${VENV_NAME}; fi
	${PYTHON} -m pip install $(REQUIREMENTS) $(APPEND)
	${PYTHON} -m pip freeze > requirements.txt

pep:
	find . -maxdepth 2 -type f -name "*.py" -exec ${PYTHON} -m autopep8 --in-place --aggressive {} \;

run:pep clean
	${PYTHON} $(APP)

clean:pep
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -type d | xargs rm -fr
	@echo "cache clear"
