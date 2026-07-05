# Nexus

A modern Freelance Marketplace Backend built with Django and Django REST Framework.

---

## About

Nexus is a backend project for a freelance marketplace where clients can post projects and freelancers can submit proposals.

This project is being developed step by step with production-ready architecture and modern backend practices.

Current status: **Phase 2 in progress (Project & Proposal API complete)**.

---

## Tech Stack

* Python 3.12
* Django
* Django REST Framework (DRF)
* django-filter
* SQLite (temporary, PostgreSQL will be introduced in Phase 5)

---

## Project Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Nexus
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements/base.txt
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

---

## Health Check

Endpoint

```text
GET /api/v1/health/
```

Example:
http://127.0.0.1:8000/api/v1/health/
Expected response

```json
{
    "status": "ok",
    "service": "Nexus"
}
```

---

## Django Admin

http://127.0.0.1:8000/admin/
Login using your superuser credentials.

---

## Current Features

* Custom User Model
* Role-based users (Client / Freelancer)
* Client Profile
* Freelancer Profile
* Django Admin configuration
* Health Check API
* REST API foundation
* API Versioning (/api/v1/)
* Project CRUD with role-based permissions
* Proposal system with marketplace business rules
* Object-level and queryset-level permission scoping
* Filtering and pagination on list endpoints

---

## API Endpoints (Phase 2)

### Authentication

Phase 2 currently uses **Session Authentication** (and Basic Authentication for local testing) since JWT authentication has not been implemented yet. This is temporary — JWT will replace this in a later phase, and no other application logic (views, permissions, serializers) will need to change when that happens.

To authenticate manually while testing:
* Log in via `/admin/` or `/api-auth/login/` to get a session cookie, **or**
* Use HTTP Basic Auth (`Authorization: Basic <email> <password>`) for quick testing with tools like VS Code REST Client.

### Projects

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET | `/api/v1/projects/` | Authenticated | List OPEN projects (paginated, filterable) |
| GET | `/api/v1/projects/mine/` | Authenticated (owner) | List all of the caller's own projects, any status |
| POST | `/api/v1/projects/` | CLIENT only | Create a new project (forced to DRAFT status) |
| GET | `/api/v1/projects/{id}/` | Owner, or anyone if OPEN | Retrieve project detail |
| PATCH | `/api/v1/projects/{id}/` | Owner only | Update project fields or status |
| DELETE | `/api/v1/projects/{id}/` | Owner only | Delete project (DRAFT only) |

### Proposals (nested under project)

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET | `/api/v1/projects/{project_id}/proposals/` | Owner sees all, freelancer sees own | List proposals on a project (paginated) |
| POST | `/api/v1/projects/{project_id}/proposals/` | FREELANCER only | Submit a proposal on an OPEN project |
| GET | `/api/v1/projects/{project_id}/proposals/{id}/` | Owner or proposal's freelancer | Retrieve proposal detail |
| PATCH | `/api/v1/projects/{project_id}/proposals/{id}/` | Freelancer, own PENDING proposal only | Edit cover letter / bid amount |
| DELETE | `/api/v1/projects/{project_id}/proposals/{id}/` | Freelancer, own PENDING proposal only | Delete a proposal |
| POST | `/api/v1/projects/{project_id}/proposals/{id}/accept/` | Project owner (client) only | Accept a pending proposal |
| POST | `/api/v1/projects/{project_id}/proposals/{id}/reject/` | Project owner (client) only | Reject a pending proposal |

---

## Filtering

The project list endpoint supports the following query parameters:

| Param | Type | Example | Description |
|---|---|---|---|
| `status` | string | `?status=OPEN` | Exact match on project status |
| `budget_min` | number | `?budget_min=100` | Minimum budget (inclusive) |
| `budget_max` | number | `?budget_max=5000` | Maximum budget (inclusive) |

Example combined query:

GET /api/v1/projects/?status=OPEN&budget_min=100&budget_max=5000

---

## Pagination

All list endpoints use DRF's `PageNumberPagination` with a page size of **10**.

Example response shape:

```json
{
  "count": 45,
  "next": "http://127.0.0.1:8000/api/v1/projects/?page=2",
  "previous": null,
  "results": [
    {
      "id": 7,
      "title": "Build a landing page",
      "status": "OPEN",
      "owner": 3,
      "owner_email": "client1@example.com",
      "budget": "500.00",
      "deadline": "2026-09-01",
      "created_at": "2026-07-05T14:39:59Z",
      "updated_at": "2026-07-05T14:39:59Z"
    }
  ]
}
```

---

## API Demo / Manual Testing

A full end-to-end HTTP demo (happy path + failure path) is available at:

http/.http
Open it in VS Code with the **REST Client** extension to run each request in sequence — including project creation, status transitions, proposal submission, accept/reject, and permission/validation failure cases (403, 404, duplicate proposal handling, etc.).

---

## Project Structure

apps/
accounts/
projects/
core/
config/
requirements/
http/

---

## Development Roadmap

### ✅ Phase 1

* Project foundation
* Custom User
* Profiles
* Admin configuration
* Health Check API

### 🚧 Phase 2

* [x] Project model + admin
* [x] Proposal model + admin + DB uniqueness constraint
* [x] Project serializers + validation
* [x] Project CRUD API with object permissions
* [x] Filtering and pagination on project list
* [x] Proposal serializers + marketplace validation
* [x] Nested proposal endpoints with role permissions
* [x] End-to-end API demo (`.http` file)
* [ ] Automated tests (Phase 7)
* [ ] JWT Authentication (later phase — Session/Basic Auth used temporarily)

---

## Known Technical Debt

See [`TECH_DEBT.md`](./TECH_DEBT.md) for tracked items, including:
* N+1 queries on project/proposal owner and freelancer fields (not yet optimized)
* ACCEPTED proposal status is currently cosmetic — no contract/payment logic behind it yet
* Authentication is temporary (Session/Basic) pending JWT implementation
* No automated test suite yet

---

## License

This project is being developed for educational and portfolio purposes.

