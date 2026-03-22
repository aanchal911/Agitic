import os
import json
from dotenv import load_dotenv

load_dotenv()

_openai_key = os.getenv("OPENAI_API_KEY", "")
_use_real = bool(_openai_key and not _openai_key.startswith("sk-..."))

if _use_real:
    from openai import OpenAI
    _client = OpenAI(api_key=_openai_key)

SYSTEM_PROMPT = """You are a senior DevOps engineer. Analyze the CI/CD error log and return JSON:
{
  "error_type": "short error class name",
  "severity": "low | medium | high | critical",
  "root_cause": "one sentence explanation",
  "affected_file": "file path or unknown",
  "confidence": "percentage e.g. 92%"
}
Output ONLY valid JSON."""


def analyze_error(log: str) -> dict:
    if _use_real:
        try:
            resp = _client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"CI/CD error log:\n{log}"},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            print(f"[Analyzer] OpenAI error: {e} — falling back to mock")

    # Mock fallback
    log_lower = log.lower()
    if "modulenotfounderror" in log_lower or "no module named" in log_lower:
        return {"error_type": "ModuleNotFoundError", "severity": "medium",
                "root_cause": "A required Python package is not installed.", "affected_file": "requirements.txt", "confidence": "95%"}
    if "syntaxerror" in log_lower:
        return {"error_type": "SyntaxError", "severity": "high",
                "root_cause": "Invalid Python syntax — missing bracket or parenthesis.", "affected_file": "src/processor.py", "confidence": "92%"}
    if "connection refused" in log_lower or "operationalerror" in log_lower:
        return {"error_type": "DatabaseConnectionError", "severity": "critical",
                "root_cause": "Database server is unreachable.", "affected_file": "api/routes.py", "confidence": "88%"}
    if "cve" in log_lower or "vulnerabilit" in log_lower:
        return {"error_type": "SecurityVulnerability", "severity": "critical",
                "root_cause": "Outdated dependencies with known CVEs detected.", "affected_file": "package.json", "confidence": "97%"}
    return {"error_type": "UnknownError", "severity": "medium",
            "root_cause": "Could not determine root cause from log snippet.", "affected_file": "unknown", "confidence": "60%"}
