.PHONY: all test analytical montecarlo figures
all: test analytical montecarlo figures
test:
	python -m pytest -q tests
analytical:
	python scripts/run_analytical.py
montecarlo:
	python scripts/run_montecarlo.py
figures:
	python scripts/make_figures.py
