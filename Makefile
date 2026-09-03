.PHONY: test up down integration

test:
	pytest tests/api tests/integration tests/resilience -v

up:
	docker compose up -d --build postgres redis api worker

down:
	docker compose down -v

integration:
	docker compose --profile test run --rm integration-tests
