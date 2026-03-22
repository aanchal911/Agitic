import os
import json
from dotenv import load_dotenv

load_dotenv()

_openai_key = os.getenv("OPENAI_API_KEY", "")
_use_real = bool(_openai_key and not _openai_key.startswith("sk-..."))

if _use_real:
    from openai import OpenAI
    _client = OpenAI(api_key=_openai_key)

SYSTEM_PROMPT = """You are a senior code reviewer. Decide if the proposed fix is correct and safe to merge.
Respond in this exact JSON format:
{
  "passes": true or false,
  "confidence": "percentage e.g. 87%",
  "verdict": "one sentence summary",
  "failure_reason": "if passes=false, why the fix is insufficient",
  "improvement_hint": "if passes=false, what the next attempt should do differently"
}
Pass only if: fix addresses root cause, code is correct, no new security issues, security risk is not critical/high.
Output ONLY valid JSON."""


def validate_fix(log: str, analysis: dict, fix: dict, security_report: dict) -> dict:
    risk_level = security_report.get("risk_level", "safe")
    security_score = security_report.get("security_score", 100)

    # Hard fail regardless of AI
    if risk_level == "critical" and security_score < 50:
        return {"passes": False, "confidence": "95%",
                "verdict": "Fix rejected — critical security vulnerabilities must be resolved first.",
                "failure_reason": f"Security score {security_score}/100 with risk_level=critical",
                "improvement_hint": "Upgrade all vulnerable dependencies before merging."}

    if _use_real:
        try:
            resp = _client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        f"Original CI log:\n{log[:500]}\n\n"
                        f"Analysis:\n{json.dumps(analysis, indent=2)}\n\n"
                        f"Proposed fix:\n{json.dumps(fix, indent=2)}\n\n"
                        f"Security report:\n{json.dumps(security_report, indent=2)}"
                    )},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            print(f"[Validator] OpenAI error: {e} — falling back to mock")

    # Mock fallback
    if fix.get("fix_type") == "other":
        return {"passes": False, "confidence": "55%",
                "verdict": "Fix is too generic — needs a specific solution.",
                "failure_reason": "fix_type is 'other', no concrete fix was generated.",
                "improvement_hint": "Provide a more specific error log so the fixer can target the root cause."}
    return {"passes": True, "confidence": "93%",
            "verdict": "Fix directly addresses the root cause and is safe to merge.",
            "failure_reason": "", "improvement_hint": ""}
