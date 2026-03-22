<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Syne&weight=800&size=40&pause=1000&color=00D4AA&center=true&vCenter=true&width=600&lines=🤖+Agitic;Autonomous+CI%2FCD+Fix+Agent;Pipeline+Fails+%E2%9D%8C+%E2%86%92+MR+Ready+%E2%9C%85" alt="Agitic" />

<br/>

<p><strong>An autonomous, event-driven AI agent that detects CI/CD pipeline failures, analyzes logs, generates code fixes, and opens GitLab Merge Requests — automatically. Zero human intervention.</strong></p>

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-00d4aa.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-000000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991.svg?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![GitLab](https://img.shields.io/badge/GitLab-API-FC6D26.svg?style=for-the-badge&logo=gitlab&logoColor=white)](https://gitlab.com)

<br/>

</div>

---

## 🎯 The Problem

Every developer knows this loop:

```
CI pipeline fails at 2am
    → dig through 500 lines of logs
    → google the error (again)
    → figure out the fix
    → create a branch
    → commit the change
    → open a MR
    → repeat tomorrow
```

> **This kills flow state. It's repetitive. It's automatable.**

**Agitic eliminates all of that** — from failure detection to MR creation, fully automated.

---

## ✨ How It Works

<div align="center">

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Pipeline Fails ❌                                         │
│         │                                                   │
│         ▼                                                   │
│   Webhook / Manual Trigger                                  │
│         │                                                   │
│         ▼                                                   │
│   ┌─────────────┐                                           │
│   │ 🧠 Analyzer │  ── parses logs, finds root cause         │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────┐                                           │
│   │ 🔧 Fixer    │  ── generates exact code patch            │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────┐                                           │
│   │ 🛡️ Security │  ── scans for CVEs & vulnerabilities      │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────┐     ❌ fails?                             │
│   │ ✔️ Validator│  ──────────────► retry with hint          │
│   └──────┬──────┘                      │                    │
│          │ ✅ passes                    └──► back to Fixer   │
│          ▼                                                   │
│   🦊 GitLab: branch + commit + MR                           │
│         │                                                   │
│         ▼                                                   │
│   MR Ready for Human Review ✅                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

</div>

---

## 🧩 Features

### 🤖 Core Agents

| Agent | What it does | Output |
|-------|-------------|--------|
| 🧠 **Analyzer** | Reads CI logs, classifies error, finds root cause | `error_type`, `severity`, `root_cause`, `confidence` |
| 🔧 **Fixer** | Generates a production-ready code patch | `code_before`, `code_after`, `shell_commands` |
| 🛡️ **Security** | Scans fix for CVEs, secrets, vulnerabilities | `security_score`, `risk_level`, `findings[]` |
| ✔️ **Validator** | Quality gate — pass or retry with improvement hint | `passes`, `confidence`, `improvement_hint` |

### 🔁 Smart Retry Loop

The Validator closes the feedback loop. On failure, the **exact reason + improvement hint** is fed back to the Fixer so each retry is meaningfully different — not the same prompt re-run.

```
Fixer generates patch
        │
        ▼
Validator reviews ──── ❌ FAIL ──► hint fed back to Fixer ──► retry
        │
        ✅ PASS
        │
        ▼
GitLab MR created
```

### ⚡ Everything Else

- **📊 Live Dashboard** — animated agent flow, stats, run history, result drawer
- **🔀 Rich MR Description** — full analysis + security score + retry timeline in every MR
- **🎛️ REST API** — `/trigger`, `/webhook`, `/api/runs` endpoints
- **🔌 Works without API keys** — full mock mode for local development
- **🔑 Plug-and-play keys** — add OpenAI + GitLab keys to `.env` and go live instantly

---

## 🏗️ Architecture

```
agitic/
├── app.py                  ← Flask server, orchestrates the agent flow
├── agents/
│   ├── analyzer.py         ← Analyzer Agent  (real OpenAI or mock)
│   ├── fixer.py            ← Fixer Agent     (real OpenAI or mock)
│   ├── security.py         ← Security Agent  (real OpenAI or mock)
│   └── validator.py        ← Validator Agent (real OpenAI or mock)
├── gitlab/
│   └── gitlab_api.py       ← GitLab REST API (real or mock)
├── templates/
│   └── dashboard.html      ← Live monitoring dashboard
├── .env                    ← Your API keys (never committed)
├── .env.example            ← Key template
└── requirements.txt
```

### Entity Relationship — Agent Data Flow

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│   CI Log     │───────▶│   Analyzer   │───────▶│    Fixer     │
│  (raw text)  │        │              │        │              │
└──────────────┘        │ error_type   │        │ code_before  │
                        │ severity     │        │ code_after   │
                        │ root_cause   │        │ shell_cmds   │
                        │ affected_file│        │ fix_type     │
                        │ confidence   │        └──────┬───────┘
                        └──────────────┘               │
                                                        ▼
                        ┌──────────────┐        ┌──────────────┐
                        │  Validator   │◀───────│   Security   │
                        │              │        │              │
                        │ passes       │        │ score /100   │
                        │ confidence   │        │ risk_level   │
                        │ verdict      │        │ findings[]   │
                        │ retry_hint   │        └──────────────┘
                        └──────┬───────┘
                               │ passes=true
                               ▼
                        ┌──────────────┐
                        │  GitLab API  │
                        │              │
                        │ branch       │
                        │ commit       │
                        │ merge request│
                        └──────────────┘
```

---

## 🚀 Quick Start

### 1️⃣ Clone & Install

```bash
git clone https://gitlab.com/your-username/agitic
cd agitic
pip install -r requirements.txt
```

### 2️⃣ Configure Keys

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
# ── OpenAI (for real AI analysis) ───────────────────────────
OPENAI_API_KEY=sk-...

# ── GitLab (for real branch/commit/MR) ──────────────────────
GITLAB_TOKEN=glpat-...
GITLAB_PROJECT_ID=12345678
GITLAB_URL=https://gitlab.com
```

> 💡 **No keys? No problem.** Leave them empty and Agitic runs in full mock mode — all agents work with hardcoded responses so you can explore the dashboard immediately.

| Keys configured | Mode |
|----------------|------|
| None | Full mock — works instantly |
| `OPENAI_API_KEY` only | Real AI analysis + mock GitLab |
| All three | Fully live — real AI + real MR |

**Where to get keys:**
- 🔑 OpenAI → [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- 🦊 GitLab Token → Profile → Access Tokens → scopes: `api`, `write_repository`
- 🆔 Project ID → GitLab project → Settings → General → top of page

### 3️⃣ Run

```bash
python app.py
```

Open **[http://localhost:4367](http://localhost:4367)** 🚀

### 4️⃣ Trigger Manually

```bash
curl -X POST http://localhost:4367/trigger \
  -H "Content-Type: application/json" \
  -d '{"log": "ModuleNotFoundError: No module named '\''requests'\''"}'
```

---

## 📸 Screenshots

### Dashboard Overview
![Dashboard Overview](./Screenshot%202026-03-22%20213418.png)

### Agent Flow Running
![Agent Flow Running](./Screenshot%202026-03-22%20220418.png)

### Result Drawer — Analysis, Fix, Security, MR
![Result Drawer](./Screenshot%202026-03-22%20220429.png)

---

## 🔗 GitLab Webhook Setup

To trigger automatically on every real CI failure:

1. Go to your GitLab project → **Settings → Webhooks**
2. Set URL: `http://your-public-host:4367/webhook`
3. Check: ✅ **Pipeline events**
4. Click **Save**

> 💡 **Local dev?** Use [ngrok](https://ngrok.com) to expose localhost:
> ```bash
> ngrok http 4367
> # Paste the https://xxx.ngrok.io URL into GitLab
> ```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Live dashboard |
| `POST` | `/trigger` | Manual trigger — body: `{"log": "..."}` |
| `POST` | `/webhook` | GitLab pipeline webhook receiver |
| `GET` | `/api/runs` | All run history as JSON |
| `GET` | `/api/runs/<run_id>` | Single run details |

---

## 🧪 Built-in Test Scenarios

Click any sample in the dashboard to load a real-world error log:

| Sample | Error | Severity | Retry? |
|--------|-------|----------|--------|
| 📦 Module Error | `ModuleNotFoundError` | Medium | No — passes first try |
| 🗄️ DB Connection | `OperationalError` | Critical | No — passes first try |
| 🛡️ Security CVE | `CVE-2021-23337` | Critical | Yes — security score too low |
| 🔴 Syntax Error | `SyntaxError` | High | No — passes first try |

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

Built with 🤖 by humans who got tired of fixing the same CI errors over and over.

</div>
