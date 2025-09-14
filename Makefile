.PHONY: all clean install check-uv venv

UV ?= uv
VENV_PY = .venv/bin/python
PYINSTALLER = .venv/bin/pyinstaller
SCRIPT = ai.py
EXECUTABLE = ai
DIST_DIR = dist
BUILD_DIR = build
SPEC_FILE = $(EXECUTABLE).spec
INSTALL_PATH = /usr/local/bin/$(EXECUTABLE)

check-uv:
	@command -v $(UV) >/dev/null 2>&1 || { echo >&2 "Error: 'uv' is not installed. Please install 'uv' to continue."; exit 1; }

venv: check-uv
	$(UV) sync

all: venv $(DIST_DIR)/$(EXECUTABLE)

$(DIST_DIR)/$(EXECUTABLE): $(SCRIPT)
	$(VENV_PY) -m pyinstaller --onefile --name $(EXECUTABLE) $(SCRIPT)

install: all
	@if [ -e $(INSTALL_PATH) ] || [ -L $(INSTALL_PATH) ]; then \
		rm -f $(INSTALL_PATH); \
	fi
	ln -sf $(PWD)/$(DIST_DIR)/$(EXECUTABLE) $(INSTALL_PATH)
	@echo "Installed $(EXECUTABLE) to $(INSTALL_PATH)"

clean:
	rm -rf $(DIST_DIR) $(BUILD_DIR) $(SPEC_FILE) __pycache__
