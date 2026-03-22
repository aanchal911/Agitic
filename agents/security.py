import os
import json
from dotenv import load_dotenv

load_dotenv()

_openai_key = os.getenv("OPENAI_API_KEY", "")
_use_real = bool(_openai_key and not _openai_key.startswith("sk-..."))

if _use_real:
    from openai import OpenAI
    _client = OpenAI(api_key=_openai_key)

SYSTEM_PROMPT = """You are a security engineer. Scan the proposed fix for vulnerabilities.
Respond in this exact JSON format:
{
  "security_score": 0-100,
  "risk_level": "safe | low | medium | high | critical",
  "summary": "one sentence",
  "findings": [
    {
      "type": "finding type",
      "cve": "CVE-XXXX-XXXX or null",
      "description": "what the issue is",
      "recommendation": "how to fix it"
    }
  ]
}
Output ONLY valid JSON."""


def scan_security(log: str, fix: dict) -> dict:
    if _use_real:
        try:
            resp = _client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        f"CI/CD log:\n{log[:500]}\n\n"
                        f"Proposed fix:\n{json.dumps(fix, indent=2)}"
                    )},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            print(f"[Security] OpenAI error: {e} — falling back to mock")

    # Mock fallback
    log_lower = log.lower()
    fix_str = str(fix).lower()
    if "cve" in log_lower or "vulnerabilit" in log_lower:
        return {"security_score": 42, "risk_level": "critical",
                "summary": "Critical CVEs detected in dependencies. Immediate upgrade required.",
                "findings": [
                    {"type": "Vulnerable Dependency", "cve": "CVE-2021-23337",
                     "description": "Prototype Pollution in lodash < 4.17.21", "recommendation": "Upgrade lodash to >= 4.17.21"},
                    {"type": "Vulnerable Dependency", "cve": "CVE-2021-3749",
                     "description": "SSRF vulnerability in axios < 0.21.2", "recommendation": "Upgrade axios to >= 0.21.2"},
                ]}
    if "password" in fix_str or "secret" in fix_str or "token" in fix_str:
        return {"security_score": 65, "risk_level": "medium",
                "summary": "Potential hardcoded secret detected in fix.",
                "findings": [{"type": "Hardcoded Secret", "cve": None,
                               "description": "Fix may contain a hardcoded credential.",
                               "recommendation": "Use environment variables instead."}]}
    return {"security_score": 95, "risk_level": "safe",
            "summary": "No security issues detected in the proposed fix.", "findings": []}
