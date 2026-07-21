.PHONY: install test lint demo

install:
	poetry install

test:
	poetry run pytest

lint:
	poetry run ruff check .

# Runnable HMAC request-integrity proof (valid -> 200, tamper -> 403).
demo:
	poetry run python demo/hmac_integrity_demo.py
