.PHONY: up down test lint smoke logs reset

up:
	docker compose up --build

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up --build

test:
	docker compose run --rm backend pytest -q --cov=app --cov-report=term-missing
	docker compose run --rm frontend npm test -- --run

lint:
	docker compose run --rm backend ruff check app tests
	docker compose run --rm backend mypy app
	docker compose run --rm frontend npm run lint

smoke:
	python scripts/smoke_test.py

logs:
	docker compose logs -f
