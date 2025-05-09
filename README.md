# System for Logging, Alerts, and Task distribution  
Author: **Anastasiia Plaskonis**  
Course: *Architecture of IT Solutions*, Ukrainian Catholic University

---

## Description

This application is built using **FastAPI** and designed to process user-submitted input by:

- detecting sensitive personal data
- logging all events and alerts
- offloading heavy processing to background workers via **Celery**

The system uses **Redis** as a message broker and is ready for container-based deployment. It supports both synchronous and asynchronous task flows.

---

## How it works

### Main components

- **FastAPI endpoint (`/run`)**: receives authorized requests, parses input, and delegates tasks.
- **Celery processor**: handle processing tasks in the background.
- **Redis broker**: manages message queues between FastAPI and Celery.
- **Logger**: captures runtime activity to `logs/app.log`.
- **Alert subsystem**: scans input for patterns like email or Ukrainian phone numbers and creates alert files in `alert_reports/`.

---

### Operational flow

1. A request is sent to `/run` with a bearer token.
2. FastAPI authenticates and logs the request.
3. Data is scanned for sensitive patterns.
4. Alerts (if needed) are generated as `.txt` reports.
5. The task is queued to Celery via Redis.
6. Celery completes processing and sends the result back.
7. The result is returned to the user and logged.

---

## Installation and setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Redis
```bash
redis-server
```

### 3. Launch Celery process
```bash
# Start 2 Celery workers as required by the task
celery -A celery_process.celery_app worker --loglevel=info --concurrency=2
```

### 4. Start FastAPI application
```bash
uvicorn client_service:app --reload
```

---

## Test request

You can test the application using `curl`:
```bash
curl -X POST http://127.0.0.1:8000/run -H "Authorization: Bearer Secret123"
```

If the input contains personal details like phone numbers or email addresses, an alert will be generated in `alert_reports/`.

---

## Files and output

- **Logs**: `logs/app.log`
- **Alerts**: `alert_reports/alert_<timestamp>.txt`

**Sample alert report:**
```
ALERT TYPE: email
TIME: 2025-05-09_22-03-38
DATA: {'name': 'Anastasiia Plaskonis', 'email': 'plaskonis.pn@ucu.edu.ua', 'phone': '+3801234567'}
```

---

## System design overview

This solution integrates several components to ensure efficient handling of user requests, secure data processing, and asynchronous task execution. Here’s how the system is structured:

### Core modules

- **API Gateway (FastAPI):**  
  Handles incoming HTTP requests at the `/run` endpoint. It performs access control, writes interaction details to log files, and evaluates the payload for sensitive content before passing it along for background processing.

- **Task queue (Redis):**  
  Serves as a communication layer between the web interface and the background workers. Redis stores and forwards messages that represent queued tasks.

- **Background processor (Celery Processor):**  
  Responsible for executing tasks asynchronously. Once data is validated by FastAPI, it is sent to Celery, where it is processed without blocking the main application thread.

- **Logging framework:**  
  Logs all events related to system usage, error traces, and warnings to a structured text file located in `logs/app.log`, using Python’s standard logging utilities.

- **Alert handler:**  
  A utility embedded in the request validation logic that scans inputs for indicators such as email addresses or Ukrainian-format phone numbers. On detection, it generates a short-form report file with a timestamp and type of alert, saved under `alert_reports/`.

---

### Request lifecycle summary

| Step | Operation | Execution Mode |
|------|-----------|----------------|
| 1 | Client sends POST request with authorization token | Synchronous |
| 2 | Server validates token and records log entry | Synchronous |
| 3 | Alert subsystem checks for sensitive info and creates report if necessary | Synchronous |
| 4 | Input is passed to Celery through Redis | Asynchronous |
| 5 | Celery processes task and returns output | Asynchronous |
| 6 | Final result is logged and delivered to client | Synchronous |

---

## Scalability strategy

As user load increases, adjustments to infrastructure become necessary to maintain performance. Below is a breakdown of recommended scaling actions:

### <10 concurrent users
- **API Layer**  >>   single FastAPI instance is sufficient for basic throughput.
- **Workers**    >>   one Celery worker can handle the asynchronous jobs without delay.
- **Redis**      >>   standalone Redis instance provides stable queue management.
- **Monitoring** >>   minimal; file-based logs and alerts perform adequately.

### <50 concurrent users
- **API Layer**  >>   Employ a process manager (e.g., Gunicorn) to enable 2–4 worker processes for better concurrency.
- **Workers**    >>   Deploy an additional 1–2 Celery workers to handle load in parallel.
- **Redis**      >>   Continue with single-node Redis, but begin performance observation.
- **Monitoring** >>   Check log/alert write speeds as file I/O may become a minor bottleneck.

### >100 concurrent users
- **API Layer**  >>
  - Scale horizontally using containerized FastAPI instances.
  - Introduce a reverse proxy or load balancer (e.g., Nginx, Traefik) to route requests evenly.
- **Workers**    >>
  - Increase worker count to 4–6 or distribute across multiple nodes.
  - Optionally segregate task types via named queues.
- **Redis**      >>
  - Upgrade to Redis Cluster or adopt a cloud-hosted variant (e.g., AWS ElastiCache).
  - Track memory and response time.
- **Monitoring** >>
  - Migrate logging to centralized systems (e.g., ELK stack, Cloud Logging).
  - Transition alert reports to a structured queue or database for scalable storage.

---

### Resource planning summary

| Layer          | 10 Users           | 50 Users                     | 100+ Users                                |
|----------------|--------------------|-------------------------------|--------------------------------------------|
| FastAPI        | 1 instance         | 2–4 Gunicorn workers          | Multiple load-balanced containers          |
| Celery Workers | 1 process          | 2–3 workers                   | 4–6+ workers (potentially distributed)      |
| Redis          | Single instance    | Monitored single instance     | Redis Cluster or managed Redis             |
| Logging        | Local text files   | Local files                   | ELK/cloud-based logging                    |
| Alerts         | File per report    | File-based                    | Queued or DB-stored alerts                 |