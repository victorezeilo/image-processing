PY ?= python3
MODULE ?= src.image_processing

SRC ?= test.jpg
DST ?= out.png
FMT ?= png
COMP ?= 3

WIDTH ?= 800
HEIGHT ?= 600

.PHONY: help convert resize test install clean


convert:
	$(PY) -m $(MODULE) convert --source "$(SRC)" --destination "$(DST)" --format "$(FMT)" --compression "$(COMP)"

resize:
	$(PY) -m $(MODULE) resize --source "$(SRC)" --width "$(WIDTH)" --height "$(HEIGHT)"

test:
	$(PY) -m pytest -q

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
