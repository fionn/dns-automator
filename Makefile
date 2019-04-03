VIRTUAL_ENV ?= venv
SRC = app/

venv: requirements.txt requirements_dev.txt
	@python3 -m venv $@
	@source $@/bin/activate && pip install -r $< -r requirements_dev.txt

tags: $(SRC)
	@ctags --languages=python --python-kinds=-i -R $(SRC)

.PHONY: outdated
outdated:
	@(source $(VIRTUAL_ENV)/bin/activate && pip list --outdated)

.PHONY: lint
lint:
	@pylint -f colorized $(SRC)

.PHONY: typecheck
typecheck:
	@mypy $(SRC)
