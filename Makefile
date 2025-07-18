RUN = uv run

all: test
#test: pytest doctest mypy
test: pytest doctest
test-full: test all-nb

CLI = $(RUN) aurelian

ui:
	$(CLI) ui


pytest:
	$(RUN) pytest

mypy:
	$(RUN) mypy src tests

DOCTEST_DIR = src
doctest:
	find $(DOCTEST_DIR) -type f \( -name "*.rst" -o -name "*.md" -o -name "*.py" \) -print0 | xargs -0 $(RUN) python -m doctest --option ELLIPSIS --option NORMALIZE_WHITESPACE

# TODO: have a more elegant way of testing a subset using pytest.mark
pytest-core:
	$(RUN) pytest tests/test_datamodel.py && \
	$(RUN) typedlogic --help

# mdkocs
serve: mkd-serve
mkd-%:
	$(RUN) mkdocs $*

# find all nb files; exclude checkpoint files
NB_FILES = $(shell find docs -type f -name "*.ipynb" -not -path "*/.ipynb_checkpoints/*")
all-nb: $(patsubst docs/%.ipynb,tmp/docs/%.ipynb,$(NB_FILES))

# run notebook with papermill and diff with nbdime
tmp/docs/%.ipynb: docs/%.ipynb
	mkdir -p $(dir $@) && \
	$(RUN) papermill --cwd $(dir $<) $< $@.tmp.ipynb && mv $@.tmp.ipynb $@ && $(RUN) nbdime diff -D -M -A -S $< $@


%-doctest: %
	$(RUN) python -m doctest --option ELLIPSIS --option NORMALIZE_WHITESPACE $<


rpt:
	$(RUN) python src/aurelian/utils/pytest_report_to_markdown.py

chat-%:
	$(RUN) aurelian $*

reports/all.log.jsonl:
	$(RUN) pytest tests/test_agents -k agent --report-log=$@
.PRECIOUS: reports/all.log.jsonl


reports/%.log.jsonl: tests/test_agents/test_%.py
	$(RUN) pytest -s $< --report-log=$@
.PRECIOUS: reports/%.log.jsonl

reports/%.md: reports/%.log.jsonl
	$(RUN) python src/aurelian/utils/pytest_report_to_markdown.py $< > $@.tmp && mv $@.tmp $@

requirements.txt:
	uv export --format requirements.txt --output-file requirements.txt --dev
