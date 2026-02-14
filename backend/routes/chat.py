"""Chat API routes — the core RAG pipeline."""

import uuid
import logging
from flask import Blueprint, request, jsonify
from services.database_service import DatabaseService
from services.embedding_service import EmbeddingService
from services.llm_client import LLMClient

logger = logging.getLogger(__name__)
bp = Blueprint("chat", __name__, url_prefix="/api/chat")

# In-memory session store (good enough for MVP)
_sessions: dict[str, list] = {}

DB_KEYWORDS = {
    "show", "select", "query", "database", "table", "customer", "account",
    "transaction", "loan", "payment", "branch", "how many", "count",
    "list", "find", "search", "get", "retrieve", "display", "total",
    "average", "sum", "max", "min", "top", "bottom", "recent",
    "credit", "card", "balance", "amount",
}


def _is_database_query(msg: str) -> bool:
    lower = msg.lower()
    return any(kw in lower for kw in DB_KEYWORDS)


@bp.route("", methods=["POST"])
def chat():
    """Handle a chat message through the RAG pipeline."""
    data = request.get_json(force=True)
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400

    session_id = data.get("session_id") or str(uuid.uuid4())
    if session_id not in _sessions:
        _sessions[session_id] = []

    # Store user message
    user_entry = {"role": "user", "content": message}
    _sessions[session_id].append(user_entry)

    try:
        if _is_database_query(message):
            response_content, sql_query, sql_result = _handle_db_query(message)
        else:
            response_content = _handle_general_query(message)
            sql_query = None
            sql_result = None

        assistant_entry = {
            "role": "assistant",
            "content": response_content,
            "sql_query": sql_query,
            "sql_result": sql_result,
        }
        _sessions[session_id].append(assistant_entry)

        return jsonify({"success": True, "session_id": session_id, "message": assistant_entry})

    except Exception as e:
        logger.exception("Chat error")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/sessions", methods=["GET"])
def list_sessions():
    """List all chat sessions."""
    out = []
    for sid, msgs in _sessions.items():
        preview = msgs[0]["content"][:80] if msgs else ""
        out.append({"session_id": sid, "message_count": len(msgs), "preview": preview})
    return jsonify(out)


@bp.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    """Get all messages in a session."""
    msgs = _sessions.get(session_id)
    if msgs is None:
        return jsonify({"error": "Session not found"}), 404
    return jsonify({"session_id": session_id, "messages": msgs})


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _handle_db_query(message: str):
    emb = EmbeddingService()
    schemas = emb.search_similar_schemas(message)

    llm = LLMClient()
    sql = llm.generate_sql(message, schemas)

    db = DatabaseService()
    result = db.execute_safe_query(sql)

    response = llm.generate_response(message, sql, result)
    return response, sql, result


def _handle_general_query(message: str):
    try:
        llm = LLMClient()
        return llm.generate_brief_response(message)
    except Exception:
        return "I'm designed to help with database queries about banking data."
