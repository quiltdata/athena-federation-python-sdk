# adapted from https://dev.to/farcellier/package-a-poetry-project-in-a-docker-container-for-production-3b4m

FROM python:3.12.5-slim-bookworm AS build

# Get ready to build
RUN pip install --no-cache-dir poetry==1.8.3

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY athena_federation ./athena_federation

RUN poetry install --without dev --no-interaction

ENTRYPOINT ["poetry", "run", "python", "-m", "athena_federation.main"]
