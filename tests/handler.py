import json
import os

from athena_federation.lambda_handler import AthenaLambdaHandler
from .sample_data_source import SampleDataSource

# This needs to be a valid bucket that the Lambda function role has access to
spill_bucket = os.environ.get("SPILL_BUCKET", "quilt-example")

example_handler = AthenaLambdaHandler(
    data_source=SampleDataSource(), spill_bucket=spill_bucket
)


def lambda_handler(event, context):
    # For debugging purposes, we print both the event and the response :)
    print(json.dumps(event))
    response = example_handler.process_event(event)
    print(json.dumps(response))

    return response
