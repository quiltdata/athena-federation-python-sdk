import athena_federation


def test_import():
    assert athena_federation.AthenaLambdaHandler
    assert athena_federation.AthenaFederationSDK
    assert athena_federation.AthenaDataSource
    assert athena_federation.AthenaFederationSDK
    assert athena_federation.AthenaSDKUtils
    assert athena_federation.models.PingResponse
    assert athena_federation.models.ListSchemasResponse
