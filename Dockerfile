FROM python:3.8-slim AS build

# Set our workdir
WORKDIR /app

# Get ready to build
RUN pip install --no-cache-dir poetry==1.8.3

# Now copy the app over and build a wheel
COPY src /app/src/
COPY pyproject.toml /app/
RUN poetry install

## Now use the compiled wheel in our lambda function
FROM amazon/aws-lambda-python:3.12.0 AS lambda

ENV TARGET_BUCKET=replace_me

COPY --from=build /app/dist/athena_federation-*-py3-none-any.whl /
RUN pip install --no-cache-dir /athena_federation-*-py3-none-any.whl

WORKDIR /app
COPY example/ ./
RUN ls ./

CMD [ "handler.lambda_handler" ]
