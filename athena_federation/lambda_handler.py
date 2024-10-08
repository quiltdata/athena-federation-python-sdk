from typing import Union
import athena_federation.models as models
from athena_federation.athena_data_source import AthenaDataSource
from athena_federation.batch_writer import BatchWriter
from athena_federation.sdk import AthenaFederationSDK
from athena_federation.utils import AthenaSDKUtils


class AthenaLambdaHandler(AthenaFederationSDK):
    def __init__(self, data_source: AthenaDataSource, spill_bucket: str) -> None:
        print(
            f'Initializing Athena data source "{data_source}", spill bucket: s3://{spill_bucket}'
        )
        self.spill_bucket = spill_bucket
        self.data_source = data_source

    def process_event(self, event):
        """
        I refactored this a bit from my version so AthenaExample could be instantiated once,
        and then events processed - but I don't really like this pattern.

        1. There is lots of unnecessary repetition (e.g. catalog_name being passed to every response).
        2. It feels weird to overwrite event every time.
        3. While functional, the `getattr` approach also seems a little wierd.
        """
        # Populate attributes needed to process the event
        self.event = event
        self.catalog_name = self.event.get("catalogName")
        request_type = self.event.get("@type") or "PingRequest"

        # TODO: As the event comes in, populate the database name, table name if provided.
        # TODO: I can also create new Request types from the event

        # Look up the request type, call it dynamically, and return the dictionary representation of it.
        # Each model returned implements `as_dict` that returns the info necessary for Athena, including
        # specific PyArrow serialization.
        request_attr = getattr(self, request_type)
        if request_attr:
            return request_attr().as_dict()
        else:
            print(f"Unknown request type: {request_type}")
            return {}

    def PingRequest(self) -> models.PingResponse:
        return models.PingResponse(
            self.catalog_name, self.event["queryId"], self.data_source.data_source_type
        )

    def ListSchemasRequest(self) -> models.ListSchemasResponse:
        database_names = self.data_source.databases()
        return models.ListSchemasResponse(self.catalog_name, database_names)

    def ListTablesRequest(self) -> models.ListTablesResponse:
        database_name = self.event.get("schemaName")
        table_names = self.data_source.tables(database_name)
        tableResponse = models.ListTablesResponse(self.catalog_name)
        for table_name in table_names:
            tableResponse.addTableDefinition(database_name, table_name)
        return tableResponse

    def GetTableRequest(self) -> models.GetTableResponse:
        database_name = self.event.get("tableName").get("schemaName")
        table_name = self.event.get("tableName").get("tableName")
        schema = self.data_source.schema(database_name, table_name)
        return models.GetTableResponse(
            self.catalog_name, database_name, table_name, schema
        )

    ## BEGIN: Placeholder methods for partition pruning/splits and spill requests
    ## Called `getPartitions(BlockWriter blockWriter, GetTableLayoutRequest request)` in Java SDK`
    def GetTableLayoutRequest(self) -> models.GetTableLayoutResponse:
        # The partition schema above was reused from CloudTrail example - we need to
        # add (also?) the schema we want to pass back in a split?
        # e.g. messageIds: pa.list_(pa.int64())
        database_name = self.event.get("tableName").get("schemaName")
        table_name = self.event.get("tableName").get("tableName")
        return models.GetTableLayoutResponse(
            self.catalog_name, database_name, table_name, None
        )

    def GetSplitsRequest(self) -> models.GetSplitsResponse:
        database_name = self.event.get("tableName").get("schemaName")
        table_name = self.event.get("tableName").get("tableName")
        data_source_splits_props = self.data_source.splits(database_name, table_name)
        if not data_source_splits_props:
            data_source_splits_props = [{}]
        splits = [
            {
                "spillLocation": AthenaSDKUtils.generate_spill_metadata(
                    self.spill_bucket, "athena-spill"
                ),
                "properties": props,
            }
            for props in data_source_splits_props
        ]
        return models.GetSplitsResponse(self.catalog_name, splits)

    ## END: Unimplmented placehodlders

    ## Called `readWithConstraint(BlockWriter blockWriter, ReadRecordsRequest request)` in Java SDK
    def ReadRecordsRequest(
        self,
    ) -> Union[models.ReadRecordsResponse, models.RemoteReadRecordsResponse]:
        schema = AthenaSDKUtils.parse_encoded_schema(self.event["schema"]["schema"])
        database_name = self.event.get("tableName").get("schemaName")
        table_name = self.event.get("tableName").get("tableName")
        split = self.event.get("split")
        split_properties = split.get("properties", {})

        # If the data source returns a generator, we can begin streaming records
        # to a RecordBatchStreamWriter.
        # Otherwise we take the response and wrap it in a list.
        records = self.data_source.records(database_name, table_name, split_properties)
        if isinstance(records, dict):
            records = (record for record in [records])

        # Convert the records to pyarrow records
        # Regardless of the return type, we stream it so we can spill to S3.
        # If the resulting batch is <6MB, we can return it immediately.
        writer = BatchWriter(split.get("spillLocation"), schema)
        for record_batch in records:
            assert isinstance(record_batch, dict)
            writer.write_rows(record_batch)

        writer.close()
        if writer.spilled:
            return models.RemoteReadRecordsResponse(
                self.catalog_name,
                schema,
                {
                    "@type": "S3SpillLocation",
                    "bucket": split.get("spillLocation").get("bucket"),
                    "key": split.get("spillLocation").get("key") + "/spill.0",
                    "directory": False,
                },
                None,
            )
        else:
            # TODO: Don't convert to a pydict
            pa_records = AthenaSDKUtils.encode_pyarrow_records(
                schema, writer.all_records().to_pydict()
            )
            return models.ReadRecordsResponse(self.catalog_name, schema, pa_records)
