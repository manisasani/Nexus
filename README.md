# Nexus

A professional, scalable freelance marketplace backend built with Django and Django REST Framework, featuring escrow-based payments, ticketing, real-time chat, and background task processing.

## Tech Stack

- **Language:** Python 3.12
- **Framework:** Django + Django REST Framework
- **Database:** PostgreSQL (planned)
- **Cache/Broker:** Redis (planned)
- **Task Queue:** Celery + Celery Beat (planned)
- **Containerization:** Docker + Docker Compose (planned)
- **Monitoring:** Sentry (planned)

## Project Status

🚧 **Work in progress** — currently in early development (Phase 1: project foundation).

## Getting Started

### Prerequisites

- Python 3.12
- pip

### Setup

1. Clone the repository:
```bash
   git clone <your-repo-url>
   cd Nexus
```

2. Create and activate a virtual environment:
```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate  # macOS/Linux
```

3. Install dependencies:
```bash
   pip install -r requirements.txt
```

4. Run migrations:
```bash
   python manage.py migrate
```

5. Start the development server:
```bash
   python manage.py runserver
```

6. Visit `http://127.0.0.1:8000` in your browser.

## License

This project is for portfolio purposes.