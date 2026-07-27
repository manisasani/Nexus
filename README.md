````md
# Nexus

A modern Freelance Marketplace Backend built with Django and Django REST Framework.

---

## About

Nexus is a backend project for a freelance marketplace where clients can post projects and freelancers can submit proposals.

This project is being developed step by step with production-ready architecture and modern backend practices.

Current status: **Phase 3 completed (JWT Authentication implemented).**

---

## Tech Stack

* Python 3.12
* Django
* Django REST Framework (DRF)
* django-filter
* djangorestframework-simplejwt
* SQLite (temporary, PostgreSQL will be introduced in Phase 5)

---

## Project Setup

### 1. Clone the repository
\`\`\`bash
git clone <repository-url>
cd Nexus
\`\`\`

### 2. Create and activate a virtual environment
\`\`\`bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/macOS
\`\`\`

### 3. Install dependencies
\`\`\`bash
pip install -r requirements/base.txt
\`\`\`

### 4. Set up PostgreSQL
Make sure PostgreSQL is running locally (or via Docker — see below), and
create a database:
\`\`\`sql
CREATE DATABASE nexus_db;
\`\`\`

Or with Docker:
\`\`\`bash
docker run --name nexus-postgres -e POSTGRES_PASSWORD=yourpassword -e POSTGRES_DB=nexus_db -p 5432:5432 -d postgres:16
\`\`\`

### 5. Configure environment variables
\`\`\`bash
cp .env.example .env
\`\`\`
Then edit \`.env\` and fill in real values (SECRET_KEY, DATABASE_URL, etc).
Generate a secret key with:
\`\`\`bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
\`\`\`

### 6. Apply migrations
\`\`\`bash
python manage.py migrate
\`\`\`

### 7. Create a superuser
\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 8. Run the development server
\`\`\`bash
python manage.py runserver
\`\`\`

# API Authentication (JWT)

Nexus uses JWT authentication powered by `djangorestframework-simplejwt`.

The API uses Access Tokens and Refresh Tokens for authentication.

Authenticated requests must include:

```http
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

| Method | Endpoint                        | Description                        |
| ------ | ------------------------------- | ---------------------------------- |
| POST   | `/api/v1/auth/register/`        | Register a new user                |
| POST   | `/api/v1/auth/login/`           | Login and receive JWT tokens       |
| POST   | `/api/v1/auth/refresh/`         | Refresh access token               |
| POST   | `/api/v1/auth/logout/`          | Logout and blacklist refresh token |
| GET    | `/api/v1/auth/me/`              | Get current authenticated user     |
| POST   | `/api/v1/auth/password-change/` | Change current user's password     |

---

## JWT Token Lifecycle

JWT authentication uses two types of tokens:

### Access Token

* Used for accessing protected API endpoints.
* Short-lived for better security.
* Sent with every authenticated request.

Example:

```http
Authorization: Bearer eyJhbGciOiJIUzI1Ni...
```

---

### Refresh Token

* Long-lived token used to obtain a new access token.
* Used only with the refresh endpoint.

Example login response:

```json
{
    "access": "eyJhbGciOiJIUzI1Ni...",
    "refresh": "eyJhbGciOiJIUzI1Ni..."
}
```

---

## Logout Strategy

Logout is implemented using JWT blacklist functionality.

When a user logs out:

1. The refresh token is sent to the logout endpoint.
2. The refresh token is added to the blacklist.
3. The blacklisted refresh token cannot be used again to generate new access tokens.

Access tokens remain valid until they naturally expire because JWT authentication is stateless.

---

## JWT Storage Recommendation

JWT tokens should not be stored in browser `localStorage`.

Although convenient, localStorage can expose tokens to JavaScript-based attacks such as XSS (Cross-Site Scripting).

Recommended production approaches:

* Store refresh tokens inside secure HttpOnly cookies.
* Keep access tokens short-lived.
* Use Secure and SameSite cookie settings.

For this backend project, authentication logic is implemented on the API side and frontend token storage strategy will be decided depending on the client application.

---

# Health Check

Endpoint:

```text
GET /api/v1/health/
```

Example:

```text
http://127.0.0.1:8000/api/v1/health/
```

Expected response:

```json
{
    "status": "ok",
    "service": "Nexus"
}
```

---

# Django Admin

```text
http://127.0.0.1:8000/admin/
```

Login using your superuser credentials.

---

# Current Features

* Custom User Model
* Role-based users (Client / Freelancer)
* Client Profile
* Freelancer Profile
* Django Admin configuration
* Health Check API
* REST API foundation
* API Versioning (/api/v1/)
* JWT Authentication with SimpleJWT
* JWT logout with token blacklist
* Login and register throttling
* Project CRUD with role-based permissions
* Proposal system with marketplace business rules
* Object-level and queryset-level permission scoping
* Filtering and pagination on list endpoints

---

# Projects API

| Method | Endpoint                 | Who                          | Description                 |
| ------ | ------------------------ | ---------------------------- | --------------------------- |
| GET    | `/api/v1/projects/`      | Authenticated                | List OPEN projects          |
| GET    | `/api/v1/projects/mine/` | Authenticated owner          | List user's projects        |
| POST   | `/api/v1/projects/`      | CLIENT only                  | Create project              |
| GET    | `/api/v1/projects/{id}/` | Owner or public OPEN project | Retrieve project            |
| PATCH  | `/api/v1/projects/{id}/` | Owner only                   | Update project              |
| DELETE | `/api/v1/projects/{id}/` | Owner only                   | Delete project (DRAFT only) |

---

# Proposals API

Nested under projects:

| Method | Endpoint                                               | Who                 | Description           |
| ------ | ------------------------------------------------------ | ------------------- | --------------------- |
| GET    | `/api/v1/projects/{project_id}/proposals/`             | Owner/Freelancer    | List proposals        |
| POST   | `/api/v1/projects/{project_id}/proposals/`             | FREELANCER only     | Submit proposal       |
| GET    | `/api/v1/projects/{project_id}/proposals/{id}/`        | Owner or freelancer | Retrieve proposal     |
| PATCH  | `/api/v1/projects/{project_id}/proposals/{id}/`        | Freelancer owner    | Edit pending proposal |
| DELETE | `/api/v1/projects/{project_id}/proposals/{id}/`        | Freelancer owner    | Delete proposal       |
| POST   | `/api/v1/projects/{project_id}/proposals/{id}/accept/` | Project owner       | Accept proposal       |
| POST   | `/api/v1/projects/{project_id}/proposals/{id}/reject/` | Project owner       | Reject proposal       |

---

# Filtering

Project list supports:

| Parameter  | Example            | Description              |
| ---------- | ------------------ | ------------------------ |
| status     | `?status=OPEN`     | Filter by project status |
| budget_min | `?budget_min=100`  | Minimum budget           |
| budget_max | `?budget_max=5000` | Maximum budget           |

Example:

```text
GET /api/v1/projects/?status=OPEN&budget_min=100&budget_max=5000
```

---

# Pagination

All list endpoints use DRF `PageNumberPagination`.

Default page size:

```text
10 items per page
```

Example response:

```json
{
    "count": 45,
    "next": "http://127.0.0.1:8000/api/v1/projects/?page=2",
    "previous": null,
    "results": []
}
```

---

# API Demo / Manual Testing

A complete API testing workflow is available at:

```text
http/nexus.http
```

Open it using VS Code REST Client extension.

The file includes:

* JWT login flow
* Project creation
* Project updates
* Proposal submission
* Accept/reject actions
* Permission failure scenarios
* Validation error scenarios

---

# Project Structure

```
apps/
 ├── accounts/
 ├── projects/
 ├── core/

config/

requirements/

http/
```

---

# Development Roadmap

## ✅ Phase 1

* Project foundation
* Custom User
* Profiles
* Admin configuration
* Health Check API

---

## ✅ Phase 2

* Project model + admin
* Proposal model + admin
* Project CRUD API
* Object permissions
* Proposal system
* Filtering
* Pagination
* Nested proposal endpoints
* API demo testing

---

## ✅ Phase 3

* JWT Authentication with SimpleJWT
* Login/Register endpoints
* Refresh token support
* Logout with blacklist
* Password change endpoint
* Authentication throttling

---

## 🚧 Future Phases

* Automated tests
* PostgreSQL migration
* Query optimization
* Docker setup
* CI/CD pipeline
* Production deployment

---

# Known Technical Debt

See `TECH_DEBT.md` for tracked items.

Current items:

* N+1 queries on related user/project fields (optimization planned)
* ACCEPTED proposal status has no payment/contract workflow yet
* Frontend JWT storage strategy needs production decision
* Automated test suite is not implemented yet

---

# License

This project is being developed for educational and portfolio purposes.

```
```
## API Versioning

All endpoints are served under `/api/v1/`. Breaking changes (removed/renamed
fields, changed data types, altered status code meaning) will be introduced
under a new prefix (`/api/v2/`) rather than modifying `v1` in place.
Non-breaking changes (new optional fields, new endpoints) may be added to
`v1` directly.

## API Documentation

Interactive API documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- Raw OpenAPI schema: `http://127.0.0.1:8000/api/v1/schema/`

## Error Response Format

All API errors follow a consistent shape:

```json
{
  "detail": "Human-readable summary of what went wrong",
  "code": "machine_readable_error_code",
  "errors": { "field_name": ["Specific validation message"] }
}
```

| HTTP Status | code | Meaning |
|---|---|---|
| 400 | `validation_error` | Request failed validation or business rules |
| 401 | `authentication_failed` | Missing or invalid credentials |
| 403 | `permission_denied` | Authenticated but not allowed |
| 404 | `not_found` | Resource does not exist |
| 429 | `throttled` | Rate limit exceeded |
| 500 | `server_error` | Unexpected server error |

## Settings

This project uses split settings under \`config/settings/\`:
- \`base.py\` — shared settings across all environments
- \`local.py\` — local development (used by default)
- \`test.py\` — used when running the test suite
- \`production.py\` — production deployment (DEBUG is hardcoded to False)

## Running with Docker

### Prerequisites
- Docker and Docker Compose installed

### First-time setup
\`\`\`bash
cp .env.example .env
# Edit .env and fill in real values
docker compose up --build
\`\`\`

The API will be available at \`http://127.0.0.1:8000/api/v1/\`.

### Common commands

| Command | Purpose |
|---|---|
| \`.\scripts\dev.ps1 up\` | Start all services |
| \`.\scripts\dev.ps1 down\` | Stop all services |
| \`.\scripts\dev.ps1 build\` | Rebuild and start |
| \`.\scripts\dev.ps1 migrate\` | Run migrations manually (rarely needed — entrypoint does this automatically) |
| \`.\scripts\dev.ps1 superuser\` | Create a Django superuser |
| \`.\scripts\dev.ps1 logs\` | Tail web service logs |
| \`.\scripts\dev.ps1 shell\` | Open Django shell inside the container |

### Services

- **web**: Django app, served via Gunicorn (production) or \`runserver\` (dev override)
- **db**: PostgreSQL 16, with data persisted in a named volume (\`postgres_data\`)

### Data persistence

Database data is stored in a Docker named volume and survives container
restarts (\`docker compose down\` + \`docker compose up\`). To fully wipe
the database, use \`docker compose down -v\`.

### Dev vs Production

\`docker-compose.override.yml\` is automatically applied in local
development and enables:
- Live code reload via bind mount (no rebuild needed for code changes)
- Django's \`runserver\` instead of Gunicorn
- \`DEBUG=True\`

In production, only \`docker-compose.yml\` is used (no override), running
Gunicorn against an immutable image build.

## Contracts (Phase 8)

When a client accepts a proposal, a Contract is automatically created,
competing proposals are rejected, and the project is closed.

### Contract Lifecycle

\`\`\`
ACTIVE → DELIVERED → COMPLETED
      ↘ CANCELLED      ↘ DISPUTED
\`\`\`

| Action | Who | Endpoint |
|---|---|---|
| Accept proposal (creates contract) | Project owner | \`POST /api/v1/projects/{id}/proposals/{id}/accept/\` |
| Mark delivered | Freelancer | \`POST /api/v1/contracts/{id}/deliver/\` |
| Mark completed | Client | \`POST /api/v1/contracts/{id}/complete/\` |
| Raise dispute | Either party | \`POST /api/v1/contracts/{id}/dispute/\` |
| View contract | Client or freelancer | \`GET /api/v1/contracts/{id}/\` |

All state transitions are atomic, idempotent, and logged in an audit
trail (\`ContractEvent\`).

## How the Wallet System Works (Plain-Language Explanation)

Instead of storing a single "balance" number that gets directly edited,
Nexus records every financial event separately — like entries in a
bank statement, not just a single account total.

Think of it like your personal bank account: your bank doesn't just
store "you have $500." It stores every deposit and withdrawal you've
ever made, and your balance is simply the sum of all of them. If
something looks wrong, the bank (and you) can trace back through every
transaction to find the mistake.

Nexus works the same way:
- Every credit (money coming in) and debit (money going out) is
  recorded as a permanent, unchangeable entry.
- The wallet's balance is calculated from these entries and cached for
  speed — but it can always be recalculated and verified from scratch.
- No transaction can ever be silently duplicated: each one carries a
  unique "idempotency key," so accidentally clicking "pay" twice never
  charges twice.
- The system physically cannot let a balance go negative — this is
  enforced by the database itself, not just application code.


## Background Tasks (Phase 10)

Nexus uses Celery with Redis as the message broker for async work
(currently: email notifications).

### Inspecting failed tasks

\`\`\`bash
# Tail worker logs (shows retries and failures)
docker compose logs -f celery_worker

# Check a specific task's status in the Django shell
from celery.result import AsyncResult
result = AsyncResult("task-id-here")
print(result.status, result.traceback)
\`\`\`

### Adding a new notification task

1. Write the task in \`apps/notifications/tasks.py\`, accepting only IDs
   (never model instances).
2. Set \`max_retries\` and use \`retry_backoff=True\`.
3. Dispatch it with \`transaction.on_commit(lambda: my_task.delay(id))\`
   if called inside a \`@transaction.atomic\` block.
4. Add an eager-mode test verifying \`django.core.mail.outbox\`.

## ⚠️ Celery Beat: Single Instance Only

Unlike Celery workers (which can be scaled horizontally), **only one
Celery Beat instance may run at a time**, in any environment. Running
multiple Beat instances causes scheduled tasks to be enqueued multiple
times, leading to duplicate work or resource waste.

If deploying to a platform with auto-scaling, ensure the Beat service is
pinned to exactly one replica (e.g. `replicas: 1` in Docker Swarm/K8s, or
a dedicated single-instance deployment separate from the scalable worker
pool).

## Phone OTP Authentication (Phase 11)

### Flow

1. `POST /api/v1/auth/otp/request/` with `{"phone_number": "+989123456789"}`
   → SMS sent (or logged to console in dev/test), 200 response.
2. `POST /api/v1/auth/otp/verify/` with `{"phone_number": "...", "code": "123456"}`
   → Returns `{"access": "...", "refresh": "...", "created": true/false}`.

### Rate Limits

| Endpoint | Limit | Scope |
|---|---|---|
| OTP request | 3/min | Per phone number |
| OTP verify | 5/min | Per phone number |
| OTP verify (service-level) | 5 attempts | Per phone number, resets on new OTP |

### Security Notes

- OTP codes are hashed (SHA-256) before storage in Redis — never stored
  or logged in plaintext.
- OTP codes expire after 5 minutes (Redis TTL).
- OTP codes are single-use — deleted immediately after successful verification.

### SMS Backend

Controlled by `SMS_BACKEND` setting: `console` (dev/test, logs to
console) or `twilio` (production, requires `TWILIO_*` env vars).

## Scheduled Tasks (Celery Beat)

| Task | Schedule | Purpose |
|---|---|---|
| `close_stale_open_projects` | Daily at 03:00 | Closes OPEN projects with no activity for 30+ days |
| `purge_expired_otps` | Hourly | No-op (Redis TTL handles this); reserved for future metrics |

⚠️ **Only one Celery Beat instance may run at a time** — see warning above.