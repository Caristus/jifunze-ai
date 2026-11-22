# Installation
Requirements: Python 3.12.
    python -m venv venv
    venv\Scripts\activate        # Windows
    pip install -r requirements.txt
    copy .env.example .env        # then edit values
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver
Production (Docker): `docker compose up --build` then open http://localhost:8000.
