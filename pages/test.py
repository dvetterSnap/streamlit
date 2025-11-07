import streamlit as st
import pandas as pd
import time
import requests

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="PO Creation Workbench", layout="wide")

# -----------------------------
# Mock data for the demo (replace with your model output)
# -----------------------------
@st.cache_data
def load_recommendations():
    data = [
        {
            "rec_id": "R-1001",
            "sku": "ABC123",
            "location": "DAL-DC",
            "shortage_date": "2025-11-18",
            "recommended_qty": 4500,
            "supplier": "Supplier A",
            "safety_stock": 3000,
            "on_hand": 1200,
            "inbound": 200,
            "forecast_gap": 3100,
            "reason": "Forecast < Safety Stock",
            "status": "Pending",
        },
        {
            "rec_id": "R-1002",
            "sku": "FGH987",
            "location": "RNO-DC",
            "shortage_date": "2025-11-22",
            "recommended_qty": 800,
            "supplier": "Supplier C",
            "safety_stock": 2000,
            "on_hand": 1600,
            "inbound": 0,
            "forecast_gap": 900,
            "reason": "Seasonal demand increase",
            "status": "Pending",
        },
        {
            "rec_id": "R-1003",
            "sku": "XYZ555",
            "location": "PHX-DC",
            "shortage_date": "2025-11-20",
            "recommended_qty": 1200,
            "supplier": "Supplier B",
            "safety_stock": 1500,
            "on_hand": 400,
            "inbound": 50,
            "forecast_gap": 1050,
            "reason": "Backorder depletion",
            "status": "Pending",
        },
    ]
    return pd.DataFrame(data)

if "recs" not in st.session_state:
    st.session_state.recs = load_recommendations()

# -----------------------------
# Sidebar filters & controls
# -----------------------------
st.sidebar.header("Filters")
location_filter = st.sidebar.multiselect(
    "Location", options=sorted(st.session_state.recs["location"].unique()), default=[]
)
supplier_filter = st.sidebar.multiselect(
    "Supplier", options=sorted(st.session_state.recs["supplier"].unique()), default=[]
)
window_days = st.sidebar.slider("Shortage window (days)", 1, 60, 21)
auto_approve_small = st.sidebar.toggle("Auto-approve tiny orders (< 250 units)", value=False)

erp = st.sidebar.selectbox("ERP System", ["SAP", "NetSuite"], index=0)

env = st.sidebar.selectbox("Environment", ["Dev", "QA", "Prod"], index=0)
dry_run = st.sidebar.toggle("Dry run (do not call ERP)", value=True)

st.sidebar.divider()
st.sidebar.caption("When Approve is clicked, we post a single JSON payload to a SnapLogic pipeline, which validates and creates the PO in the ERP, returning PO number & status.")

# -----------------------------
# Header stats
# -----------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Pending recommendations", int((st.session_state.recs["status"] == "Pending").sum()))
with col2:
    st.metric("Auto-approved today", 0)
with col3:
    st.metric("Failures (24h)", 0)

st.title("Review & Approve Suggested POs")

# -----------------------------
# Filtered table
# -----------------------------
df = st.session_state.recs.copy()
if location_filter:
    df = df[df["location"].isin(location_filter)]
if supplier_filter:
    df = df[df["supplier"].isin(supplier_filter)]

# Only show recs within window (mock: all are in-window)

# Selection model
st.subheader("Recommendations queue")
selection = st.data_editor(
    df,
    column_config={
        "rec_id": st.column_config.Column("Rec ID", disabled=True),
        "sku": st.column_config.Column("SKU", disabled=True),
        "location": st.column_config.Column("Location", disabled=True),
        "shortage_date": st.column_config.Column("Shortage Date", disabled=True),
        "recommended_qty": st.column_config.NumberColumn("Recommended Qty", disabled=True),
        "supplier": st.column_config.Column("Supplier", disabled=True),
        "forecast_gap": st.column_config.NumberColumn("Forecast Gap", disabled=True),
        "reason": st.column_config.Column("Reason / Driver", disabled=True),
        "status": st.column_config.Column("Status", disabled=True),
    },
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic",
    disabled=True,
)

# Row chooser
st.divider()
left, right = st.columns([2, 1])
with left:
    chosen_id = st.selectbox("Select a recommendation to review", options=df["rec_id"].tolist())
    chosen = df[df["rec_id"] == chosen_id].iloc[0].to_dict()

with right:
    st.download_button("Download queue (CSV)", data=df.to_csv(index=False), file_name="po_recommendations.csv")

# -----------------------------
# Detail & approval panel
# -----------------------------
with st.container(border=True):
    st.subheader("Recommendation details")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SKU", chosen["sku"])
    c2.metric("Location", chosen["location"])
    c3.metric("Shortage date", chosen["shortage_date"])
    c4.metric("Rec qty", int(chosen["recommended_qty"]))

    st.write(
        f"**Supplier:** {chosen['supplier']}  |  **Reason:** {chosen['reason']}  |  **Forecast gap:** {int(chosen['forecast_gap'])}"
    )

    st.markdown("**Business justification**")
    justification = st.text_area(
        "",
        value=f"Auto-generated: {chosen['reason']} (gap {int(chosen['forecast_gap'])})",
        height=90,
    )

    # Policy checks (mock)
    st.markdown("**Policy checks**")
    pc_ok = chosen["recommended_qty"] >= 0 and chosen["recommended_qty"] <= 10000
    st.checkbox("Supplier is preferred", value=True, disabled=True)
    st.checkbox("Within buyer authority limit", value=True, disabled=True)
    st.checkbox("Delivery window acceptable", value=True, disabled=True)

    st.divider()
    colA, colB, colC = st.columns([1,1,2])

    def build_payload(row: dict) -> dict:
        return {
            "rec_id": row["rec_id"],
            "sku": row["sku"],
            "location": row["location"],
            "shortage_date": row["shortage_date"],
            "recommended_qty": int(row["recommended_qty"]),
            "supplier": row["supplier"],
            "justification": justification,
            "erp": erp,
            "environment": env,
            "dry_run": dry_run,
        }

    with colA:
        approve = st.button("Approve & Create PO", type="primary", use_container_width=True, disabled=not pc_ok)
    with colB:
        reject = st.button("Reject", use_container_width=True)
    with colC:
        st.caption("Approving will call the SnapLogic pipeline and return a PO number on success.")

    if approve:
        payload = build_payload(chosen)
        with st.status("Creating PO via SnapLogic…", expanded=True) as status:
            st.write("Posting payload to SnapLogic pipeline endpoint…")
            time.sleep(0.6)
            # Call SnapLogic Ultra/Task endpoint
            try:
                SL_ENDPOINT = (
                    "https://elastic.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/"
                    "Dylan%20Vetter/DemoBucket/Amazon%20PO%20creation%20Task?bearer_token=12345"
                )
                res = requests.post(SL_ENDPOINT, json=payload, timeout=30)
                res.raise_for_status()
                # Try a few common field names for the PO number
                data = {}
                try:
                    data = res.json()
                except Exception:
                    data = {"raw": res.text}
                po_number = (
                    (data.get("po_number") if isinstance(data, dict) else None)
                    or (data.get("poNumber") if isinstance(data, dict) else None)
                    or (data.get("PO") if isinstance(data, dict) else None)
                    or "PO-UNKNOWN"
                )
                st.write({"payload": payload, "response": data})
                status.update(label="PO created", state="complete")
            except Exception as e:
                st.error(f"Failed to create PO: {e}")
                status.update(label="Failed", state="error")
                st.stop()
        # Update in-memory table
        st.session_state.recs.loc[st.session_state.recs["rec_id"] == chosen["rec_id"], "status"] = f"Created: {po_number}"
        st.toast(f"PO {po_number} created", icon="✅")
        st.rerun()

    if reject:
        st.session_state.recs.loc[st.session_state.recs["rec_id"] == chosen["rec_id"], "status"] = "Rejected"
        st.toast(f"Recommendation {chosen['rec_id']} rejected", icon="🚫")
        st.rerun()

# -----------------------------
# Activity log tab (simple)
# -----------------------------
st.subheader("Activity log")
log_df = st.session_state.recs.copy()[["rec_id", "sku", "location", "status"]]
st.dataframe(log_df, use_container_width=True, hide_index=True)

# -----------------------------
# Notes for integration
# -----------------------------
with st.expander("Integration notes (hide in final demo)"):
    st.markdown(
        """
        **Payload shape posted to SnapLogic** (example):
        ```json
        {
          "rec_id": "R-1001",
          "sku": "ABC123",
          "location": "DAL-DC",
          "shortage_date": "2025-11-18",
          "recommended_qty": 4500,
          "supplier": "Supplier A",
          "justification": "Forecast < Safety Stock (gap 3100)",
          "environment": "Dev",
          "dry_run": true
        }
        ```
        - Replace the mocked `requests.post` with your SnapLogic pipeline trigger (Ultra Task or API endpoint).
        - Store endpoint and tokens in `st.secrets` for the demo.
        """
    )
