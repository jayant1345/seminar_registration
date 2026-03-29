# SeminarHub — Seminar Registration System

A production-ready web application for managing seminar registrations, built with Python (Flask), SQLite, and Bootstrap 5.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Architecture & Logic](#architecture--logic)
- [Database Design](#database-design)
- [API Reference](#api-reference)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Admin Panel](#admin-panel)
- [Email Configuration](#email-configuration)
- [Sample Data](#sample-data)
- [Tech Stack](#tech-stack)

---

## Overview

SeminarHub is a full-stack seminar registration system that allows participants to register for seminars online and provides administrators with tools to manage, search, filter, and export registration data. Each registered participant receives a unique Registration ID and a QR code for venue check-in.

---

## Features

### Public (Participant-facing)
| Feature | Description |
|---|---|
| Registration Form | Collects name, email, phone, organization, and seminar selection |
| Server-side Validation | Regex-based email and phone validation, required field checks |
| Client-side Validation | Bootstrap 5 HTML5 form validation with custom JS |
| Duplicate Prevention | Blocks re-registration by the same email or phone number |
| Unique Registration ID | Auto-generated in format `SEM-YYYY-XXXXXX` using UUID |
| QR Code Generation | PNG QR code encoding reg ID, name, and seminar — saved and displayed |
| Email Confirmation | HTML confirmation email sent via Flask-Mail (SMTP) |
| Success Page | Displays full registration details, QR code, and print option |
| Flash Messages | Auto-dismissing success/warning/error banners |
| Responsive UI | Bootstrap 5, mobile-friendly layout |

### Admin Panel
| Feature | Description |
|---|---|
| Login / Logout | Session-based password authentication |
| Dashboard | Total registrations count + per-seminar bar chart (progress bars) |
| Registrations Table | Paginated list (20 per page) with all participant details |
| Search | Live filter by name, email, phone, registration ID, or organization |
| Seminar Filter | Dropdown to view registrations for a specific seminar |
| CSV Export | One-click download of all registrations as `.csv` |
| Excel Export | Styled `.xlsx` export with auto-sized columns via openpyxl |
| Delete Record | Remove individual registrations with confirmation prompt |

### REST API (Bonus)
| Endpoint | Description |
|---|---|
| `GET /api/v1/registrations` | Paginated list of all registrations (JSON) |
| `GET /api/v1/registrations/<reg_id>` | Single registration lookup by ID |
| `GET /api/v1/stats` | Total count + breakdown per seminar |

---

## Project Structure

```
seminar_1/
├── app/
│   ├── __init__.py          # Application factory — creates Flask app, inits extensions
│   ├── models.py            # SQLAlchemy ORM model: Participant
│   ├── utils.py             # Helper functions: ID generation, QR code creation
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py          # Public routes: /, /register, /success/<reg_id>
│   │   ├── admin.py         # Admin routes: login, dashboard, registrations, export, delete
│   │   └── api.py           # REST API routes: /api/v1/...
│   ├── templates/
│   │   ├── base.html        # Base layout: navbar, flash messages, footer
│   │   ├── index.html       # Home page with hero section and seminar cards
│   │   ├── register.html    # Registration form
│   │   ├── success.html     # Post-registration confirmation page
│   │   ├── admin/
│   │   │   ├── login.html       # Admin login form
│   │   │   ├── dashboard.html   # Stats dashboard
│   │   │   └── registrations.html  # Searchable paginated registrations table
│   │   └── email/
│   │       └── confirmation.html   # HTML email template
│   └── static/
│       ├── css/style.css    # Custom styles: hero gradient, animations, print styles
│       └── js/main.js       # Client validation, auto-dismiss alerts, URL pre-select
├── config.py                # Config classes: DevelopmentConfig, ProductionConfig
├── run.py                   # Entry point + Flask CLI commands (init-db, seed-db)
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variable template
```

---

## Architecture & Logic

### Application Factory Pattern
`app/__init__.py` uses Flask's application factory (`create_app()`), which:
1. Loads configuration from `config.py` based on `FLASK_ENV`
2. Initializes extensions: `SQLAlchemy`, `Flask-Mail`
3. Registers three Blueprints: `main`, `admin`, `api`
4. Sets up rotating file logging for production

This pattern makes the app testable and configurable without global state.

### Registration Flow

```
User submits form
       │
       ▼
Server-side validation
  ├─ Name length, email regex, phone regex
  ├─ Required fields check
  └─ Duplicate email / phone check (DB query)
       │
       ▼
Generate unique Registration ID  ← uuid4 hex + year
       │
       ▼
Generate & save QR code PNG  ← qrcode + Pillow
       │
       ▼
Insert Participant record into SQLite
       │
       ▼
Send HTML confirmation email  ← Flask-Mail (non-blocking failure)
       │
       ▼
Redirect to /success/<reg_id>
```

### Admin Authentication
- Session-based: `session['admin_logged_in'] = True` on correct password
- `@admin_bp.before_request` guard redirects unauthenticated requests to login
- Password configurable via `ADMIN_PASSWORD` environment variable

### Duplicate Prevention
Two separate unique constraints in the DB (`email`, `phone`) plus pre-check queries before insert prevent any duplicate registrations. The form re-renders with a warning flash if a duplicate is detected.

### QR Code
- Generated using the `qrcode` library with `Pillow` as the image backend
- Saved as a PNG to `app/static/qrcodes/<REG_ID>.png`
- Also returned as a base64-encoded string for inline `<img>` display without a separate HTTP request

### Export Logic
- **CSV**: Uses Python's built-in `csv` module, streamed as a `Response` with `text/csv` MIME type
- **Excel**: Uses `openpyxl` to create a styled workbook with bold blue headers and auto-sized columns, streamed as a `BytesIO` buffer

---

## Database Design

### Table: `participants`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY | Auto-increment internal ID |
| `registration_id` | VARCHAR(20) | UNIQUE, NOT NULL, INDEX | e.g. `SEM-2024-A1B2C3` |
| `name` | VARCHAR(100) | NOT NULL | Full name |
| `email` | VARCHAR(120) | UNIQUE, NOT NULL, INDEX | Lowercase email |
| `phone` | VARCHAR(20) | UNIQUE, NOT NULL | Phone number |
| `organization` | VARCHAR(150) | NOT NULL | College or company |
| `seminar` | VARCHAR(200) | NOT NULL | Selected seminar name |
| `timestamp` | DATETIME | NOT NULL, DEFAULT utcnow | Registration time (UTC) |
| `qr_code_path` | VARCHAR(255) | NULLABLE | Relative path to QR PNG |

The database file is created automatically at `instance/seminar.db` on first run.

---

## API Reference

### `GET /api/v1/registrations`
Returns paginated registrations.

**Query params:** `page` (default: 1), `per_page` (default: 20, max: 100)

```json
{
  "total": 42,
  "page": 1,
  "pages": 3,
  "per_page": 20,
  "registrations": [
    {
      "id": 1,
      "registration_id": "SEM-2024-A1B2C3",
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "phone": "+1-555-0101",
      "organization": "MIT",
      "seminar": "AI & Machine Learning Fundamentals",
      "registered_at": "2024-11-01T10:30:00"
    }
  ]
}
```

### `GET /api/v1/registrations/<reg_id>`
Returns a single registration by Registration ID.

### `GET /api/v1/stats`
Returns total count and per-seminar breakdown.

```json
{
  "total_registrations": 42,
  "by_seminar": {
    "AI & Machine Learning Fundamentals": 12,
    "Web Development with Python": 8,
    "Data Science & Analytics": 7
  }
}
```

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/jayant1345/seminar_registration.git
cd seminar_registration

# 2. Create and activate virtual environment
py -3.11 -m venv .venv311
# Windows:
.venv311\Scripts\activate
# macOS/Linux:
source .venv311/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your settings

# 5. Run the app (DB is auto-created on first run)
python run.py
```

Visit `http://127.0.0.1:8001`

---

## Configuration

All settings are in `config.py` and can be overridden via a `.env` file:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-...` | Flask session secret — **change in production** |
| `DATABASE_URL` | `sqlite:///seminar.db` | SQLAlchemy DB URI (use `mysql://...` for MySQL) |
| `MAIL_SERVER` | `smtp.gmail.com` | SMTP server hostname |
| `MAIL_PORT` | `587` | SMTP port (TLS) |
| `MAIL_USERNAME` | — | SMTP login username |
| `MAIL_PASSWORD` | — | SMTP login password / App password |
| `MAIL_DEFAULT_SENDER` | `noreply@seminar.com` | From address for emails |
| `ADMIN_PASSWORD` | `admin123` | Admin panel password |
| `FLASK_ENV` | `default` | `development` or `production` |

---

## Running the App

```bash
# Development (debug mode, port 8001)
python run.py

# Initialize DB manually (optional — auto-runs on startup)
flask --app run init-db

# Seed sample data (8 test registrations)
flask --app run seed-db
```

---

## Admin Panel

1. Navigate to `http://127.0.0.1:8001/admin`
2. Enter the admin password (default: `admin123`)
3. Available actions:
   - **Dashboard** — view stats and recent registrations
   - **All Registrations** — search, filter, paginate
   - **Export CSV / Excel** — download full dataset
   - **Delete** — remove a registration record

---

## Email Configuration

To enable confirmation emails, use a Gmail account with an **App Password**:

1. Enable 2FA on your Google account
2. Generate an App Password at `myaccount.google.com/apppasswords`
3. Set in `.env`:
   ```
   MAIL_USERNAME=you@gmail.com
   MAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
   MAIL_DEFAULT_SENDER=you@gmail.com
   ```

Email failures are logged as warnings and do **not** block registration.

---

## Sample Data

Run the seed command to populate 8 sample registrations for testing:

```bash
flask --app run seed-db
```

Sample participants span all 6 seminars across MIT, Stanford, Google, Harvard, Amazon, UC Berkeley, Microsoft, and UCLA.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.0 |
| ORM | Flask-SQLAlchemy 3.1 (SQLAlchemy 2.0) |
| Database | SQLite (dev) / MySQL-compatible (prod) |
| Email | Flask-Mail 0.10 |
| QR Code | qrcode 7.4 + Pillow 10.3 |
| Excel Export | openpyxl 3.1 |
| Frontend | Bootstrap 5.3, Bootstrap Icons |
| Env Config | python-dotenv |

---

## License

MIT License. Free to use and modify.
