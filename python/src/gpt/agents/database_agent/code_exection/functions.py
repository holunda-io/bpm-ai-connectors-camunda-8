import re
from typing import List, Callable

from langchain import SQLDatabase
from langchain.base_language import BaseLanguageModel
from langchain.tools import QuerySQLDataBaseTool, InfoSQLDatabaseTool, ListSQLDatabaseTool, QuerySQLCheckerTool

from gpt.agents.database_agent.code_exection.util import format_template


def get_database_functions(llm: BaseLanguageModel, db: SQLDatabase) -> List[Callable]:

    def sql_query(query: str):
        """
        Takes a detailed and correct SQL query, returns a list of tuples with results from the database.
        If the query is not correct, an error message will be returned. If an error is returned, rewrite the query, check the query, and try again.
        If you encounter an issue with Unknown column 'xxxx' in 'field list', use sql_table_info to query the correct table fields.
        """
        return eval(QuerySQLDataBaseTool(db=db).run(query))

    def sql_table_info(tables: List[str]):
        """
        Takes a list of table names, returns the schema and sample rows for those tables.
        Be sure that the tables actually exist by calling sql_list_tables first!
        Example Input: [table1, table2, table3]
        """
        return InfoSQLDatabaseTool(db=db).run(
            ", ".join(tables)
        )

    def sql_list_tables():
        """
        Returns a list of table names in the database
        """
        result = ListSQLDatabaseTool(db=db).run("")
        return re.split(r'\s*,\s*', result)

    def sql_check_query(query_template: str, **query_kwargs):
        """
        Use this tool to double-check if your query is correct before executing it.
        Always use this tool before executing a query with sql_query
        """
        return QuerySQLCheckerTool(db=db, llm=llm).run(
            query_template.format(query_kwargs)
        )

    return [sql_query, sql_table_info, sql_list_tables]
