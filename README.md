# Nexus

A modern Freelance Marketplace Backend built with Django and Django REST Framework.

---

## About

Nexus is a backend project for a freelance marketplace where clients can post projects and freelancers can submit proposals.

This project is being developed step by step with production-ready architecture and modern backend practices.

Current status: **Phase 1 completed**.

---

## Tech Stack

* Python 3.12
* Django
* Django REST Framework (DRF)
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

```
http://127.0.0.1:8000/api/v1/health/
```

Expected response

```json
{
    "status": "ok",
    "service": "Nexus"
}
```

---

## Django Admin

```
http://127.0.0.1:8000/admin/
```

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

---

## Project Structure

```
apps/
    accounts/
core/
config/
requirements/
http/
```

---

## Development Roadmap

### ✅ Phase 1

* Project foundation
* Custom User
* Profiles
* Admin configuration
* Health Check API

### 🚧 Phase 2

* Project CRUD
* Proposal system
* Object permissions
* Filtering
* Pagination

---

## License

This project is being developed for educational and portfolio purposes.
