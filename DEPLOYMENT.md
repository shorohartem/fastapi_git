# CI/CD and public Swagger

After deployment, Swagger UI is available at
`https://<service-name>.onrender.com/docs`.

## Local FastAPI block with MailHog

```bash
docker compose up --build
```

- Swagger: `http://localhost:8001/docs`
- MailHog inbox: `http://localhost:8025`
- Put test images into the local `media` directory and pass their relative path
  to `POST /api/v1/analyze_doc`.

## Pipeline

For every push and pull request to `main`, GitHub Actions installs dependencies,
runs tests with coverage, builds the Docker image, and smoke-tests `/health` and
`/docs`. The `render.yaml` blueprint configures Render to deploy `main` only after
the GitHub checks pass. It also provisions a Redis-compatible Render Key Value
queue and starts a Celery worker alongside the demo web service.

## First deployment

1. Push the repository to GitHub using the `main` branch.
2. Sign in at https://dashboard.render.com and connect the GitHub account.
3. Choose **New > Blueprint**, select this repository, and apply `render.yaml`.
4. Wait for GitHub CI and the Render deployment to complete.
5. Open the service URL shown by Render and append `/docs`.

Locally, `docker-compose.yml` uses MailHog as the test SMTP server. Open its inbox
at `http://localhost:8025`; no real email is sent. MailHog uses `SMTP_HOST=mailhog`,
`SMTP_PORT=1025`, and `SMTP_USE_TLS=false`.

For a real SMTP provider during Blueprint setup, provide `SMTP_HOST`, `SMTP_PORT`,
`SMTP_USER`, `SMTP_PASSWORD`, `NOTIFICATION_EMAIL`, and the corresponding
`SMTP_USE_TLS` value. Also provide `DJANGO_BASE_URL` and `DJANGO_MEDIA_URL`;
`DJANGO_MEDIA_URL` must point to a URL from which the worker can download Django
media files.

Both POST APIs return HTTP 202 and a Celery `task_id`. Poll
`GET /api/v1/tasks/{task_id}` to retrieve the result or error.
