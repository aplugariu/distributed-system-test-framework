# Distributed System Test Framework

A portfolio project demonstrating **Python-based system and integration testing** for an asynchronous distributed application.

The project translates system-validation concepts commonly used in embedded/HIL environments—state transitions, fault paths, recovery validation, deterministic test data and observability—into a modern software stack.

## Architecture

```text
Client / pytest
     |
     | REST
     v
+-----------+       +------------+       +-----------+
| FastAPI   | ----> | PostgreSQL |       |   Redis   |
| API       |       | device DB  |       |   queue   |
+-----------+       +------------+       +-----+-----+
                                               |
                                               v
                                         +-----------+
                                         |  Worker   |
                                         | async job |
                                         +-----+-----+
                                               |
                                               v
                                      CREATED -> PROCESSING
                                               -> READY/FAILED
```

## What this demonstrates

- Python test automation with `pytest`
- REST API functional and negative testing
- asynchronous state validation with polling/timeouts
- PostgreSQL persistence
- Redis-backed asynchronous processing
- deterministic failure-path testing
- Docker Compose integration environments
- CI with GitHub Actions
- clean separation of API, service and worker layers
- testable state-machine behavior

## Stack

`Python` · `pytest` · `FastAPI` · `SQLAlchemy` · `PostgreSQL` · `Redis` · `Docker Compose` · `GitHub Actions` · `httpx`

## Test strategy

### API tests
Validate HTTP contracts, input validation and error behavior.

### Integration tests
Validate application state and persistence behavior.

### Docker end-to-end tests
Exercise the complete path:

```text
POST /devices
    -> PostgreSQL
    -> Redis queue
    -> Worker
    -> PROCESSING
    -> READY or FAILED
```

Instead of using fixed sleeps, tests poll for the expected system state using a bounded timeout. This mirrors real-world validation of asynchronous systems.

### Failure-path test
Creating a device named `force-failure` intentionally drives the worker into a controlled failure path and validates that the externally observable state becomes `FAILED`.

This provides a simple base for future fault-injection scenarios such as worker restarts, Redis outages, database outages, duplicate events and delayed processing.

## Run locally

### Fast local tests

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
pytest tests/api tests/integration tests/resilience -v
```

### Full distributed stack

```bash
docker compose up -d --build postgres redis api worker
docker compose --profile test run --rm integration-tests
docker compose down -v
```

API documentation is available at `http://localhost:8000/docs` while the stack is running.

## Roadmap

- [ ] add retries and idempotency validation
- [ ] add worker-restart recovery test
- [ ] add Redis outage/recovery scenario
- [ ] add PostgreSQL consistency assertions
- [ ] add structured logs and correlation IDs
- [ ] add Prometheus metrics and Grafana dashboard
- [ ] add Playwright UI layer
- [ ] add Allure test reporting
- [ ] add performance/latency thresholds

## Why I built this

My background is in embedded-system and HIL validation, where testing often means more than checking a return value: stimulate the system, observe state transitions across interfaces, inject faults, analyze timing and verify recovery.

This repository applies the same engineering mindset to distributed software systems using Python, APIs, queues, databases and CI/CD.
