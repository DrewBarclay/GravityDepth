.PHONY: test run

test:
	poetry run pytest tests/

run:
	poetry run python game.py