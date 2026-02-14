"""Database service for safe, read-only SQL execution."""

import logging
import threading
from decimal import Decimal
from datetime import datetime, date, time
from sqlalchemy import create_engine, text
from config import config
import sqlparse

logger = logging.getLogger(__name__)

engine = create_engine(
    config.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)


class QueryTimeoutException(Exception):
    """Raised when a query exceeds the configured timeout."""
    pass


class DatabaseService:
    def __init__(self):
        self.timeout = config.SQL_QUERY_TIMEOUT
        self.max_rows = config.MAX_RESULT_ROWS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_safe_query(self, sql_query: str) -> dict:
        """Execute a SQL query with read-only safety constraints."""
        try:
            if not self._is_safe_query(sql_query):
                raise ValueError("Query contains potentially unsafe operations")

            parsed_query = self._parse_and_format_query(sql_query)
            result = self._execute_with_timeout(parsed_query)

            return {
                "success": True,
                "data": result["data"],
                "columns": result["columns"],
                "row_count": result["row_count"],
                "query": parsed_query,
            }
        except Exception as e:
            logger.error("Error executing query: %s", e)
            return {"success": False, "error": str(e), "query": sql_query}

    def test_connection(self) -> dict:
        """Test database connectivity."""
        try:
            with engine.connect() as conn:
                row = conn.execute(text("SELECT 1")).fetchone()
            return {"success": True, "message": "Database connection successful", "result": row[0] if row else None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_database_stats(self) -> dict:
        """Return table list with row counts and descriptions."""
        descriptions = {
            "branches": "Bank branch locations and contact information",
            "customers": "Customer personal and financial information",
            "accounts": "Bank accounts with balances and types",
            "transactions": "All account transactions and transfers",
            "credit_cards": "Credit card information and limits",
            "credit_card_transactions": "Credit card purchases and payments",
            "loans": "Loan information (mortgages, personal, auto)",
            "loan_payments": "Individual loan payment records",
        }
        try:
            tables = []
            total_rows = 0
            with engine.connect() as conn:
                rows = conn.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name"
                )).fetchall()

                for (table_name,) in rows:
                    if table_name.startswith(("pg_", "sql_")):
                        continue
                    cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
                    tables.append({
                        "table_name": table_name,
                        "row_count": cnt,
                        "description": descriptions.get(table_name, f"Table: {table_name}"),
                    })
                    total_rows += cnt

            return {"success": True, "total_tables": len(tables), "total_rows": total_rows, "tables": tables}
        except Exception as e:
            logger.error("Error getting database stats: %s", e)
            return {"success": False, "error": str(e)}

    def get_table_info(self, table_name: str) -> dict:
        """Return column metadata for a table."""
        try:
            with engine.connect() as conn:
                rows = conn.execute(text(
                    "SELECT column_name, data_type, is_nullable, column_default "
                    "FROM information_schema.columns WHERE table_name = :t ORDER BY ordinal_position"
                ), {"t": table_name}).fetchall()

            return {
                "success": True,
                "table_name": table_name,
                "columns": [
                    {"name": r[0], "type": r[1], "nullable": r[2] == "YES", "default": r[3]}
                    for r in rows
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize_value(value):
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (datetime, date, time)):
            return value.isoformat()
        return value

    @staticmethod
    def _is_safe_query(sql_query: str) -> bool:
        """Only allow SELECT / WITH (CTE) statements."""
        parsed = sqlparse.parse(sql_query)
        if not parsed:
            return False

        dangerous = {"INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "EXEC", "EXECUTE", "CALL", "MERGE", "UPSERT"}
        upper = sql_query.upper()
        for kw in dangerous:
            if kw in upper:
                return False

        for stmt in parsed:
            first = None
            for token in stmt.flatten():
                if token.ttype not in (
                    sqlparse.tokens.Comment.Single,
                    sqlparse.tokens.Comment.Multiline,
                    sqlparse.tokens.Whitespace,
                    sqlparse.tokens.Newline,
                ):
                    first = token
                    break
            if first is None:
                continue
            val = first.value.upper()
            if val not in ("SELECT", "WITH"):
                return False
        return True

    def _parse_and_format_query(self, sql_query: str) -> str:
        try:
            formatted = sqlparse.format(sql_query, reindent=True, keyword_case="upper")
            if "LIMIT" not in formatted.upper():
                formatted = f"{formatted.rstrip(';')} LIMIT {self.max_rows};"
            return formatted
        except Exception:
            return sql_query

    def _execute_with_timeout(self, sql_query: str) -> dict:
        result = {"data": [], "columns": [], "row_count": 0}
        exc_box = [None]

        def _run():
            try:
                with engine.connect() as conn:
                    rs = conn.execute(text(sql_query))
                    if rs.returns_rows:
                        result["columns"] = list(rs.keys())
                        rows = rs.fetchmany(self.max_rows)
                        result["data"] = [[self._serialize_value(v) for v in r] for r in rows]
                        result["row_count"] = len(rows)
            except Exception as e:
                exc_box[0] = e

        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=self.timeout)

        if t.is_alive():
            raise QueryTimeoutException(f"Query timed out after {self.timeout}s")
        if exc_box[0]:
            raise exc_box[0]
        return result
