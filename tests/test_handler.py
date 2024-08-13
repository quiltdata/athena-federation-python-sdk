from .handler import lambda_handler


def test_handler():
    # This is a simple test that checks if the lambda handler can be called
    # without throwing an exception.
    lambda_handler(
        {
            "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab",
        },
        {},
    )
    assert True


def test_ping():
    result = lambda_handler(
        {
            "@type": "PingRequest",
            "catalogName": "athena_python_sdk",
            "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab",
            "sourceType": "athena_python_sdk",
            "capabilities": 23,
        },
        {},
    )
    assert result


def test_schemas():
    lambda_handler(
        {
            "@type": "ListSchemasRequest",
            "catalogName": "athena_python_sdk",
            "schemas": ["sampledb"],
            "requestType": "LIST_SCHEMAS",
        },
        {},
    )
    assert True
