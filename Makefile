.PHONY: setup server test test-coverage lint fix loaddata

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	.venv/bin/python manage.py migrate
	.venv/bin/python manage.py load_data

server:
	.venv/bin/python manage.py runserver

lint:
	.venv/bin/isort --check-only .
	.venv/bin/black --check .
	.venv/bin/flake8 .

fix:
	.venv/bin/isort .
	.venv/bin/black .
	.venv/bin/flake8 .


test:
	.venv/bin/python -m pytest tests/ -v

test-coverage:
	.venv/bin/pytest --cov=. -q

loaddata:
	.venv/bin/python manage.py load_data
