from .handler import lambda_handler
import pytest

TABLE_DEF = {"tableName": "demo", "schemaName": "sampledb"}


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


def test_PingRequest():
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
    assert result["@type"] == "PingResponse"


def test_ListSchemasRequest():
    result = lambda_handler(
        {
            "@type": "ListSchemasRequest",
            "catalogName": "athena_python_sdk",
            "schemas": ["sampledb"],
            "requestType": "LIST_SCHEMAS",
        },
        {},
    )
    assert result
    assert result["@type"] == "ListSchemasResponse"


def test_ListTablesRequest():
    result = lambda_handler(
        {
            "@type": "ListTablesRequest",
            "catalogName": "athena_python_sdk",
            "schemaName": "sampledb",
            "tables": ["demo"],
            "requestType": "LIST_TABLES",
        },
        {},
    )
    assert result
    assert result["@type"] == "ListTablesResponse"
    assert result["requestType"] == "LIST_TABLES"
    assert "tables" in result
    assert len(result["tables"]) == 1
    assert result["tables"][0] == TABLE_DEF


def test_GetTableRequest():
    result = lambda_handler(
        {
            "@type": "GetTableRequest",
            "catalogName": "athena_python_sdk",
            "tableName": TABLE_DEF,
        },
        {},
    )
    assert result
    assert result["@type"] == "GetTableResponse"
    assert result["requestType"] == "GET_TABLE"


def test_GetTableLayoutRequest():
    result = lambda_handler(
        {
            "@type": "GetTableLayoutRequest",
            "catalogName": "athena_python_sdk",
            "tableName": TABLE_DEF,
        },
        {},
    )
    assert result
    assert result["@type"] == "GetTableLayoutResponse"
    assert result["requestType"] == "GET_TABLE_LAYOUT"
    assert "aId" in result["partitions"]


def test_GetSplitsRequest():
    result = lambda_handler(
        {
            "@type": "GetSplitsRequest",
            "catalogName": "athena_python_sdk",
            "tableName": TABLE_DEF,
        },
        {},
    )
    assert result
    assert result["@type"] == "GetSplitsResponse"
    assert result["requestType"] == "GET_SPLITS"
    splits = result["splits"]
    assert splits
    assert len(splits) == 2
    split = splits[0]
    print("SPLIT", split)
    loc = split["spillLocation"]
    assert loc["bucket"] == "quilt-example"
    assert "athena-spill" in loc["key"]
    assert loc["directory"]
    assert split["properties"] == {'name': 'split1', 'action': 'normal'}

    split1 = splits[1]
    loc1 = split1["spillLocation"]
    assert loc1["bucket"] == "quilt-example"
    assert "athena-spill" in loc1["key"]
    assert loc1["directory"]
    assert split1["properties"] == {'name': 'split2', 'action': 'spill'}


@pytest.mark.skip
def test_ReadRecordsRequest():
    result = lambda_handler(
        {
            "@type": "ReadRecordsRequest",
            "catalogName": "athena_python_sdk",
            "schema": {
                "schema": "request_timestamp:timestamp,elb_name:string,request_ip:string"
            },
            "tableName": {"schemaName": "sampledb", "tableName": "demo"},
            "split": {
                "spillLocation": {
                    "bucket": "quilt-example",
                    "key": "athena-spill",
                    "directory": True,
                },
                "properties": {"name": "split1", "action": "normal"},
            },
        },
        {},
    )
    assert result
    assert result["@type"] == "RemoteReadRecordsResponse"
    assert result["requestType"] == "READ_RECORDS"
    assert "schema" in result
    assert "spillLocation" in result
    assert "records" in result
    assert len(result["records"]) == 2
    assert result["records"][0]
