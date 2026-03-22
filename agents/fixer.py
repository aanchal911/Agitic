import os
import json
from dotenv import load_dotenv

load_dotenv()

_openai_key = os.getenv("OPENAI_API_KEY", "")
_use_real = bool(_openai_key and not _openai_key.startswith("sk-..."))

if _use_real:
    from openai import OpenAI
    _client = OpenAI(api_key=_openai_key)

SYSTEM_PROMPT = """You are a senior software engineer. Given a CI/CD error log and analysis, produce a fix.
Respond in this exact JSON format:
{
  "fix_description": "one sentence",
  "fix_type": "dependency | code_change | config | test_fix | other",
  "file_path": "path/to/file",
  "code_before": "original broken snippet or empty string",
  "code_after": "fixed snippet",
  "shell_commands": ["commands", "to", "run"],
  "explanation": "step-by-step explanation"
}
Output ONLY valid JSON."""


def generate_fix(log: str, analysis: dict, previous_fixes: list = None) -> dict:
    if _use_real:
        try:
            retry_context = ""
            if previous_fixes:
                retry_context = (
                    "\n\nPREVIOUS FAILED ATTEMPTS (do NOT repeat):\n"
                    + json.dumps(previous_fixes, indent=2)
                    + "\n\nProduce a different, improved solution."
                )
            resp = _client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": (
                        f"CI/CD error log:\n{log}\n\n"
                        f"Analysis:\n{json.dumps(analysis, indent=2)}"
                        f"{retry_context}"
                    )},
                ],
                temperature=0.3 + (len(previous_fixes or []) * 0.1),
                response_format={"type": "json_object"},
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            print(f"[Fixer] OpenAI error: {e} — falling back to mock")

    # Mock fallback
    error_type = analysis.get("error_type", "")
    if error_type == "ModuleNotFoundError":
        module = "requests"
        for word in log.split():
            if "'" in word:
                module = word.strip("'\"")
                break
        return {"fix_description": f"Add missing '{module}' to requirements.txt", "fix_type": "dependency",
                "file_path": "requirements.txt", "code_before": "flask\nopenai",
                "code_after": f"flask\nopenai\n{module}", "shell_commands": [f"pip install {module}"],
                "explanation": f"Package '{module}' is missing from requirements.txt."}
    if error_type == "SyntaxError":
        return {"fix_description": "Fix missing closing parenthesis", "fix_type": "code_change",
                "file_path": "src/processor.py", "code_before": "def process_data(data",
                "code_after": "def process_data(data):", "shell_commands": [],
                "explanation": "Function definition was missing closing parenthesis and colon."}
    if error_type == "DatabaseConnectionError":
        return {"fix_description": "Add DATABASE_URL and start database", "fix_type": "config",
                "file_path": ".env", "code_before": "# no database config",
                "code_after": "DATABASE_URL=postgresql://localhost:5432/mydb",
                "shell_commands": ["docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=pass postgres"],
                "explanation": "Database is unreachable. Set DATABASE_URL and ensure DB is running."}
    if error_type == "SecurityVulnerability":
        return {"fix_description": "Upgrade vulnerable dependencies", "fix_type": "dependency",
                "file_path": "package.json", "code_before": '"lodash": "^4.17.15"',
                "code_after": '"lodash": "^4.17.21"', "shell_commands": ["npm audit fix --force", "npm install"],
                "explanation": "Upgrading lodash, axios, node-fetch to patch known CVEs."}
    return {"fix_description": "Manual review required", "fix_type": "other", "file_path": "unknown",
            "code_before": "", "code_after": "# Review the error log manually", "shell_commands": [],
            "explanation": "Error type not recognized. Please review manually."}
