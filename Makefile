.PHONY: install run dryrun csv format

install:
	pip install -r requirements.txt

run:
	python boat_scraper.py

dryrun:
	python boat_scraper.py --dryrun

csv:
	python boat_scraper.py --csv

format:
	black boat_scraper.py
	isort boat_scraper.py
