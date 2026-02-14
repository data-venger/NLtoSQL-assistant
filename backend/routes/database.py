"""Database introspection & direct query API routes."""

from flask import Blueprint, request, jsonify
from services.database_service import DatabaseService

bp = Blueprint("database", __name__, url_prefix="/api/database")


@bp.route("/test", methods=["GET"])
def test_connection():
    return jsonify(DatabaseService().test_connection())


@bp.route("/tables", methods=["GET"])
def list_tables():
    return jsonify(DatabaseService().get_database_stats())


@bp.route("/tables/<table_name>", methods=["GET"])
def table_info(table_name):
    return jsonify(DatabaseService().get_table_info(table_name))


@bp.route("/execute", methods=["POST"])
def execute_query():
    """Execute a user-provided SQL query (read-only)."""
    data = request.get_json(force=True)
    sql = data.get("query", "").strip()
    if not sql:
        return jsonify({"error": "Query is required"}), 400
    return jsonify(DatabaseService().execute_safe_query(sql))
