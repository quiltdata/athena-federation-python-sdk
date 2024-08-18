# adapted from https://dev.to/farcellier/package-a-poetry-project-in-a-docker-container-for-production-3b4m
# and  https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0
FROM amazon/aws-lambda-python:3.12 AS build

# Get ready to build
RUN pip install --no-cache-dir poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

FROM amazon/aws-lambda-python:3.12 AS lambda
RUN pip install --no-cache-dir poetry==1.8.3
COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
COPY athena_federation ./athena_federation
COPY example/ ./example
RUN touch ./example/handler.py
RUN ls -R ./

# Only needed if you, e.g., install a script
# RUN poetry install --without dev 

CMD [ "example.handler.sample_handler" ]
