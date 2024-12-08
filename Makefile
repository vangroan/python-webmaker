SHELL := /bin/bash
SOURCE_FILES := src/ tests/

.PHONY: fmt
fmt:
	@echo "Formatting"
	@isort $(SOURCE_FILES)
	@for d in $(SOURCE_FILES); do \
		black $$d ; \
	done
	@ruff check --fix $(SOURCE_FILES) 
	@echo "Done"

.PHONY: lint
lint:
	@echo "Linting"
	@ruff check $(SOURCE_FILES)
	@mypy $(SOURCE_FILES)
	@echo "Done"
