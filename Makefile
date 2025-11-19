install:
	poetry install

project:
	poetry run project

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	poetry install

lint:
	poetry run ruff check .

test:
	poetry run project
