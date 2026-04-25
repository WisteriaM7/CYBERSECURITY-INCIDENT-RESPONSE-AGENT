# 🛡️ Cybersecurity Incident Response Agent

A Streamlit app where three AI agents collaboratively triage, analyse, and recommend response actions for cybersecurity incidents — powered by a local LLM via Ollama.

## Agents (Chained Pipeline)

| Agent | Role |
|---|---|
| 🔍 **Log Parser** | Extracts events timeline, IoCs, anomalies, and affected assets from raw logs |
| 🕵️ **Threat Intelligence** | Classifies attack type, maps to MITRE ATT&CK, assesses severity & blast radius |
| 🔒 **Containment Advisor** | Recommends immediate actions, containment, eradication, recovery, and notifications |

Each agent receives the output of the previous one — building an increasingly rich analysis.

---

## Project Structure

```
ir_agent/
├── app.py                          # Streamlit UI
├── agents.py                       # Agent prompts + chained runner
├── log_utils.py                    # File reader (TXT, LOG, CSV, JSON)
├── storage.py                      # Save/load incidents as JSON
├── ollama_client.py                # Ollama HTTP client
├── requirements.txt
├── sample_logs/
│   └── brute_force_and_exfil.log  # Ready-to-use test log
└── incidents/                      # Auto-created, stores JSON results
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and run Ollama

```bash
# Download from https://ollama.com
ollama pull llama3      # or mistral, phi3, gemma2, etc.
ollama serve
```

### 3. Run the app

```bash
streamlit run app.py
```

---

## How to Use

1. **Upload a log file** (TXT, LOG, CSV, JSON) or **paste log text** directly
2. Set **incident context** in the sidebar (org, environment, severity)
3. Select which **agents** to run
4. Click **🚨 Run Incident Analysis**
5. View the full report: parsed events → threat intel → containment plan
6. All incidents are saved and visible in **Past Incidents**

---

## Quick Test

Use the included sample log to try the full pipeline immediately:

1. Upload `sample_logs/brute_force_and_exfil.log`
2. Set Environment: **Production**, Severity: **Critical**
3. Run all three agents

The sample log simulates: SSH brute force → credential compromise → privilege escalation → data exfiltration → backdoor installation.

---

## Supported Log Formats

| Format | How it's handled |
|---|---|
| `.txt` / `.log` | Read as-is |
| `.csv` | Parsed into `key=value` lines per row |
| `.json` | Flattened into readable key=value format |

---

## Notes

- Agents are **chained**: each agent sees the output of all previous agents
- Large logs are truncated to ~6,000 characters to fit model context windows
- All incident reports are stored in `incidents/` as JSON
- No internet or API keys required — fully local via Ollama
- Recommended model: `llama3` or `mistral` for best security reasoning
