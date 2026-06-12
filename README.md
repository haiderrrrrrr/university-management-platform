# University Management Platform

A Django university management system that connects academic administration, course delivery, assessments, results, payments, and role-based portals in one application.

## Live App

https://university-management-platform-mgdq.onrender.com

## Features

- Role-based access for administrators, lecturers, students, and parents
- Academic session and semester management
- Program and course catalog management
- Lecturer course allocation
- Student registration and course enrollment
- Course materials and video upload support
- Practice quizzes, examinations, progress tracking, and marking
- Assignment, attendance, quiz, midterm, and final-exam scoring
- GPA, CGPA, assessment, and result reporting
- Student and lecturer profile management
- News and campus event publishing
- Invoice records and optional payment gateway integration
- Search across academic content
- REST API endpoints protected by Django authentication
- PostgreSQL and SQLite support through Django ORM

## Role Workflows

### Administrator

Administrators manage users, programs, courses, academic sessions, semesters, lecturer allocations, news, results, and platform records. They also have access to Django administration.

### Lecturer

Lecturers view allocated courses, manage academic periods, publish course resources, create quizzes, mark completed attempts, and submit student scores.

### Student

Students view their courses, take quizzes, review progress, inspect assessment scores, access grade results, and maintain their profile.

### Parent

Parent accounts are linked to individual students and provide a read-oriented portal without academic or administrative modification privileges.

## How The Data Is Connected

1. An academic `Session` contains one or more `Semester` records.
2. A `Program` contains its related `Course` records.
3. A lecturer receives courses through `CourseAllocation` for an academic session.
4. A student account has one `Student` profile linked to a program.
5. A parent account has one `Parent` record linked to a student.
6. Student enrollment creates `TakenCourse` records connecting students and courses.
7. Each taken course stores assessment marks, totals, grades, and grade points.
8. Semester summaries are stored as `Result` records with GPA and CGPA.
9. A course can contain multiple quizzes, questions, and choices.
10. Quiz attempts are stored as `Sitting` records with answers, scores, and completion state.
11. Student payment records are stored as `Invoice` entries.

## Technology Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12, Django 4.2 |
| API | Django REST Framework |
| Application Server | Gunicorn |
| Database | PostgreSQL, Neon, SQLite |
| Frontend | Django Templates, Bootstrap, HTML, CSS, JavaScript |
| Static Files | WhiteNoise |
| Real-Time Foundation | Django Channels |
| Reports | ReportLab |
| Payments | Stripe and GoPay integration points |
| Deployment | Render |

## Project Structure

```text
.
|-- accounts/          User roles, profiles, authentication, and permissions
|-- app/               Dashboard, news, sessions, semesters, and demo seeding
|-- course/            Programs, courses, allocations, files, and enrollment
|-- coursemanagement/  Department course offering settings
|-- payments/          Invoices and payment gateway integrations
|-- quiz/              Quizzes, questions, attempts, progress, and marking
|-- result/            Assessments, grades, GPA, CGPA, and PDF reports
|-- search/            Platform search
|-- SMS/               Django project settings, URLs, ASGI, and WSGI
|-- static/            Stylesheets, scripts, fonts, and images
|-- templates/         Django templates
|-- .env.example       Environment configuration template
|-- manage.py          Django management entry point
`-- requirements.txt   Runtime dependencies
```

## Local Setup

### Windows PowerShell

```powershell
git clone https://github.com/haiderrrrrrr/university-management-platform.git
cd university-management-platform

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Linux or macOS

```bash
git clone https://github.com/haiderrrrrrr/university-management-platform.git
cd university-management-platform

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/accounts/login/`.

## Database Configuration

SQLite is used when `DATABASE_URL` is empty, making the project runnable without installing a database server.

To use PostgreSQL or Neon, set:

```env
DATABASE_URL=postgresql://username:password@hostname/database?sslmode=require
```

Then apply the schema:

```bash
python manage.py migrate
```

The real `.env` file is ignored by Git and must never be committed.

## Demo Data

Populate a connected university dataset:

```bash
python manage.py seed_demo_data
```

The command is idempotent and can be rerun without creating duplicate demo records. It creates programs, courses, users, allocations, enrollments, results, quizzes, completed attempts, news, and invoices.

Demo accounts:

| Role | Username | Password |
| --- | --- | --- |
| Lecturer | `lecturer.amina` | `Demo@12345` |
| Student | `student.ali` | `Demo@12345` |
| Parent | `parent.ali` | `Demo@12345` |

Create an administrator separately with:

```bash
python manage.py createsuperuser
```

## Environment Variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Django cryptographic signing key |
| `DEBUG` | Yes | Enables or disables development mode |
| `ALLOWED_HOSTS` | Yes | Comma-separated accepted hostnames |
| `DATABASE_URL` | No | PostgreSQL URL; empty uses SQLite |
| `USER_EMAIL` | No | SMTP email account |
| `USER_PASSWORD` | No | SMTP application password |
| `STRIPE_SECRET_KEY` | No | Stripe server credential |
| `STRIPE_PUBLISHABLE_KEY` | No | Stripe browser credential |
| `GOPAY_GOID` | No | GoPay account identifier |
| `GOPAY_CLIENT_ID` | No | GoPay client identifier |
| `GOPAY_CLIENT_SECRET` | No | GoPay client credential |

Without payment credentials, academic features remain available while external payment transactions stay disabled.

## Verification

```bash
python manage.py check
python manage.py test
```

The repository includes an idempotent demo-data command for repeatable manual verification across administrator, lecturer, student, and parent workflows.
