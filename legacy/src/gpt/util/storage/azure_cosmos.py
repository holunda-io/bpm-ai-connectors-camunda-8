from typing import Optional, Sequence, List, cast, Tuple, Iterator

from langchain.schema import BaseStore


class AzureCosmosDbNoSqlStore(BaseStore[str, str]):
    """
    BaseStore implementation using Azure Cosmos DB NoSQL as the underlying store.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        key: str,
        database_name: str,
        container_name: str
    ) -> None:
        try:
            from azure.cosmos import CosmosClient, PartitionKey
        except ImportError as e:
            raise ImportError(
                "The AzureCosmosDbNoSqlStore requires the azure-cosmos library to be installed. "
                "pip install azure-cosmos"
            ) from e

        client = CosmosClient(url=endpoint, credential=key)

        database = client.create_database_if_not_exists(id=database_name)

        key_path = PartitionKey(path="/id")
        self.container = database.create_container_if_not_exists(
            id=container_name, partition_key=key_path, offer_throughput=400
        )

    def mget(self, keys: Sequence[str]) -> List[Optional[str]]:
        """Get the values associated with the given keys."""
        return [self.container.read_item(item=key, partition_key=key)['value'] for key in keys]

    def mset(self, key_value_pairs: Sequence[Tuple[str, str]]) -> None:
        """Set the given key-value pairs."""
        for key, value in key_value_pairs:
            self.container.create_item({"id": key, "value": value})

    def mdelete(self, keys: Sequence[str]) -> None:
        """Delete the given keys."""
        for key in keys:
            self.container.delete_item(item=key, partition_key=key)

    def yield_keys(self, *, prefix: Optional[str] = None) -> Iterator[str]:
        """Yield keys in the store."""
        keys = [i["id"] for i in self.container.read_all_items()]
        for key in keys:
            if (prefix and prefix.startswith(prefix)) or not prefix:
                yield key
