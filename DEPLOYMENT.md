# CI/CD and public Swagger on Ubuntu

On the Ubuntu VPS, Swagger UI is available directly at
`http://5.35.45.102/`.

## Local FastAPI block with MailHog

```bash
docker compose up --build
```

- Swagger: `http://localhost:8001/`
- MailHog inbox: `http://localhost:8025`
- Put test images into the local `media` directory and pass their relative path
  to `POST /api/v1/analyze_doc`.

## Pipeline

For every push and pull request to `main`, GitHub Actions installs dependencies,
runs tests with coverage, builds the Docker image, and smoke-tests `/health` and
Swagger. After a successful check of a push to `main`, the `deploy` job connects
to the Ubuntu VPS, updates `/opt/fastapi_ocr` with `git pull --ff-only`, rebuilds
the production Compose stack, and verifies the deployed `/health` endpoint.

Create a GitHub environment named `production` and add these environment secrets:

- `VPS_HOST`: the VPS hostname or IP address (for example `5.35.45.102`)
- `VPS_USER`: the SSH user that owns `/opt/fastapi_ocr` and can run Docker
- `VPS_SSH_KEY`: the private SSH key used by GitHub Actions
- `VPS_KNOWN_HOSTS`: the trusted host-key line produced locally with
  `ssh-keyscan -H <VPS_HOST>` after its fingerprint has been verified

The corresponding public key must be present in the VPS user's
`~/.ssh/authorized_keys`. Deployment deliberately uses `git pull --ff-only`:
if the server checkout has conflicting or divergent changes, the job stops
instead of overwriting them.

## First deployment to Ubuntu

```bash
git clone https://github.com/shorohartem/fastapi_git.git /opt/fastapi_ocr
cd /opt/fastapi_ocr
docker compose -f docker-compose.prod.yml up -d --build
```

Check the deployment with `docker compose -f docker-compose.prod.yml ps` and
`curl http://localhost/health`.

Locally, `docker-compose.yml` uses MailHog as the test SMTP server. Open its inbox
at `http://localhost:8025`; no real email is sent. MailHog uses `SMTP_HOST=mailhog`,
`SMTP_PORT=1025`, and `SMTP_USE_TLS=false`.

For a real SMTP provider, provide `SMTP_HOST`, `SMTP_PORT`,
`SMTP_USER`, `SMTP_PASSWORD`, `NOTIFICATION_EMAIL`, and the corresponding
`SMTP_USE_TLS` value. Also provide `DJANGO_BASE_URL` and `DJANGO_MEDIA_URL`;
`DJANGO_MEDIA_URL` must point to a URL from which the worker can download Django
media files.

Both POST APIs return HTTP 202 and a Celery `task_id`. Poll
`GET /api/v1/tasks/{task_id}` to retrieve the result or error.
