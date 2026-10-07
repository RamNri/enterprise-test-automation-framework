
# 🚀 OPEN FOR WORK: ENTERPRISE TEST AUTOMATION & AI QUALITY SPECIALIST
> **Are you an Engineering Manager, Tech Lead, or Recruiter looking for an advanced QA specialist?**  
> I am the sole architect of this framework. I combine **13+ years of enterprise QA leadership** (with proven tenures at **VMware** and **Amazon**) with deep **AWS Cloud Architecture** and **first-principles AI/LLM engineering metrics** (including testing RAG pipelines and hallucination validation).
> 
> I am actively interviewing for full-time roles: **Senior QA Automation Engineer | AI/ML Quality Engineer**.
> 
> 📬 **Let's connect and build together:**  
> 📧 **Direct Email:** nripeshsrivastawa@gmail.com  
> 🌐 **GitHub Profile:** [://github.com](https://github.com/RamNri)

---


# Enterprise Selenium + API Automation Framework

## Overview

This project is a automation framework built using Python. It combines Selenium UI automation and REST API automation inside a scalable, enterprise-style architecture.

The goal is not simply to write automated tests, but to demonstrate how an automation framework can be designed, structured, tested, executed, diagnosed, and evolved as a software system.

### Current capabilities

- Selenium UI Automation
- REST API Automation
- Enterprise API Client
- Authentication Manager
- Dependency Injection
- Builder Pattern
- Mapper Pattern
- Response Object Pattern
- Service Layer
- Reusable Assertions
- Enterprise Logging
- Execution Context
- Faker seed isolation
- Parallel execution with pytest-xdist
- Local and remote Selenium execution
- Selenium Grid with Docker Compose
- Failure diagnostics
- Failure artifact management
- Screenshot capture
- HTML test reporting
- Browser and Selenium session correlation
- Sensitive data masking
- CRUD API workflow testing
- Dockerized test execution

---

# Architecture

```text
                              Tests
                                |
                 +--------------+--------------+
                 |                             |
          UI Automation                 API Automation
                 |                             |
           Page Objects                   Services
                 |                             |
           UI Actions                    API Clients
                 |                             |
                 |                    Authentication Manager
                 |                             |
                 |                        API Client
                 |                             |
                 +--------------+--------------+
                                |
                                v
                       Test Infrastructure
                                |
             +------------------+------------------+
             |                  |                  |
       Execution Context    Logging          Diagnostics
             |                  |                  |
       Test Lifecycle       API Logging     Failure Artifacts
             |                  |                  |
       Parallel Execution    Masking        HTML Reporting
```

The framework separates test orchestration from application-facing layers and cross-cutting infrastructure.

### Architectural rules

1. Tests orchestrate only.
2. Services own business workflows.
3. API clients own HTTP communication.
4. Page objects own UI communication.
5. Mappers own request/response serialization.
6. Utilities remain generic and reusable.
7. Configuration is centralized.
8. Shared infrastructure belongs in `core` or dedicated framework infrastructure packages.

---

# Design Principles

The framework follows software engineering principles rather than being a collection of automation scripts.

## SOLID

- Single Responsibility Principle
- Dependency Injection
- Separation of Concerns
- Testability

## Design Patterns

- Builder Pattern
- Mapper Pattern
- Service Layer
- Factory Pattern
- Response Object Pattern

## Framework Principles

- Strongly typed models
- Reusable assertions
- Centralized logging
- Execution-context isolation
- Scalable folder structure
- Enterprise layer separation
- Failure diagnostics
- Observability

---

# Selenium WebDriver Architecture

The Selenium layer supports multiple browsers and two execution modes: local and remote.

```text
                         DriverFactory
                              |
                 +------------+------------+
                 |                         |
              LOCAL                     REMOTE
                 |                         |
        +--------+--------+                v
        |        |        |          Selenium Hub
      Chrome  Firefox    Edge              |
                                           v
                                      Chrome Node
                                           |
                                           v
                                      Real Browser
```

`DriverFactory` is responsible for creating and closing WebDriver sessions. Browser selection, headless mode, execution mode, and Grid URL are resolved through centralized configuration.

The same tests can therefore execute against a local browser or a remote browser without changing test code.

---

# Selenium Grid with Docker

Selenium Grid is a first-class execution capability of this framework.

The project uses Docker Compose to create a Selenium Grid consisting of a Hub and browser node, while a separate test-runner container executes the pytest suite.

## Grid architecture

```text
                         Docker Compose
                              |
                 +------------+------------+
                 |                         |
                 v                         v
          selenium-hub                 test-runner
             :4444                         |
                 ^                          |
                 |                          |
                 |                    pytest tests
                 |
                 v
             chrome node
                 |
                 v
           Chrome Browser
```

The complete remote execution flow is:

```text
pytest
  |
  v
DriverFactory
  |
  +---- LOCAL  ----> Local WebDriver
  |
  +---- REMOTE ----> Selenium Hub
                         |
                         v
                    Chrome Node
                         |
                         v
                    Chrome Browser
```

### Why this matters

The tests do not need to know whether Selenium is running locally or inside Grid. The execution mode is controlled by configuration.

Inside Docker, the test runner connects to the Hub using the Docker service name:

```text
http://selenium-hub:4444
```

`localhost:4444` would refer to the test-runner container itself and is therefore not the correct address for container-to-container Grid communication.

### Docker Compose topology

```yaml
services:
  selenium-hub:
    image: selenium/hub:4.41.0-20260222
    ports:
      - "4444:4444"

  chrome:
    image: selenium/node-chrome:4.41.0-20260222
    shm_size: 2gb
    depends_on:
      selenium-hub:
        condition: service_healthy
    environment:
      - SE_EVENT_BUS_HOST=selenium-hub

  test-runner:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      chrome:
        condition: service_started
    command: pytest --execution-mode remote
```

### Grid readiness

The Hub has a health check and the Chrome node depends on a healthy Hub. This reduces startup-order failures during containerized execution.

### Remote execution result

The complete Docker + Selenium Grid execution has been validated with the full framework suite:

```text
134 passed, 1 deselected
```

This confirms that the framework can execute its UI/API/unit coverage through the Dockerized remote Selenium path.

---

# Execution Context

The framework uses a thread-local execution context to maintain execution information independently for concurrent test workers/threads.

The context contains:

- Execution ID
- Worker ID
- Thread ID
- Test name
- Faker seed
- Browser
- Selenium Session ID
- Start time
- Duration
- Driver

A key distinction is maintained between worker identity, thread identity, and individual test execution identity.

```text
Worker
  |
  +-- Thread
       |
       +-- Test A --> Execution ID A
       |
       +-- Test B --> Execution ID B
       |
       +-- Test C --> Execution ID C
```

A worker or thread may execute multiple tests, but each test receives a new execution ID and test-specific execution state.

This allows logs, reports, browser sessions, and failure artifacts to be correlated with an individual test execution.

---

# Parallel Execution

Parallel execution is implemented using `pytest-xdist`.

```powershell
pytest -v -n 2
```

Conceptually:

```text
                         Pytest
                           |
              +------------+------------+
              |                         |
             gw0                       gw1
              |                         |
           Worker                    Worker
              |                         |
        +-----+-----+             +-----+-----+
        |     |     |             |     |     |
       T1    T2    T3            T4    T5    T6
        |     |     |             |     |     |
       E1    E2    E3            E4    E5    E6
```

Where:

- `gw0`, `gw1` represent pytest workers.
- Test execution IDs identify individual test executions.
- Worker/thread reuse does not cause execution metadata to leak between tests.

---

# API Automation Architecture

The API layer follows a service/client/mapper/model architecture.

```text
Tests
  |
  v
BookingService
  |
  v
BookingClient
  |
  v
BookingMapper
  |
  +-------------------+
  |                   |
  v                   v
BookingRequest   BookingResponse
  |                   |
  v                   v
Booking           Booking
```

### Responsibilities

- **Tests**: orchestration and assertions.
- **Services**: business workflows.
- **Clients**: HTTP communication.
- **Mappers**: serialization/deserialization.
- **Models**: strongly typed request/domain data.
- **Response objects**: structured response handling.
- **Authentication Manager**: authentication lifecycle.

Dependency injection is used to keep these layers independently testable.

---

# Configuration

Configuration is centralized and separated into environment and runtime concerns.

Runtime configuration includes:

- Browser
- Headless mode
- Execution mode
- Selenium Grid URL

Environment configuration includes application and API endpoints.

The framework supports command-line configuration such as:

```powershell
pytest --browser chrome
pytest --headless
pytest --env local
pytest --execution-mode local
pytest --execution-mode remote
```

The same test suite can therefore be executed with different runtime configurations without modifying test code.

---

# Logging

The framework provides centralized execution-aware logging using Python's logging infrastructure.

Logs can include:

- Timestamp
- Log level
- Logger name
- Execution ID
- Worker ID
- Thread ID
- Test name
- Faker seed
- Browser/session information
- Message

Example:

```text
2026-08-27 11:44:44 | INFO | core.driver.driver_factory |
[exec=07e9b33c... | worker=gw0 | thread=34064 |
test=tests/test_failure_artifacts.py::test_failure_artifact |
seed=904989091] |
Browser created : chrome
```

This makes framework activity traceable to a specific test execution.

---

# API Logging

API requests and responses are logged with execution context.

```text
HTTP REQUEST
POST /booking
      |
      v
HTTP RESPONSE
200 OK
Elapsed : 0.32 sec
```

API logging includes:

- HTTP method
- Endpoint
- Request body
- Response status
- Response reason
- Response body
- Response time
- Execution context

Sensitive information is masked before being written to logs.

---

# Sensitive Data Masking

The framework prevents sensitive information from being exposed in logs.

Sensitive fields include values such as:

```text
password
token
access_token
refresh_token
authorization
api_key
secret
client_secret
```

Example:

```json
{
  "username": "user",
  "password": "********"
}
```

Masking is applied to request headers and structured request bodies.

---

# Failure Diagnostics

Failure diagnostics are implemented as a dedicated framework capability.

```text
Test Failure
     |
     v
pytest lifecycle hook
     |
     v
Failure Sanitizer
     |
     v
Failure Artifact Manager
     |
     v
Screenshot Capture
     |
     v
pytest-html Report
```

For failed UI tests, the framework captures a browser screenshot and attaches it to the HTML report.

Failure processing is separated from the pytest lifecycle so individual components remain independently testable.

---

# Failure Artifact Management

Failure artifacts are isolated by worker and execution ID.

```text
artifacts/
└── screenshots/
    └── gw0/
        └── <execution_id>/
            └── test_failure_artifact_<timestamp>.png
```

This prevents artifacts from different parallel executions from overwriting one another.

The framework currently captures:

- Browser screenshots
- Failure information
- Execution metadata
- HTML report attachments

---

# HTML Reporting

The framework integrates with `pytest-html`.

The report includes execution metadata such as:

| Metadata | Purpose |
|---|---|
| Execution ID | Identifies the individual test execution |
| Worker | Identifies the pytest worker |
| Thread | Identifies the execution thread |
| Browser | Identifies the browser used |
| Selenium Session ID | Correlates the test with its WebDriver session |
| Test Result | Pass/fail status |
| Duration | Test execution time |

For failed UI tests, the corresponding screenshot is attached to the HTML report.

The diagnostic path is therefore:

```text
Failed Test
    |
    v
Execution ID
    |
    v
Worker / Thread
    |
    v
Browser Session
    |
    v
Screenshot
    |
    v
Logs
```

---

# Intentional Failure Validation

The framework contains a dedicated test for validating the failure-artifact pipeline.

It is marked with:

```python
@pytest.mark.artifact_validation
```

Normal execution excludes this intentional failure through `pytest.ini`.

```powershell
pytest
```

The validation test can be executed explicitly:

```powershell
pytest -m artifact_validation
```

It is intentionally expected to fail so the screenshot capture and HTML-report attachment mechanisms can be validated.

---

# Docker

The framework can be packaged into a Docker image using the project `Dockerfile`.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["pytest"]
```

Docker provides a reproducible environment for running the framework and forms the foundation for later CI/CD and cloud execution.

---

# Project Structure

```text
SELENIUM_FRAMEWORK/
├── config/
├── core/
│   ├── driver/
│   ├── execution/
│   └── logger.py
├── ui/
│   ├── browser/
│   ├── pages/
│   ├── page_components/
│   ├── locators/
│   ├── waits/
│   ├── actions/
│   └── validations/
├── api/
│   ├── client/
│   ├── clients/
│   ├── models/
│   ├── mappers/
│   ├── responses/
│   └── services/
├── database/
├── framework_logging/
├── services/
├── utilities/
├── test_data/
├── tests/
│   ├── ui/
│   ├── api/
│   ├── database/
│   └── integration/
├── reports/
├── logs/
├── artifacts/
├── conftest.py
├── pytest.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

Runtime-generated artifacts are excluded from source control.

---

# Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| Test Runner | Pytest |
| UI Automation | Selenium WebDriver |
| API Automation | Requests |
| Parallel Execution | pytest-xdist |
| Containerization | Docker |
| Grid | Selenium Grid |
| Orchestration | Docker Compose |
| Reporting | pytest-html |
| Logging | Python Logging |
| Test Data | Faker |
| Version Control | Git |

---

# Testing Strategy

The framework itself is tested using unit tests in addition to integration and framework-level validation.

Testing covers areas including:

- Execution Context
- Configuration
- Runtime configuration
- Driver behavior
- Logging utilities
- Failure sanitization
- Failure artifact management
- Execution lifecycle
- Sensitive-data masking
- Framework configuration
- Parallel execution
- Dockerized remote execution

The framework also performs real parallel execution validation using pytest-xdist.

---

# Running the Tests

## Normal local execution

```powershell
pytest -v
```

## Run in parallel

```powershell
pytest -v -n 2
```

## Run unit tests

```powershell
pytest .\tests\unit -v
```

## Run headless

```powershell
pytest --headless
```

## Run remote Selenium Grid execution

```powershell
pytest --execution-mode remote
```

When running from inside the Docker Compose test-runner, the framework uses:

```text
http://selenium-hub:4444
```

## Start Selenium Grid and run the complete suite

```powershell
docker compose up --build --abort-on-container-exit test-runner
```

## Stop the Grid

```powershell
docker compose down
```

## Inspect Grid services

```powershell
docker compose ps
```

## Inspect Chrome node logs

```powershell
docker compose logs chrome
```

## Run failure-artifact validation

```powershell
pytest -m artifact_validation -v -n 2 --html=artifacts/report.html --self-contained-html
```

---

# Git and Generated Artifacts

Runtime artifacts are intentionally excluded from source control.

```text
artifacts/
├── logs/
├── screenshots/
└── report.html
```

Source code, framework components, tests, Docker configuration, and project configuration remain version controlled.

---

# Roadmap

The framework is being evolved deliberately from framework fundamentals toward enterprise execution, reporting, CI/CD, cloud, integrations, and AI-assisted engineering.

## Phase 1 — Enterprise Framework Core

- [x] UI Automation
- [x] API Automation
- [x] Builders
- [x] Mappers
- [x] Services
- [x] Dependency Injection
- [x] Authentication
- [x] CRUD
- [x] Assertions
- [x] Enterprise Logging
- [x] Retry Policy
- [x] Retry Policy Unit Tests
- [ ] Custom Exceptions
- [ ] Faker expansion
- [ ] Advanced Fixtures
- [x] Pytest Markers

## Phase 2 — Enterprise Execution

- [x] Parallel Execution with pytest-xdist
- [x] Docker
- [x] Docker Compose
- [x] Selenium Grid
- [ ] BrowserStack

## Phase 3 — Enterprise Reporting

- [x] Pytest HTML baseline
- [ ] Allure
- [ ] Screenshots expansion
- [ ] Video capture
- [ ] API attachments
- [ ] Centralized logs in reports
- [ ] Environment metadata
- [ ] Categories/history

## Phase 4 — Cloud & DevOps

- [ ] GitHub Actions
- [ ] Docker image build in CI
- [ ] AWS ECR
- [ ] AWS ECS / EC2 execution
- [ ] S3 report publishing
- [ ] CloudFront report hosting
- [ ] IAM
- [ ] Secrets Manager
- [ ] Parameter Store
- [ ] Scheduled regression
- [ ] CloudWatch
- [ ] SNS notifications

Target architecture:

```text
GitHub Push
    |
    v
GitHub Actions
    |
    v
Docker Image
    |
    v
AWS ECR
    |
    v
AWS ECS / EC2
    |
    v
Selenium + API Tests
    |
    v
Allure Results
    |
    v
S3
    |
    v
CloudFront
    |
    v
Slack / Notification
```

## Phase 5 — Integrations

- [ ] BrowserStack integration
- [ ] Slack notifications
- [ ] Email notifications
- [ ] Jira integration
- [ ] TestRail integration where applicable
- [ ] REST-based enterprise integrations


# Enterprise Evolution

The framework is intentionally being built in layers.

```text
Automation Scripts
       |
       v
Reusable Framework
       |
       v
Enterprise Execution
       |
       v
Docker + Selenium Grid
       |
       v
Cloud Execution
       |
       v
CI/CD
       |
       v
Observability + Integrations
       |
       v
AI-Assisted Quality Engineering
```

This progression demonstrates not only test automation skills, but also framework architecture, distributed execution, containerization, DevOps awareness, observability, and engineering leadership.
