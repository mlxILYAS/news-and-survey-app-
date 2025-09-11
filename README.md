

# Django News & Survey Portal

A Django-based news and surveys application that lets authenticated users manage articles and run surveys with results and basic analytics. The project uses SQLite by default and ships with templates for core pages and a management command for cleaning up article slugs.

Key modules:
- Core project: [`manage.py`](manage.py), [`project/settings.py`](project/settings.py), [`project/urls.py`](project/urls.py)
- App: [`news/models.py`](news/models.py), [`news/views.py`](news/views.py), [`news/forms.py`](news/forms.py), [`news/urls.py`](news/urls.py), [`news/signals.py`](news/signals.py)
- Templates: [`templates/base.html`](templates/base.html), [`templates/home.html`](templates/home.html), article and survey templates
- Auth templates: [`templates/registration/login.html`](templates/registration/login.html), [`templates/registration/profile.html`](templates/registration/profile.html)
- Media storage: [`media/`](media/)
- DB: [`db.sqlite3`](db.sqlite3)
- Management command: [`news/management/commands/fix_article_slugs.py`](news/management/commands/fix_article_slugs.py)

## Features

- Articles
  - Create, view, edit, and delete articles with images and excerpts
  - Slug generation and a repair command for existing records
  - Tagging and categorization support (as implemented in migrations)
  - View counting for engagement tracking
- Surveys
  - Create surveys with questions
  - Collect responses and view results
- User & Admin
  - Login and basic profile templates
  - Superuser dashboard template
  - Django admin enabled
- Media
  - Local media storage for uploaded article images under [`media/articles/`](media/articles/)

## Tech Stack

- Python 3.13+ (project was run with a Python 3.13 build, as indicated by compiled artifacts)
- Django 4/5.x (typical; install the latest stable compatible with Python 3.13)
- SQLite (default dev database)

## Project Layout (selected)

- Core
  - [`manage.py`](manage.py)
  - [`project/settings.py`](project/settings.py)
  - [`project/urls.py`](project/urls.py)
- App
  - [`news/models.py`](news/models.py)
  - [`news/views.py`](news/views.py)
  - [`news/forms.py`](news/forms.py)
  - [`news/urls.py`](news/urls.py)
  - [`news/signals.py`](news/signals.py)
  - [`news/management/commands/fix_article_slugs.py`](news/management/commands/fix_article_slugs.py)
- Templates
  - [`templates/base.html`](templates/base.html)
  - [`templates/home.html`](templates/home.html)
  - Article:
    - [`templates/article_create.html`](templates/article_create.html)
    - [`templates/article_detail.html`](templates/article_detail.html)
    - [`templates/article_confirm_delete.html`](templates/article_confirm_delete.html)
  - Survey:
    - [`templates/survey_create.html`](templates/survey_create.html)
    - [`templates/survey_detail.html`](templates/survey_detail.html)
    - [`templates/survey_edit.html`](templates/survey_edit.html)
    - [`templates/survey_list.html`](templates/survey_list.html)
    - [`templates/survey_results.html`](templates/survey_results.html)
    - [`templates/survey_submitted.html`](templates/survey_submitted.html)
    - [`templates/survey_confirm_delete.html`](templates/survey_confirm_delete.html)
  - Admin/Superuser:
    - [`templates/superuser_dashboard.html`](templates/superuser_dashboard.html)
    - [`templates/user_management.html`](templates/user_management.html)
  - Auth:
    - [`templates/registration/login.html`](templates/registration/login.html)
    - [`templates/registration/profile.html`](templates/registration/profile.html)
- Data
  - [`db.sqlite3`](db.sqlite3)
  - [`media/`](media/)

## Quick Start

1) Clone and setup environment
- Create a Python 3.13 virtual environment and activate it.

2) Install dependencies
- If you have a requirements file, install it:
  - pip install -r requirements.txt
- Otherwise, install Django and Pillow (for images):
  - pip install "Django&gt;=4.2" Pillow

3) Create and apply migrations
- python manage.py makemigrations
- python manage.py migrate

4) Create a superuser
- python manage.py createsuperuser

5) Run the development server
- python manage.py runserver

6) Access the app
- App: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Configuration

- Django settings: [`project/settings.py`](project/settings.py)
- Common environment variables:
  - DJANGO_SECRET_KEY
  - DJANGO_DEBUG (True/False)
  - DJANGO_ALLOWED_HOSTS (comma-separated)
- Media and static
  - MEDIA_ROOT defaults to the local [`media/`](media/) directory
  - In development, media is typically served by adding proper URL patterns; see [`project/urls.py`](project/urls.py)
  - For production, serve static and media with your web server or CDN

## URLs

Top-level routing is configured in:
- [`project/urls.py`](project/urls.py) – includes app URLs
- [`news/urls.py`](news/urls.py) – app-specific endpoints

Typical pages based on available templates:
- Home / articles list: uses [`templates/home.html`](templates/home.html)
- Article CRUD:
  - Create: [`templates/article_create.html`](templates/article_create.html)
  - Detail: [`templates/article_detail.html`](templates/article_detail.html)
  - Delete confirm: [`templates/article_confirm_delete.html`](templates/article_confirm_delete.html)
- Survey:
  - Create: [`templates/survey_create.html`](templates/survey_create.html)
  - List: [`templates/survey_list.html`](templates/survey_list.html)
  - Detail: [`templates/survey_detail.html`](templates/survey_detail.html)
  - Edit: [`templates/survey_edit.html`](templates/survey_edit.html)
  - Results: [`templates/survey_results.html`](templates/survey_results.html)
  - Submitted: [`templates/survey_submitted.html`](templates/survey_submitted.html)

Note: Exact URL paths are defined in [`news/urls.py`](news/urls.py).

## Management Commands

- Fix/normalize article slugs:
  - python manage.py fix_article_slugs
  - Source: [`news/management/commands/fix_article_slugs.py`](news/management/commands/fix_article_slugs.py)

## Data Model Overview

The app revolves around Articles and Surveys:
- Article
  - Title, body/content, excerpt, image, slug, views, category, tags
- Survey
  - One survey has multiple questions
  - Users submit responses; results page aggregates them

For exact fields and relations, see:
- Models: [`news/models.py`](news/models.py)
- Migrations: [`news/migrations/`](news/migrations/)

## Signals

Project uses Django signals (e.g., for slugs or side effects). See:
- [`news/signals.py`](news/signals.py)

## Authentication

Templates provided for:
- Login: [`templates/registration/login.html`](templates/registration/login.html)
- Profile: [`templates/registration/profile.html`](templates/registration/profile.html)

Protect views as needed (e.g., login_required) in [`news/views.py`](news/views.py).

## Development Tips

- Use DEBUG=True only in development
- Use a strong SECRET_KEY in production
- Configure ALLOWED_HOSTS properly
- Run tests (if/when added):
  - python manage.py test

## Deployment Notes

- Use a robust database in production (e.g., Postgres)
- Configure static and media file serving
- Apply migrations on deploy
- Create an admin superuser
- Set up a process manager (e.g., systemd, supervisord) and reverse proxy (e.g., Nginx)

## Troubleshooting

- If article URLs 404 due to missing/old slugs, run:
  - python manage.py fix_article_slugs
- If images don’t render, check MEDIA_URL and MEDIA_ROOT in [`project/settings.py`](project/settings.py) and related URL patterns in [`project/urls.py`](project/urls.py)

## License

Specify your license here (e.g., MIT). If you add a license file, place it at the project root as [`LICENSE`](LICENSE).
