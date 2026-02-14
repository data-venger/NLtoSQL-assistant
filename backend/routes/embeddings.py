"""Embeddings API routes for schema management."""

from flask import Blueprint, request, jsonify
from services.embedding_service import EmbeddingService

bp = Blueprint("embeddings", __name__, url_prefix="/api/embeddings")


@bp.route("/embed", methods=["POST"])
def embed_schema():
    data = request.get_json(force=True)
    table_name = data.get("table_name", "").strip()
    ddl = data.get("ddl_statement", "").strip()
    if not table_name or not ddl:
        return jsonify({"error": "table_name and ddl_statement are required"}), 400

    eid = EmbeddingService().embed_schema(table_name, ddl, data.get("description", ""))
    return jsonify({"success": True, "embedding_id": eid, "table_name": table_name})


@bp.route("/search", methods=["POST"])
def search_schemas():
    data = request.get_json(force=True)
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400

    results = EmbeddingService().search_similar_schemas(query, limit=data.get("limit", 3))
    return jsonify({"success": True, "results": results})


@bp.route("/schemas", methods=["GET"])
def list_schemas():
    return jsonify({"success": True, "schemas": EmbeddingService().get_all_schemas()})
