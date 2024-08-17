import json
import os

from athena_federation.lambda_handler import AthenaLambdaHandler
from .sample_data_source import SampleDataSource

# This needs to be a valid bucket that the Lambda function role has access to
spill_bucket = os.environ.get("SPILL_BUCKET", "quilt-example")

print("Creating example_handler")

example_handler = AthenaLambdaHandler(
    data_source=SampleDataSource(), spill_bucket=spill_bucket
)

print("Created example_handler")


def sample_handler(event, context):
    # For debugging purposes, we print both the event and the response :)
    print("EVENT", json.dumps(event))
    response = example_handler.process_event(event)
    print("RESPONSE", json.dumps(response))

    return response
