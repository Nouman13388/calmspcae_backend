# calmspcae_backend

## Project overview

This is a Django backend project using Django 5.1, Django Channels, Django REST Framework and other common packages. The repository name is `calmspcae_backend` (project package `calmspcae_backend`).

## Purpose

- Provides REST APIs (via DRF) and WebSocket support (via Channels).
- Includes an app `my_app` with models and migrations.

## What I changed (dev-friendly)

To make local development easier without MySQL or Redis, the following changes were made to `calmspcae_backend/settings.py`:

- A `DATABASE_ENGINE` environment variable was added. Set it to `sqlite` to use a local SQLite database. By default, the app still uses MySQL when `DATABASE_ENGINE` is not `sqlite`.
- During development (when `DEBUG=True`), Channels will use the in-memory channel layer (`channels.layers.InMemoryChannelLayer`) so you don't need Redis locally.

## Quick start (Windows - PowerShell)

1. Clone the repo (if not already cloned):

   git clone <repo-url>
   cd calmspcae_backend

2. Create a Python virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies (we created a `requirements-dev.txt` that excludes `mysqlclient` for easier Windows installs):

```powershell
pip install -r requirements-dev.txt
```

If you need MySQL support later, you can install `mysqlclient` and set `DATABASE_ENGINE` to `mysql` and provide DB credentials in `.env`.

4. Configure environment variables

Create a `.env` file in the repository root (a sample is included in `.env` if present). For development using SQLite, add:

```
DATABASE_ENGINE=sqlite
SECRET_KEY=your-secret-key
IS_PRODUCTION=False
```

For production (MySQL), use:

```
DATABASE_ENGINE=mysql
DATABASE_NAME=your_db
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=your_host
DATABASE_PORT=3306
IS_PRODUCTION=True
SECRET_KEY=your-secret-key
```

5. Run migrations and start server

```powershell
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

## Notes about Channels (WebSockets)

- In development (`DEBUG=True`) the project uses the in-memory channel layer, which is not suitable for production but allows WebSocket features while developing without Redis.
- In production, ensure you have Redis running and update `CHANNEL_LAYERS` settings or set `DEBUG=False` and configure the Redis host/port as needed.

## Static files

- `STATICFILES_DIRS` points to a `static/` directory at the project root. Create that directory if you plan to serve or collect static files locally:

```powershell
New-Item -ItemType Directory -Path .\static
```

## Troubleshooting

- mysqlclient installation fails on Windows: Use `requirements-dev.txt` (it excludes `mysqlclient`) or install prebuilt wheels for your Python version. If you need MySQL locally, consider using WSL or a Docker container.
- Redis not available: development will use an in-memory channel layer. For production, install Redis and configure `CHANNEL_LAYERS` accordingly.
- Static files warning: create the `static/` folder or change `STATICFILES_DIRS` in `settings.py`.

## Project structure (top-level)

- manage.py
- requirements.txt (full dependencies)
- requirements-dev.txt (dev-friendly, excludes mysqlclient)
- calmspcae_backend/ (Django project package)
- my_app/ (application code)
- media/ (uploaded files)

## Security

- Do NOT commit real secret keys or production credentials. Keep `.env` out of version control. The repo currently expects a `.env` file for configuration via `django-environ` and `python-decouple`.

## Next steps you might want

- Add `requirements-dev.txt` to the repo (already created) and commit it.
- Update `README.md` with API endpoints and authentication details once you finalize the API surface.
- Add Docker support for reproducing the exact prod environment locally (MySQL/Redis) if needed.

If you'd like, I can:

- Commit `requirements-dev.txt` and `README.md` changes and create a small `README` PR.
- Add a `make` or PowerShell script to automate venv creation and run steps.
- Add a `CONTRIBUTING.md` with setup notes for new devs.
