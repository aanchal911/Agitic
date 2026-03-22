import os
import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from agents.analyzer import analyze_error
from agents.fixer import generate_fix
from agents.security import scan_security
from agents.validator import validate_fix

from gitlab.gitlab_api import create_branch, commit_fix, create_merge_request

load_dotenv()

app = Flask(__name__)

# In-memory store for dashboard
pipeline_runs = []

MAX_RETRY_ATTEMPTS = 3  # Keep small for demo clarity


@app.route("/")
def dashboard():
    return render_template("dashboard.html", runs=pipeline_runs)


@app.route("/webhook", methods=["POST"])
def gitlab_webhook():
    """GitLab CI/CD webhook endpoint — triggered on pipeline failure."""
    payload = request.json or {}

    if "object_kind" in payload and payload.get("object_kind") == "pipeline":
        status = payload.get("object_attributes", {}).get("status")
        if status != "failed":
            return jsonify({"message": "Pipeline not failed, skipping"}), 200
        log = (
            f"GitLab Pipeline #{payload['object_attributes'].get('id')} failed.\n"
            f"Stages: {payload['object_attributes'].get('stages', [])}"
        )
    else:
        log = payload.get("log", "")

    if not log:
        return jsonify({"error": "No log provided"}), 400

    return _run_agent_flow(log, source="webhook")


@app.route("/trigger", methods=["POST"])
def trigger_agent():
    """Manual trigger endpoint for testing."""
    log = request.json.get("log", "")
    if not log:
        return jsonify({"error": "No log provided"}), 400
    return _run_agent_flow(log, source="manual")


def _run_agent_flow(log: str, source: str):
    """
    Core multi-agent pipeline with Smart Retry.

    Flow:
      Trigger → Analyze → Fix → Validate → [retry if needed] → GitLab MR

    On each failed validation the Fixer Agent receives all prior attempts
    as context, so each retry produces a meaningfully different solution.
    """
    session_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    attempts = []
    final_fix = None
    final_analysis = None
    final_security = None
    ci_passed = False

    print(f"\n{'='*60}")
    print(f"[Agitic] triggered [{source}] - Session: {session_id}")
    print(f"{'='*60}")

    previous_fixes = []  # Feed prior failed attempts to Fixer for improvement

    for attempt_num in range(1, MAX_RETRY_ATTEMPTS + 1):
        print(f"\n{'─'*40}")
        print(f"[Attempt {attempt_num} / {MAX_RETRY_ATTEMPTS}]")
        print(f"{'─'*40}")

        print("[Analyzer] Examining CI logs...")
        analysis = analyze_error(log)
        print(f"   -> {analysis.get('error_type', '?')} | severity: {analysis.get('severity', '?')}")

        print("[Fixer] Generating code fix...")
        fix = generate_fix(log, analysis, previous_fixes=previous_fixes)
        print(f"   -> {fix.get('fix_description', 'fix generated')}")

        print("[Security] Scanning for vulnerabilities...")
        security_report = scan_security(log, fix)
        print(f"   -> Score: {security_report.get('security_score', '?')}/100 | Risk: {security_report.get('risk_level', '?')}")

        print("[Validator] Checking fix quality...")
        validation = validate_fix(log, analysis, fix, security_report)
        is_valid = validation.get("passes", False)
        confidence = validation.get("confidence", "0%")
        print(f"   -> passes={is_valid} | confidence={confidence}")

        attempt_record = {
            "attempt": attempt_num,
            "analysis": analysis,
            "fix": fix,
            "security_report": security_report,
            "validation": validation,
            "passed": is_valid,
        }
        attempts.append(attempt_record)

        final_analysis = analysis
        final_fix = fix
        final_security = security_report

        if is_valid:
            ci_passed = True
            print(f"\n[PASSED] Fix validated on attempt {attempt_num}!")
            break
        else:
            reason = validation.get("failure_reason", "Quality check failed")
            print(f"\n[FAILED] Attempt {attempt_num} failed validation: {reason}")
            previous_fixes.append({
                "attempt": attempt_num,
                "fix": fix.get("code_after", ""),
                "failure_reason": reason,
            })
            if attempt_num < MAX_RETRY_ATTEMPTS:
                print("[Retry] Re-analyzing with improved context...")

    # ── GitLab Integration ─────────────────────────────────────
    branch_name = f"autofix/{session_id}"
    mr_url = None
    gitlab_status = "skipped"

    gitlab_token = os.getenv("GITLAB_TOKEN", "")
    project_id = os.getenv("GITLAB_PROJECT_ID", "")

    if gitlab_token and project_id:
        print(f"\n[GitLab] Creating branch: {branch_name}")
        create_branch(branch_name)

        print("[GitLab] Committing fix...")
        commit_fix(branch_name, final_fix, session_id)

        print("[GitLab] Opening Merge Request...")
        mr_url = create_merge_request(
            branch_name, final_analysis, final_security,
            attempts=attempts, ci_passed=ci_passed
        )
        gitlab_status = "mr_created"
        print(f"   MR created: {mr_url}")
    else:
        print("\n[GitLab] env vars not set - demo mode")
        mr_url = "https://gitlab.com/demo/project/-/merge_requests/42"
        gitlab_status = "demo_mode"

    # ── Build result ───────────────────────────────────────────
    result = {
        "run_id": session_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "source": source,
        "log_snippet": log[:300],
        "total_attempts": len(attempts),
        "ci_passed": ci_passed,
        "attempts": attempts,
        "analysis": final_analysis,
        "fix": final_fix,
        "security_report": final_security,
        "branch": branch_name,
        "mr_url": mr_url,
        "gitlab_status": gitlab_status,
    }
    pipeline_runs.insert(0, result)

    status_label = (
        f"PASSED after {len(attempts)} attempt(s)"
        if ci_passed
        else f"Max attempts ({MAX_RETRY_ATTEMPTS}) reached"
    )
    print(f"\n{status_label}")
    print(f"{'='*60}\n")

    return jsonify(result), 200


@app.route("/api/runs", methods=["GET"])
def get_runs():
    return jsonify(pipeline_runs)


@app.route("/api/runs/<run_id>", methods=["GET"])
def get_run(run_id):
    run = next((r for r in pipeline_runs if r["run_id"] == run_id), None)
    if not run:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(run)


if __name__ == "__main__":
    print("Agitic starting...")
    app.run(debug=True, port=4367)
