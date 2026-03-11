install:
	uv sync

build:
	./build.sh

lint:
	uv run ruff check .

render-start:
	uv run gunicorn task_manager.wsgi

django-tests:
	uv run manage.py test

test:
	uv run pytest

test-coverage:
	uv run pytest --cov=gendiff --cov-report=xml:coverage.xml