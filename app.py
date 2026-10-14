from pathlib import Path
import streamlit as st
import plotly.express as px

from src.pipeline import DEFAULT_DB, fetch_tickets, get_summary, load_tickets

st.set_page_config(page_title="Service Desk Analytics", page_icon="🎫", layout="wide")
st.title("IT Service Desk Ticket Automation & Analytics")
st.caption("Synthetic demonstration data — replace with an approved export before operational use.")

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Import ticket CSV", type=["csv"])
    if uploaded is not None:
        temp_path = Path("data/uploaded_tickets.csv")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_bytes(uploaded.getvalue())
        try:
            count = load_tickets(temp_path, DEFAULT_DB)
            st.success(f"Imported {count} tickets")
        except Exception as exc:
            st.error(f"Import failed: {exc}")
    if st.button("Load bundled sample data", use_container_width=True):
        try:
            st.success(f"Loaded {load_tickets('data/tickets.csv', DEFAULT_DB)} tickets")
        except Exception as exc:
            st.error(str(exc))

if not DEFAULT_DB.exists():
    load_tickets("data/tickets.csv", DEFAULT_DB)

summary = get_summary()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total tickets", f"{summary['total']:,}")
c2.metric("Open / in progress", f"{summary['open']:,}")
c3.metric("Resolved SLA breaches", f"{summary['breached']:,}")
c4.metric("Avg. resolution (hours)", f"{summary['avg_resolution_hours']:.1f}")

df = fetch_tickets()
if df.empty:
    st.info("No tickets loaded yet.")
    st.stop()

left, right = st.columns(2)
with left:
    team_counts = df.groupby("team", dropna=False).size().reset_index(name="tickets")
    st.plotly_chart(px.bar(team_counts, x="team", y="tickets", title="Tickets by team"), use_container_width=True)
with right:
    status_counts = df.groupby("status", dropna=False).size().reset_index(name="tickets")
    st.plotly_chart(px.pie(status_counts, names="status", values="tickets", title="Ticket status mix"), use_container_width=True)

st.subheader("Triage queue")
filter_col1, filter_col2, filter_col3 = st.columns(3)
teams = ["All"] + sorted(df["team"].dropna().unique().tolist())
statuses = ["All"] + sorted(df["status"].dropna().unique().tolist())
priorities = ["All"] + sorted(df["priority"].dropna().unique().tolist())
team_choice = filter_col1.selectbox("Team", teams)
status_choice = filter_col2.selectbox("Status", statuses)
priority_choice = filter_col3.selectbox("Priority", priorities)

filtered = df.copy()
if team_choice != "All":
    filtered = filtered[filtered["team"] == team_choice]
if status_choice != "All":
    filtered = filtered[filtered["status"] == status_choice]
if priority_choice != "All":
    filtered = filtered[filtered["priority"] == priority_choice]

columns = ["ticket_id", "created_at", "team", "category", "description", "status", "priority",
           "sla_hours", "resolution_hours", "sla_breached", "assignee"]
st.dataframe(filtered[columns], use_container_width=True, hide_index=True)
st.download_button("Download filtered tickets", filtered.to_csv(index=False), "filtered_tickets.csv", "text/csv")
