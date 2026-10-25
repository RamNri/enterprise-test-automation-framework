
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

A Python-based, enterprise-style automation framework combining **Selenium UI automation**, **REST API testing**, parallel execution, Dockerized Selenium Grid, CI workflows, and an initial AWS container-execution and result-storage path.

The goal is to demonstrate more than individual test scripts: this project shows how an automation framework can be designed, structured, executed, diagnosed, and integrated with modern engineering infrastructure.

## Highlights

- Selenium WebDriver UI automation and REST API automation
- Enterprise API client and authentication manager
- Dependency injection and reusable assertions
- Builder, mapper, factory, service-layer, and response-object patterns
- Centralized configuration and execution-aware logging
- Faker seed isolation and thread-local execution context
- Parallel execution with `pytest-xdist`
- Local and remote Selenium execution
- Docker Compose-based Selenium Grid with Chrome node
- Failure diagnostics, screenshots, and artifact management
- `pytest-html` reporting with execution metadata
- Sensitive-data masking in logs
- CRUD API workflow testing
- Dockerized test execution
- GitHub Actions workflows for tests, BrowserStack, Docker Grid, and ECR image build/push
- One-off Amazon ECS Fargate test execution
- Raw Allure result upload to Amazon S3
- CloudWatch logs for task execution and diagnostics

## Architecture

```text
                           Tests
                            |
                 +----------+----------+
                 |                     |
           UI Automation         API Automation
                 |                     |
            Page Objects             Services
                 |                     |
             UI Actions             API Clients
                 |                     |
          Selenium WebDriver    Authentication / HTTP
                 |                     |
                 +----------+----------+
                            |
                    Test Infrastructure
                            |
          +-----------------+-----------------+
          |                 |                 |
    Execution Context     Logging        Diagnostics
          |                 |                 |
    Test Lifecycle       API Logging    Failure Artifacts
          |                 |                 |
    Parallel Execution   Data Masking   HTML Reporting
```

The framework separates test orchestration from application-facing layers and cross-cutting infrastructure.

### Architectural rules

1. Tests orchestrate workflows and assertions.
2. Services own business workflows.
3. API clients own HTTP communication.
4. Page objects own UI communication.
5. Mappers own request/response serialization.
6. Utilities remain generic and reusable.
7. Configuration is centralized.
8. Shared infrastructure belongs in `core` or dedicated framework infrastructure packages.

## Design Principles

### SOLID and framework principles

- Single Responsibility Principle
- Dependency injection
- Separation of concerns
- Testability
- Strongly typed models
- Reusable assertions
- Centralized logging
- Execution-context isolation
- Scalable folder structure
- Failure diagnostics and observability

### Design patterns

- Builder Pattern
- Mapper Pattern
- Service Layer
- Factory Pattern
- Response Object Pattern

## Selenium WebDriver Architecture

The Selenium layer supports multiple browsers and two execution modes: local and remote.

```text
                         DriverFactory
                              |
                  +-----------+-----------+
                  |                       |
                LOCAL                   REMOTE
                  |                       |
          +-------+-------+          Selenium Hub
          |       |       |               |
        Chrome Firefox  Edge          Chrome Node
                                          |
                                      Real Browser
```

`DriverFactory` creates and closes WebDriver sessions. Browser selection, headless mode, execution mode, and Grid URL are resolved through centralized configuration. The same tests can execute locally or remotely without changing test code.

## Selenium Grid with Docker

Selenium Grid is a first-class execution capability. Docker Compose starts a Hub and browser node, while a separate test-runner container executes pytest.

```text
                    Docker Compose
                         |
             +-----------+-----------+
             |                       |
        selenium-hub             test-runner
           :4444                      |
             ^                    pytest tests
             |
          chrome node
             |
        Chrome Browser
```

Inside Docker, the test runner connects to the Hub using the service name:

```text
http://selenium-hub:4444
```

`localhost:4444` would refer to the test-runner container itself, not the Hub.

### Run the suite through Docker Compose

```powershell
docker compose up --build --abort-on-container-exit test-runner
```

Inspect services and logs:

```powershell
docker compose ps
docker compose logs chrome
```

Stop the Grid:

```powershell
docker compose down
```

The Hub health check and Chrome-node dependency help reduce startup-order failures.

## Execution Context and Parallel Execution

The framework uses a thread-local execution context to keep metadata isolated across concurrent workers and threads. Context can include:

- Execution ID
- Worker ID
- Thread ID
- Test name
- Faker seed
- Browser and Selenium session ID
- Start time and duration
- Driver reference

A worker or thread may execute multiple tests, but each test receives a new execution ID and test-specific state. This helps correlate logs, reports, browser sessions, and failure artifacts.

Run in parallel:

```powershell
pytest -v -n 2
```

## API Automation Architecture

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
Booking              Booking
```

### Responsibilities

- **Tests:** orchestration and assertions
- **Services:** business workflows
- **Clients:** HTTP communication
- **Mappers:** serialization and deserialization
- **Models:** strongly typed request/domain data
- **Response objects:** structured response handling
- **Authentication Manager:** authentication lifecycle

Dependency injection keeps these layers independently testable.

## Configuration

Configuration is centralized and separates runtime settings from environment endpoints.

Runtime configuration includes browser, headless mode, execution mode, and Selenium Grid URL. Environment configuration includes application and API endpoints.

Examples of supported command-line configuration:

```powershell
pytest --browser chrome
pytest --headless
pytest --env local
pytest --execution-mode local
pytest --execution-mode remote
```

## Logging and Observability

Centralized logging can include timestamp, log level, logger name, execution ID, worker ID, thread ID, test name, Faker seed, browser/session information, and message. This makes framework activity traceable to a specific test execution.

API request/response logging can capture HTTP method, endpoint, request body, response status, reason, response body, response time, and execution context.

## Sensitive Data Masking

The framework masks sensitive information before writing it to logs. Examples include:

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

Masking is applied to request headers and structured request bodies. Never commit real credentials, access keys, tokens, or environment-specific secrets.

## Failure Diagnostics and Artifact Management

Failure processing is separated from pytest lifecycle hooks so components can be tested independently.

```text
Test Failure
     |
pytest lifecycle hook
     |
Failure Sanitizer
     |
Failure Artifact Manager
     |
Screenshot Capture
     |
pytest-html Report
```

For failed UI tests, the framework captures a browser screenshot and attaches it to the HTML report. Failure artifacts are isolated by worker and execution ID to avoid overwriting artifacts from parallel executions.

The framework can capture:

- Browser screenshots
- Failure information
- Execution metadata
- HTML report attachments

## HTML Reporting

The framework integrates with `pytest-html`. Report metadata can include:

| Metadata | Purpose |
|---|---|
| Execution ID | Identifies an individual test execution |
| Worker | Identifies the pytest worker |
| Thread | Identifies the execution thread |
| Browser | Identifies the browser used |
| Selenium Session ID | Correlates the test with its WebDriver session |
| Test Result | Pass/fail status |
| Duration | Test execution time |

For failed UI tests, the corresponding screenshot can be attached to the report.

## Intentional Failure Validation

The framework includes a dedicated test for validating the failure-artifact pipeline, marked with:

```python
@pytest.mark.artifact_validation
```

Normal execution excludes this intentional failure through `pytest.ini`. Run it explicitly:

```powershell
pytest -m artifact_validation
```

It is intentionally expected to fail so screenshot capture and HTML-report attachment can be validated.

## Docker

The framework can be packaged into a Docker image using the project `Dockerfile`.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["pytest"]
```

Docker provides a reproducible execution environment and is used by the local Selenium Grid workflow and CI image build.

## AWS Container Execution and S3 Results

The project has an initial AWS path for running API tests as a one-off ECS Fargate task.

```text
GitHub Actions
      |
      v
Docker image build
      |
      v
Amazon ECR
      |
      v
One-off ECS Fargate task
      |
      v
pytest API suite
      |
      v
Allure raw result files
      |
      v
Private Amazon S3 bucket
      |
      v
CloudWatch task logs
```

### Implemented and exercised

- Docker image build and push to Amazon ECR from GitHub Actions
- ECS Fargate task definition for a one-off run
- Task-role-based AWS access rather than credentials embedded in test code
- Raw Allure result upload to S3 under a unique run-specific prefix
- CloudWatch logs for execution and upload diagnostics

A successful ECS task log confirmed **13 Allure result files uploaded** to a run-specific S3 prefix.

### Allure HTML status

S3 currently contains raw Allure results, not the generated HTML dashboard. The next step is to generate the HTML report and publish it with controlled access. Keep the report bucket private unless a reviewed hosting design explicitly requires a different access model.

## Running the Tests

### Normal local execution

```powershell
pytest -v
```

### Run in parallel

```powershell
pytest -v -n 2
```

### Run unit tests

```powershell
pytest .\tests\unit -v
```

### Run headless

```powershell
pytest --headless
```

### Run remote Selenium Grid execution

```powershell
pytest --execution-mode remote
```

When running inside the Docker Compose test-runner, the Grid URL is:

```text
http://selenium-hub:4444
```

### Start Selenium Grid and run the suite

```powershell
docker compose up --build --abort-on-container-exit test-runner
```

### Stop the Grid

```powershell
docker compose down
```

### Inspect Grid services

```powershell
docker compose ps
```

### Inspect Chrome node logs

```powershell
docker compose logs chrome
```

### Run failure-artifact validation

```powershell
pytest -m artifact_validation -v -n 2 --html=artifacts/report.html --self-contained-html
```
## Project Structure

The main directories follow this general layout; some modules may evolve as the framework grows.

```text
enterprise-test-automation-framework/
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

Runtime-generated logs, reports, screenshots, and test artifacts are excluded from source control.

## GitHub Actions / CI Status

At the latest recorded checkpoint, these GitHub Actions job categories passed:

- Test suite
- BrowserStack execution
- Docker/Selenium Grid execution
- Docker image build and push to Amazon ECR

Check the repository's **Actions** tab for current status. The ECS Fargate task and S3 upload were also manually exercised. Fully automated orchestration from a GitHub event through ECS execution and browsable Allure HTML publication remains future work.
