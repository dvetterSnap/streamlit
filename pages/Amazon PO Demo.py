import streamlit as st
import pandas as pd
import time
import requests
from urllib.parse import quote

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="PO Creation Workbench", layout="wide", page_icon="🛒")

# -----------------------------
# Custom Styling (SAFE ADDITIONS)
# -----------------------------
st.markdown("""
    <style>
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    
    .stButton>button {
        border-radius: 8px;
        height: 3em;
        font-weight: 500;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Mock data for the demo (replace with your model output)
# -----------------------------
@st.cache_data
def load_recommendations():
    data = [
        {
            "rec_id": "R-1001",
            "sku": "ABC123",
            "sku_id" :  "16",
            "location": "DAL-DC",
            "shortage_date": "11/18/2025",
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
            "sku_id" :  "18",
            "location": "RNO-DC",
            "shortage_date": "11/12/2025",
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
            "sku_id" :  "15",
            "location": "PHX-DC",
            "shortage_date": "11/20/2025",
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
st.sidebar.header("🔧 Filters & Configuration")

location_filter = st.sidebar.multiselect(
    "📍 Location", options=sorted(st.session_state.recs["location"].unique()), default=[]
)
supplier_filter = st.sidebar.multiselect(
    "🏭 Supplier", options=sorted(st.session_state.recs["supplier"].unique()), default=[]
)
window_days = st.sidebar.slider("📅 Shortage window (days)", 1, 60, 21)
auto_approve_small = st.sidebar.toggle("✅ Auto-approve tiny orders (< 250 units)", value=False)

erp = st.sidebar.selectbox("💼 ERP System", ["SAP", "NetSuite"], index=0)
env = st.sidebar.selectbox("🌐 Environment", ["Dev", "QA", "Prod"], index=0)

# Build accountName from ERP + Environment
if erp == "NetSuite":
    accountName_raw = "../../shared/NS_Token account_2018_2_TimToken vld 10.25.2023"
else:
    ACCOUNT_MAP = {"Dev": "sap_dev", "QA": "sap_qa", "Prod": "sap_prod"}
    accountName_raw = ACCOUNT_MAP.get(env, f"sap_{env.lower()}")

# URL-encode for safe query param (encode slashes and spaces)
accountName_param = quote(accountName_raw, safe="")

dry_run = st.sidebar.toggle("🧪 Dry run (do not call ERP)", value=True)

st.sidebar.divider()
st.sidebar.caption("💡 Approve posts one JSON payload to a SnapLogic pipeline which creates the PO in the ERP and returns a status.")

if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# -----------------------------
# Header stats
# -----------------------------
st.title("🛒 Review & Approve Suggested POs")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📋 Pending recommendations", int((st.session_state.recs["status"] == "Pending").sum()))
with col2:
    approved_today = len([s for s in st.session_state.recs["status"] if "Created" in str(s)])
    st.metric("✅ Auto-approved today", approved_today)
with col3:
    failures = int((st.session_state.recs["status"] == "Failed").sum())
    st.metric("⚠️ Failures (24h)", failures)

# -----------------------------
# Filtered table
# -----------------------------
df = st.session_state.recs.copy()
if location_filter:
    df = df[df["location"].isin(location_filter)]
if supplier_filter:
    df = df[df["supplier"].isin(supplier_filter)]

# Selection model
st.subheader("📦 Recommendations queue")
selection = st.data_editor(
    df,
    column_config={
        "rec_id": st.column_config.Column("🆔 Rec ID", disabled=True),
        "sku": st.column_config.Column("📦 SKU", disabled=True),
        "location": st.column_config.Column("📍 Location", disabled=True),
        "shortage_date": st.column_config.Column("📅 Shortage Date", disabled=True),
        "recommended_qty": st.column_config.NumberColumn("🔢 Recommended Qty", disabled=True),
        "supplier": st.column_config.Column("🏭 Supplier", disabled=True),
        "forecast_gap": st.column_config.NumberColumn("📊 Forecast Gap", disabled=True),
        "reason": st.column_config.Column("💡 Reason / Driver", disabled=True),
        "status": st.column_config.Column("✓ Status", disabled=True),
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
    chosen_id = st.selectbox("🔍 Select a recommendation to review", options=df["rec_id"].tolist())
    chosen = df[df["rec_id"] == chosen_id].iloc[0].to_dict()

with right:
    st.download_button("📥 Download queue (CSV)", data=df.to_csv(index=False), file_name="po_recommendations.csv")

# -----------------------------
# Detail & approval panel
# -----------------------------
with st.container(border=True):
    st.subheader("📄 Recommendation details")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 SKU", chosen["sku"])
    c2.metric("📍 Location", chosen["location"])
    c3.metric("📅 Shortage date", chosen["shortage_date"])
    c4.metric("🔢 Rec qty", int(chosen["recommended_qty"]))

    st.write(
        f"**🏭 Supplier:** {chosen['supplier']}  |  **💡 Reason:** {chosen['reason']}  |  **📊 Forecast gap:** {int(chosen['forecast_gap'])}"
    )

    # Add warnings
    warnings = []
    if chosen["recommended_qty"] > 5000:
        warnings.append("⚠️ Large quantity order - requires additional approval")
    if chosen["on_hand"] < chosen["safety_stock"] * 0.2:
        warnings.append("🔴 Critical stock level - expedited shipping recommended")
    
    if warnings:
        st.markdown("---")
        for w in warnings:
            st.warning(w)

    st.markdown("---")
    st.markdown("**📝 Business justification**")
    justification = st.text_area(
        "",
        value=f"Auto-generated: {chosen['reason']} (gap {int(chosen['forecast_gap'])})",
        height=90,
    )

    st.markdown("**✅ Policy checks**")
    pc_ok = chosen["recommended_qty"] >= 0 and chosen["recommended_qty"] <= 10000
    st.checkbox("✓ Supplier is preferred", value=True, disabled=True)
    st.checkbox("✓ Within buyer authority limit", value=True, disabled=True)
    st.checkbox("✓ Delivery window acceptable", value=True, disabled=True)

    st.divider()
    colA, colB, colC = st.columns([1,1,2])

    def build_payload(row: dict) -> dict:
        return {
            "rec_id": row["rec_id"],
            "sku": row["sku"],
            "sku_id": row["sku_id"],
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
        approve = st.button("✅ Approve & Create PO", type="primary", use_container_width=True, disabled=not pc_ok)
    with colB:
        reject = st.button("❌ Reject", use_container_width=True)
    with colC:
        if dry_run:
            st.caption("🧪 **Dry Run Mode:** No actual PO will be created")
        else:
            st.caption(f"⚡ **Live Mode:** Approving will call the SnapLogic pipeline")

    if approve:
        payload = build_payload(chosen)
        with st.status("🔄 Creating PO via SnapLogic…", expanded=True) as status:
            st.write("📤 Posting payload to SnapLogic pipeline endpoint…")
            time.sleep(0.6)
            try:
                # Keep bearer token; append encoded accountName derived from ERP + Environment rules
                SL_ENDPOINT = (
                    "https://elastic.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/"
                    "Dylan%20Vetter/DemoBucket/Amazon%20PO%20creation%20Task"
                    f"?bearer_token=12345&accountName={accountName_param}"
                )

                res = requests.post(SL_ENDPOINT, json=payload, timeout=30)

                # Success rule: any 2xx is success; no response parsing
                if 200 <= res.status_code < 300:
                    po_number = "PO-CREATED"
                    st.write({
                        "endpoint": SL_ENDPOINT,
                        "status_code": res.status_code,
                        "accountName_raw": accountName_raw
                    })
                    status.update(label="✅ PO created", state="complete")
                else:
                    raise Exception(f"Non-2xx status code: {res.status_code}")

            except Exception as e:
                st.error(f"❌ Failed to create PO: {e}")
                st.session_state.recs.loc[
                    st.session_state.recs["rec_id"] == chosen["rec_id"], "status"
                ] = "Failed"
                st.toast("PO creation failed", icon="❌")
                status.update(label="Failed", state="error")
                st.stop()

        # Update in-memory table on success
        st.session_state.recs.loc[
            st.session_state.recs["rec_id"] == chosen["rec_id"], "status"
        ] = f"Created: {po_number}"
        st.toast("🎉 PO created", icon="✅")
        st.rerun()

    if reject:
        st.session_state.recs.loc[
            st.session_state.recs["rec_id"] == chosen["rec_id"], "status"
        ] = "Rejected"
        st.toast(f"🚫 Recommendation {chosen['rec_id']} rejected", icon="❌")
        st.rerun()

# -----------------------------
# Activity log tab (simple)
# -----------------------------
st.subheader("📜 Activity log")
log_df = st.session_state.recs.copy()[["rec_id", "sku", "location", "status"]]
st.dataframe(log_df, use_container_width=True, hide_index=True)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 Powered by SnapLogic")
with col2:
    st.caption(f"📅 Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
with col3:
    st.caption(f"🌐 Environment: {env} | ERP: {erp}")

# -----------------------------
# Notes for integration
# -----------------------------
with st.expander("🔧 Integration notes (hide in final demo)"):
    st.markdown(
        """
        - For NetSuite (any environment) the `accountName` param is a shared token value and is URL-encoded.
        - For SAP, `accountName` is mapped by environment (sap_dev, sap_qa, sap_prod).
        - Success is determined solely by HTTP 2xx status; the response body is not parsed.
        """
    )
