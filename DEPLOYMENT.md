# CI/CD and public Swagger

After deployment, Swagger UI is available at
`https://<service-name>.onrender.com/docs`.

## Pipeline

For every push and pull request to `main`, GitHub Actions installs dependencies,
runs tests with coverage, builds the Docker image, and smoke-tests `/health` and
`/docs`. The `render.yaml` blueprint configures Render to deploy `main` only after
the GitHub checks pass.

## First deployment

1. Push the repository to GitHub using the `main` branch.
2. Sign in at https://dashboard.render.com and connect the GitHub account.
3. Choose **New > Blueprint**, select this repository, and apply `render.yaml`.
4. Wait for GitHub CI and the Render deployment to complete.
5. Open the service URL shown by Render and append `/docs`.

Add SMTP, Redis/Celery, and Django integration settings in Render Dashboard before
using those integrations. Swagger and the health endpoint work without them.
