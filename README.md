# 🤖 Agitic

> An autonomous, event-driven AI agent system that detects CI/CD pipeline failures, analyzes logs, generates code fixes, and creates GitLab Merge Requests — automatically.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GitLab](https://img.shields.io/badge/GitLab-Duo-orange.svg)](https://gitlab.com)

---

## 🎯 The Problem

Developers waste enormous time on repetitive CI/CD failures:
- Hunting through noisy logs to find the root cause
- Googling the fix for the 10th time
- Creating branches, committing fixes, opening MRs manually
- Context-switching kills flow state

**Agitic eliminates all of that.**

---

## ✨ The Solution

A **multi-agent, event-driven workflow** triggered automatically by GitLab pipeline failures:

```
Pipeline Fails ❌
      ↓
Webhook fires → Agitic triggered 🤖
      ↓
🧠 Analyzer Agent  — parses logs, identifies root cause
      ↓
🔧 Fixer Agent     — generates exact code patch
      ↓
🛡️ Security Agent  — scans fix for vulnerabilities (CVEs)
      ↓
🦊 GitLab API      — creates branch + commits fix + opens MR
      ↓
MR ready for human review ✅
```

---

## 🧩 Features

### Core
- **🧠 Analyzer Agent** — Error type, severity, root cause, affected file, confidence %
- **🔧 Fixer Agent** — Code patches with before/after diffs and shell commands
- **🛡️ Security Agent** — CVE detection, secret scanning, vulnerability assessment
- **✔️ Validator Agent** — Quality gate: decides pass or retry with improvement hints
- **🔁 Smart Retry Loop** — Retries with full failure context until the fix passes
- **🦊 GitLab Integration** — Branch creation, file commits, MR with retry history
- **⚡ Event-Driven** — Webhook trigger on CI failure (zero manual intervention)

### Bonus
- **📊 Live Dashboard** — Animated agent flow, retry timeline, run history drawer
- **🔀 Rich MR Description** — Analysis + security score + retry log in every MR
- **🎛️ REST API** — `/trigger`, `/webhook`, `/api/runs` endpoints
- **📋 Sample Logs** — 4 built-in test scenarios for demo

---

## 🏗️ Architecture

```
agitic/
├── app.py                  # Flask server
├── agents/
│   ├── analyzer.py         # Analyzer Agent
│   ├── fixer.py            # Fixer Agent
│   ├── security.py         # Security Agent
│   └── validator.py        # Validator Agent
├── gitlab/
│   └── gitlab_api.py       # GitLab REST API integration
├── templates/
│   └── dashboard.html      # Live monitoring dashboard
├── .env                    # Your API keys (not committed)
├── .env.example            # Key template
└── requirements.txt
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://gitlab.com/your-username/agitic
cd agitic
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your keys
```

```env
OPENAI_API_KEY=sk-...
GITLAB_TOKEN=glpat-...
GITLAB_PROJECT_ID=12345678
```

**Get your keys:**
- OpenAI: https://platform.openai.com/api-keys
- GitLab Token: Profile → Access Tokens → scopes: `api`, `write_repository`
- Project ID: Your GitLab project → Settings → General

### 3. Run

```bash
python app.py
```

Open **http://localhost:4367** for the dashboard.

### 4. Test It

```bash
curl -X POST http://localhost:4367/trigger \
  -H "Content-Type: application/json" \
  -d '{"log": "ModuleNotFoundError: No module named '\''requests'\''"}'
```

---

## 🔗 GitLab Webhook Setup

To trigger automatically on real CI failures:

1. Go to your GitLab project → **Settings → Webhooks**
2. URL: `http://your-public-host:4367/webhook`
3. Trigger: ✅ **Pipeline events**
4. Save

Now every failed pipeline automatically triggers the agent. 🎉

> **Tip for local dev:** Use [ngrok](https://ngrok.com) to expose localhost:
> ```bash
> ngrok http 4367
> # Use the https://xxx.ngrok.io URL in GitLab
> ```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Live dashboard |
| `POST` | `/trigger` | Manual trigger `{"log": "..."}` |
| `POST` | `/webhook` | GitLab pipeline webhook |
| `GET` | `/api/runs` | All run history (JSON) |
| `GET` | `/api/runs/<run_id>` | Single run details |

---

## 🤖 4-Agent System

Each agent has a single, focused responsibility and communicates via structured JSON:

| Agent | Role | Output |
|-------|------|--------|
| 🧠 Analyzer | Parses CI logs | error_type, severity, root_cause, confidence |
| 🔧 Fixer | Generates code patch | code_before/after, shell_commands |
| 🛡️ Security | CVE & vuln scanning | security_score, risk_level, findings[] |
| ✔️ Validator | Quality gate + retry decision | passes, confidence, improvement_hint |

### 🔁 Smart Retry Loop

The Validator Agent closes the feedback loop:

```
generate fix → validate → ❌ failed?
                             ↓ improvement_hint fed back to Fixer
                          retry with new context → validate again → ✅
```

On each failed attempt, the Fixer receives the full history of what was tried
and why it failed — so retries produce meaningfully different solutions, not
the same prompt re-run.

---

## 📸 Screenshots

![Dashboard Overview](./Screenshot%202026-03-22%20213418.png)

![Agent Flow Running](./Screenshot%202026-03-22%20220418.png)

![Result Drawer](./Screenshot%202026-03-22%20220429.png)

---

## 📄 License

MIT — see [LICENSE](LICENSE)


