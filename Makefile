.PHONY: create-venv clean-venv test-with-venv first-release release lint

VENV_ACTIVATE_PATH=venv/bin/activate
SRC_FOLDER=src/

# Init new virtual environment
create-venv:
	virtualenv venv --python=python3

# Remove existing virtual environment
clean-venv:
	rm -rf venv

# Test in virtual environment
test-with-venv:
	( \
		. ${VENV_ACTIVATE_PATH}; \
    pip install -r requirements.txt; \
    python ${SRC_FOLDER}/main.py \
  )

# Run pylint checking
lint:
	( \
		. ${VENV_ACTIVATE_PATH}; \
    pip install -r requirements.txt; \
    pylint ${SRC_FOLDER} \
  )

# Create the first release
first-release:
	npx standard-version --first-release

# Create a new release
release:
	npx standard-version
