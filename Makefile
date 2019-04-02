venv: requirements.txt
	@python3 -m venv $@
	@source $@/bin/activate && pip install -r $<

.PHONY: lint
lint:
	@pylint -f colorized app/

.PHONY: typecheck
typecheck:
	@mypy app/
