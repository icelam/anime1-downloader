.PHONY: create-venv clean-venv test-with-venv first-release release lint build

VENV_ACTIVATE_PATH=venv/bin/activate
SRC_FOLDER=anime1download

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
		python ${SRC_FOLDER} \
  )

# Run pylint checking
lint:
	( \
		. ${VENV_ACTIVATE_PATH}; \
		pip install -r requirements.txt; \
		pylint ${SRC_FOLDER} \
  )

# Build for distribution
build:
	( \
		rm -rf ./build ./dist ${SRC_FOLDER}.spec; \
		. ${VENV_ACTIVATE_PATH}; \
		pip install -r requirements.txt; \
		pyinstaller --log-level DEBUG --onefile ${SRC_FOLDER}/__main__.py --name ${SRC_FOLDER} \
  )

# Create the first release
first-release:
	npx standard-version --first-release

# Create a new release
release:
	npx standard-version
