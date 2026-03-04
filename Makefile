install:
	uv sync

build:
	./build.sh

lint:
	uv run ruff check .

render-start:
	uv run gunicorn task_manager.wsgi