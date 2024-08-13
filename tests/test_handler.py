from .handler import lambda_handler


def test_lambda_handler():
    # This is a simple test that checks if the lambda handler can be called
    # without throwing an exception.
    lambda_handler({}, {})
    assert True

