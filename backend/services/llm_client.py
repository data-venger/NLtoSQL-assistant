"""LLM client supporting Ollama and Gemini providers."""

import logging
import os
import requests
from config import config

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for local Ollama LLM."""

    def __init__(self):
        self.base_url = config.OLLAMA_URL
        self.model = config.OLLAMA_MODEL

    def _make_request(self, prompt: str, system_prompt: str | None = None) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if system_prompt:
            payload["system"] = system_prompt
        try:
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except Exception as e:
            logger.error("Ollama request failed: %s", e)
            raise

    def generate_sql(self, user_question: str, relevant_schemas: list) -> str:
        system = (
            "You are a SQL expert. Generate accurate, safe PostgreSQL queries.\n"
            "Rules:\n"
            "1. Only generate SELECT statements\n"
            "2. Use proper PostgreSQL syntax\n"
            "3. Include appropriate JOINs when needed\n"
            "4. Use LIMIT to keep results reasonable\n"
            "5. Use column names exactly as defined in schema\n"
            "6. Return only the SQL query, no explanations"
        )
        schema_ctx = "\n\n".join(
            f"Table: {s['table_name']}\n{s['ddl_statement']}" for s in relevant_schemas
        )
        prompt = f"Database Schema:\n{schema_ctx}\n\nUser Question: {user_question}\n\nGenerate a PostgreSQL SELECT query:"
        sql = self._make_request(prompt, system)
        sql = sql.replace("```sql", "").replace("```", "").strip()
        return sql

    def generate_response(self, user_question: str, sql_query: str, query_result: dict) -> str:
        system = (
            "You are a helpful data analyst. Answer clearly and concisely.\n"
            "Rules:\n1. Answer in natural language\n2. Be specific with numbers\n"
            "3. Keep responses under 200 words\n4. Highlight key insights"
        )
        if query_result.get("success"):
            data = query_result.get("data", [])
            cols = query_result.get("columns", [])
            rc = query_result.get("row_count", 0)
            if rc == 0:
                result_text = "No results found."
            else:
                result_text = f"Found {rc} result(s).\nColumns: {', '.join(cols)}\n"
                for i, row in enumerate(data[:3]):
                    result_text += f"Row {i+1}: {dict(zip(cols, row))}\n"
                if rc > 3:
                    result_text += f"... and {rc - 3} more rows"
        else:
            result_text = f"Query failed: {query_result.get('error', 'Unknown error')}"

        prompt = (
            f"User Question: {user_question}\n\n"
            f"SQL Query Used: {sql_query}\n\n"
            f"Query Results: {result_text}\n\n"
            "Provide a helpful response:"
        )
        try:
            return self._make_request(prompt, system)
        except Exception:
            return f"Found {query_result.get('row_count', 0)} results for your query."

    def generate_brief_response(self, user_question: str) -> str:
        system = "You are a database assistant. For non-database questions, provide a very brief response (under 50 words) and redirect to database topics."
        prompt = f"Question: {user_question}\n\nBrief response:"
        try:
            resp = self._make_request(prompt, system)
            return resp[:200] if len(resp) > 200 else resp
        except Exception:
            return "I'm designed to help with database queries about banking data."

    def test_connection(self) -> dict:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=10)
            r.raise_for_status()
            return {"success": True, "message": "Ollama connected", "model": self.model, "provider": "ollama"}
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "ollama"}


class GeminiClient:
    """Client for Google Gemini API."""

    def __init__(self):
        import google.generativeai as genai
        self.api_key = config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        genai.configure(api_key=self.api_key)
        self.model_name = config.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

    def _make_request(self, prompt: str, system_prompt: str | None = None) -> str:
        full = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        resp = self.model.generate_content(full, generation_config={"temperature": 0.1, "max_output_tokens": 500})
        return resp.text.strip()

    # Delegate same interface as OllamaClient ---
    def generate_sql(self, user_question, relevant_schemas):
        return OllamaClient.generate_sql(self, user_question, relevant_schemas)

    def generate_response(self, user_question, sql_query, query_result):
        return OllamaClient.generate_response(self, user_question, sql_query, query_result)

    def generate_brief_response(self, user_question):
        return OllamaClient.generate_brief_response(self, user_question)

    def test_connection(self):
        try:
            self._make_request("Say hello.")
            return {"success": True, "message": "Gemini connected", "model": self.model_name, "provider": "gemini"}
        except Exception as e:
            return {"success": False, "error": str(e), "provider": "gemini"}


class LLMClient:
    """Factory that selects the configured LLM provider."""

    def __init__(self):
        provider = config.LLM_PROVIDER.lower()
        if provider == "gemini":
            self._client = GeminiClient()
        else:
            self._client = OllamaClient()

    def generate_sql(self, *a, **kw):
        return self._client.generate_sql(*a, **kw)

    def generate_response(self, *a, **kw):
        return self._client.generate_response(*a, **kw)

    def generate_brief_response(self, *a, **kw):
        return self._client.generate_brief_response(*a, **kw)

    def test_connection(self):
        return self._client.test_connection()
