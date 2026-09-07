# Distributed System Test Framework

A Python portfolio project focused on **system, integration, resilience and fault-injection testing** of an asynchronous distributed application.

The application itself is intentionally small. Its purpose is to provide realistic system behavior that can be stimulated, observed and disrupted through automated tests.

The project applies validation principles commonly used in embedded/HIL testing — state transitions, multiple observables, deterministic fault injection, timing constraints and recovery validation — to a software stack based on APIs, queues, workers and databases.

## Architecture

```text
Client / pytest
      |
      | REST
      v
+-------------+
| FastAPI API |
+------+------+
       |
       +--------------------+
       |                    |
       v                    v
+-------------+       +-------------+
| PostgreSQL  |       | Redis       |
| persistence |       | job queue   |
+-------------+       +------+------+
                            |
                            v
                      +-------------+
                      | Worker(s)   |
                      | async jobs  |
                      +------+------+
                             |
                             v
                 CREATED -> PROCESSING
                         -> READY / FAILED
```

The baseline implementation uses a Redis-backed processing queue.

A separate Redis Streams implementation is also included to explore **consumer groups, acknowledgement and stale in-flight job recovery** without replacing the existing validated queue path.

## What this project demonstrates

* Python test automation with `pytest`
* REST API functional and negative testing
* asynchronous state validation using polling and bounded timeouts
* PostgreSQL persistence and API-to-database consistency validation
* Redis-backed asynchronous job processing
* worker crash and restart recovery
* Redis outage and recovery validation
* PostgreSQL outage and recovery validation
* deterministic failure-path testing
* duplicate-processing and idempotency checks
* correlation ID propagation across API and worker processing
* multi-worker processing against a shared queue
* processing latency guardrails
* Docker-based end-to-end environments
* GitHub Actions CI
* Redis Streams consumer groups
* message acknowledgement with `XACK`
* stale pending-message recovery with `XAUTOCLAIM`
* recovery of an in-flight `PROCESSING` job by another consumer

## Stack

`Python` · `pytest` · `FastAPI` · `SQLAlchemy` · `PostgreSQL` · `Redis` · `Redis Streams` · `Docker Compose` · `GitHub Actions` · `httpx`

## Test strategy

### API and contract tests

Validate HTTP behavior, payload validation, error contracts and basic state-machine rules.

These tests are kept fast and do not require the full distributed environment.

### Integration tests

Validate behavior across component boundaries, including:

* asynchronous state transitions
* API-to-PostgreSQL consistency
* Redis Stream producer/consumer behavior
* message acknowledgement
* multi-worker processing
* stream-worker processing

### End-to-end tests

Exercise the complete distributed flow:

```text
POST /devices
    -> PostgreSQL: CREATED
    -> Redis queue
    -> Worker
    -> PostgreSQL: PROCESSING
    -> PostgreSQL: READY / FAILED
```

Tests use bounded polling instead of fixed sleeps wherever the expected system state is observable.

### Resilience and fault-injection tests

The framework deliberately disrupts infrastructure and validates recovery behavior.

Scenarios include:

```text
Worker crash
    -> restart
    -> pending job recovery
    -> READY
```

```text
Redis unavailable
    -> API cannot enqueue work
    -> Redis restored
    -> new job accepted
    -> READY
```

```text
PostgreSQL unavailable
    -> persistence-dependent request fails
    -> PostgreSQL restored and ready
    -> system accepts work again
    -> READY
```

For multi-consumer failover, the Redis Streams implementation validates:

```text
consumer-1 receives job
    -> device enters PROCESSING
    -> message remains unacknowledged
    -> message becomes stale
    -> consumer-2 claims it with XAUTOCLAIM
    -> job is retried
    -> READY
```

`processing_count` is used as an observable to distinguish normal processing from retry/recovery behavior.

## Queue reliability experiments

The project contains two queue approaches for different test purposes.

### Redis List processing

The baseline worker uses a main queue and an in-flight processing queue. Jobs are moved atomically before processing and removed only after successful completion.

This supports worker restart recovery and demonstrates at-least-once processing behavior.

### Redis Streams

A separate implementation explores Redis-native consumer reliability:

* `XADD` — append a job to the stream
* `XREADGROUP` — deliver work to a consumer group
* `XACK` — acknowledge successful processing
* `XAUTOCLAIM` — transfer ownership of stale pending work to another consumer

The Streams implementation was introduced specifically to validate multi-worker failover where one consumer disappears while another remains active.

## Parallel worker validation

The worker service can be scaled to multiple instances:

```bash
docker compose up -d --build --scale worker=2 postgres redis api worker
```

Tests verify that independent jobs can be consumed by different workers while preserving unique device state and avoiding duplicate processing.

## Timing validation

The suite includes an end-to-end processing latency guardrail.

This is used as a regression threshold rather than as a full load-performance benchmark.

## Observability

The system exposes several test observables:

* HTTP responses
* persisted PostgreSQL state
* Redis queue/stream state
* device state transitions
* `processing_count`
* worker logs
* correlation IDs
* CI test results
* code coverage

This allows tests to validate not only the final result, but also recovery and retry behavior across component boundaries.

## CI

GitHub Actions separates fast tests from tests that require the real distributed stack.

Fast checks cover API behavior, contracts and state-machine logic.

Docker integration jobs start PostgreSQL, Redis, FastAPI and worker services before running end-to-end and resilience scenarios.

## Why I built this

My background is in embedded-system and HIL validation, where testing commonly involves stimulating a system, observing state across multiple interfaces, injecting faults, analyzing timing and validating recovery.

This project applies the same validation mindset to distributed software systems.

The project applies the same system-validation mindset to APIs, databases, queues and asynchronous workers.

Instead of power-cycle or communication fault injection, the tests stop workers, Redis or PostgreSQL and validate deterministic recovery behavior.

The goal is not to build a large application. The goal is to demonstrate **system-level test engineering on realistic asynchronous and failure-prone behavior**.

## Remaining optional extensions

* Prometheus runtime metrics
* Grafana dashboards
* Allure reporting
* Playwright UI layer
* higher-load performance testing
