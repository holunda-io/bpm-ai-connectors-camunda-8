from typing import List, Optional, Type

from langchain import SQLDatabase
from langchain.agents.agent_toolkits.base import BaseToolkit
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools import BaseTool, BaseSQLDatabaseTool
from langchain.pydantic_v1 import Field, BaseModel


class QuerySQLDataBaseToolSchema(BaseModel):
    query: str = Field(description="valid sql query")

class QuerySQLDataBaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for querying a SQL database."""

    name = "sql_query"
    description = """\
    Input to this tool is a detailed and correct SQL query, output is a result from the database.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    If you encounter an issue with Unknown column 'xxxx' in 'field list', using sql_schema to query the correct table fields."""
    args_schema: Type[QuerySQLDataBaseToolSchema] = QuerySQLDataBaseToolSchema

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the query, return the results or an error message."""
        return self.db.run_no_throw(query)

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("QuerySqlDbTool does not support async")

class InfoSQLDataBaseToolSchema(BaseModel):
    table_names: str = Field(description="comma-separated list of table names")

class InfoSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting metadata about a SQL database."""

    name = "sql_schema"
    description = """\
    Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables.

    Example Input: "table1, table2, table3"
    """
    args_schema: Type[InfoSQLDataBaseToolSchema] = InfoSQLDataBaseToolSchema

    def _run(
        self,
        table_names: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get the schema for tables in a comma-separated list."""
        return self.db.get_table_info_no_throw(list(map(str.strip, table_names.split(","))))

    async def _arun(
        self,
        table_name: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("SchemaSqlDbTool does not support async")

class ListSQLDataBaseToolSchema(BaseModel):
    input: str = Field(description="empty string")

class ListSQLDatabaseTool(BaseSQLDatabaseTool, BaseTool):
    """Tool for getting tables names."""

    name = "sql_list_tables"
    description = "Input is an empty string, output is a comma separated list of tables in the database."
    args_schema: Type[ListSQLDataBaseToolSchema] = ListSQLDataBaseToolSchema

    def _run(
        self,
        input: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get the schema for a specific table."""
        return ", ".join(self.db.get_usable_table_names())

    async def _arun(
        self,
        input: str = "",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("ListTablesSqlDbTool does not support async")


class SQLDatabaseToolkit(BaseToolkit):
    """Toolkit for interacting with SQL databases."""

    db: SQLDatabase = Field(exclude=True)
    llm: BaseLanguageModel = Field(exclude=True)

    @property
    def dialect(self) -> str:
        """Return string representation of dialect to use."""
        return self.db.dialect

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            QuerySQLDataBaseTool(db=self.db),
            InfoSQLDatabaseTool(db=self.db),
            ListSQLDatabaseTool(db=self.db),
        ]
