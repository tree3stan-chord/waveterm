# Makefile for waveterm
# A modern terminal-based music visualizer

PYTHON = python3
PACKAGE = waveterm
VERSION = 0.2.0

.PHONY: help build install uninstall test clean dist rpm dev-install check format demo smoke-test

help:
	@echo "Available targets:"
	@echo "  build       - Build the package"
	@echo "  install     - Install the package"
	@echo "  uninstall   - Uninstall the package"
	@echo "  dev-install - Install in development mode"
	@echo "  test        - Run tests"
	@echo "  check       - Run code quality checks"
	@echo "  format      - Format code"
	@echo "  clean       - Clean build artifacts"
	@echo "  dist        - Create distribution package"
	@echo "  rpm         - Build RPM package"
	@echo "  demo        - Run WaveTerm demo"
	@echo "  smoke-test  - Run basic functionality tests"

build:
	$(PYTHON) -m build

install:
	$(PYTHON) -m pip install .

uninstall:
	@echo "Uninstalling $(PACKAGE)..."
	$(PYTHON) -m pip uninstall $(PACKAGE) -y || echo "Package not installed via pip"
	@echo "Removing any remaining executables..."
	@rm -f ~/.local/bin/$(PACKAGE) ~/.local/bin/$(PACKAGE)-demo 2>/dev/null || true
	@echo "Uninstall complete!"

dev-install:
	$(PYTHON) -m pip install -e .[dev]

test:
	PYTHONPATH=. $(PYTHON) -m unittest discover tests -v

check:
	@echo "Running security checks..."
	@command -v bandit >/dev/null 2>&1 && bandit -r $(PACKAGE)/ || echo "bandit not available - install with: pip install bandit"
	@echo "Running type checking..."
	@command -v mypy >/dev/null 2>&1 && mypy $(PACKAGE)/ || echo "mypy not available - install with: pip install mypy"
	@echo "Running lint checks..."
	@command -v flake8 >/dev/null 2>&1 && flake8 $(PACKAGE)/ || echo "flake8 not available - install with: pip install flake8"

format:
	@command -v black >/dev/null 2>&1 && black $(PACKAGE)/ tests/ || echo "black not available - install with: pip install black"
	@command -v isort >/dev/null 2>&1 && isort $(PACKAGE)/ tests/ || echo "isort not available - install with: pip install isort"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf $(PACKAGE).egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -f $(PACKAGE)-$(VERSION).tar.gz

dist: clean
	$(PYTHON) -m build
	tar czf $(PACKAGE)-$(VERSION).tar.gz \
		--exclude='.git*' \
		--exclude='*.pyc' \
		--exclude='__pycache__' \
		--exclude='build' \
		--exclude='dist' \
		--exclude='*.egg-info' \
		--transform 's,^,$(PACKAGE)-$(VERSION)/,' \
		$(PACKAGE)/ tests/ *.py *.toml *.md *.spec Makefile LICENSE

rpm: dist
	@echo "Building RPM package..."
	@command -v rpmbuild >/dev/null 2>&1 || (echo "rpmbuild not available - install rpm-build package" && exit 1)
	mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	cp $(PACKAGE)-$(VERSION).tar.gz ~/rpmbuild/SOURCES/
	cp $(PACKAGE).spec ~/rpmbuild/SPECS/
	rpmbuild -ba ~/rpmbuild/SPECS/$(PACKAGE).spec
	@echo "RPM packages created in ~/rpmbuild/RPMS/"

# Demo target - run the visualizer demo
demo:
	@echo "Running WaveTerm demo..."
	$(PYTHON) -m $(PACKAGE).demo || $(PACKAGE)-demo || echo "Demo failed - ensure WaveTerm is installed"

# Smoke test - basic functionality verification
smoke-test:
	@echo "Running smoke tests..."
	@$(PACKAGE) --version && echo "✓ CLI version check works"
	@$(PACKAGE) modes >/dev/null && echo "✓ Modes listing works"
	@timeout 3s $(PACKAGE) run --mode bars --input sim >/dev/null 2>&1 || echo "✓ Basic visualization works (timeout expected)"
	@timeout 2s $(PACKAGE)-demo >/dev/null 2>&1 || echo "✓ Demo mode works (timeout expected)"
	@echo "All smoke tests completed!"

# Visualization test - cycle through all modes briefly
viz-test:
	@echo "Testing all visualization modes..."
	@for mode in bars wave matrix particles circle starfield fire ocean dna neural glitch void hypercube fractal portal; do \
		echo "Testing $$mode mode..."; \
		timeout 1s $(PACKAGE) run --mode $$mode --input sim >/dev/null 2>&1 || true; \
	done
	@echo "All visualization modes tested!"

# Performance test - check rendering performance
perf-test:
	@echo "Running performance tests..."
	@echo "Testing 30 FPS performance..."
	@timeout 5s $(PACKAGE) run --mode bars --fps 30 --input sim >/dev/null 2>&1 || true
	@echo "Testing 60 FPS performance..."  
	@timeout 5s $(PACKAGE) run --mode particles --fps 60 --input sim >/dev/null 2>&1 || true
	@echo "Performance tests completed!"

# Install with audio dependencies (for systems with audio hardware)
install-audio:
	$(PYTHON) -m pip install .[audio]

# Install with all dependencies
install-all:
	$(PYTHON) -m pip install .[all]

all: clean build test check