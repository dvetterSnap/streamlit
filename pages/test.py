import streamlit as st
import pandas as pd
import time
import requests
from urllib.parse import quote

# -----------------------------
# Configuration Constants
# -----------------------------
CONFIG = {
    'MIN_WINDOW_DAYS': 1,
    'MAX_WINDOW_DAYS': 60,
    'DEFAULT_WINDOW_DAYS': 21,
    'AUTO_APPROVE_THRESHOLD': 250,
    'MAX_QTY_LIMIT': 10000,
    'API_TIMEOUT': 30
}

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="PO Creation Workbench", layout="wide", page_icon="🛒")

# -----------------------------
# Custom Styling
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
        font-weight: 600;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Mock data for the demo
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
st.sidebar.markdown("# 🔧 Configuration")

with st.sidebar.expander("🎯 Filters", expanded=True):
    location_filter = st.multiselect(
        "📍 Location", 
        options=sorted(st.session_state.recs["location"].unique()), 
        default=[]
    )
    supplier_filter = st.multiselect(
        "🏭 Supplier", 
        options=sorted(st.session_state.recs["supplier"].unique()), 
        default=[]
    )
    window_days = st.slider(
        "📅 Shortage window (days)", 
        CONFIG['MIN_WINDOW_DAYS'], 
        CONFIG['MAX_WINDOW_DAYS'], 
        CONFIG['DEFAULT_WINDOW_DAYS']
    )

with st.sidebar.expander("⚙️ System Settings", expanded=True):
    erp = st.selectbox("💼 ERP System", ["SAP", "NetSuite"], index=0)
    env = st.selectbox("🌐 Environment", ["Dev", "QA", "Prod"], index=0)

with st.sidebar.expander("🔒 Safety Controls", expanded=False):
    auto_approve_small = st.toggle(
        "Auto-approve tiny orders (< 250 units)", 
        value=False
    )
    dry_run = st.toggle("🧪 Dry run (do not call ERP)", value=True)

# Build accountName from ERP + Environment
if erp == "NetSuite":
    accountName_raw = "../../shared/NS_Token account_2018_2_TimToken vld 10.25.2023"
else:
    ACCOUNT_MAP = {"Dev": "sap_dev", "QA": "sap_qa", "Prod": "sap_prod"}
    accountName_raw = ACCOUNT_MAP.get(env, "sap_dev")

accountName_param = quote(accountName_raw, safe="")

st.sidebar.divider()
st.sidebar.caption("💡 Approve posts one JSON payload to a SnapLogic pipeline")

if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.session_state.recs = load_recommendations()
    st.toast("Data refreshed!", icon="✅")
    st.rerun()

# -----------------------------
# Header stats
# -----------------------------
st.title("🛒 Review & Approve Suggested POs")

col1, col2, col3 = st.columns(3)
pending_count = int((st.session_state.recs["status"] == "Pending").sum())
approved_count = len([s for s in st.session_state.recs["status"] if "Created" in str(s)])
failed_count = int((st.session_state.recs["status"] == "Failed").sum())

with col1:
    st.metric("📋 Pending Recommendations", pending_count)
with col2:
    st.metric("✅ Approved Today", approved_count)
with col3:
    st.metric("⚠️ Failures (24h)", failed_count)

st.divider()

# -----------------------------
# Filtered table
# -----------------------------
df = st.session_state.recs.copy()
if location_filter:
    df = df[df["location"].isin(location_filter)]
if supplier_filter:
    df = df[df["supplier"].isin(supplier_filter)]

st.subheader("📦 Recommendations Queue")

selection = st.data_editor(
    df,
    column_config={
        "rec_id": st.column_config.TextColumn("🆔 Rec ID", width="small"),
        "sku": st.column_config.TextColumn("📦 SKU", width="medium"),
        "location": st.column_config.TextColumn("📍 Location", width="small"),
        "shortage_date": st.column_config.DateColumn("📅 Shortage Date", width="medium"),
        "recommended_qty": st.column_config.NumberColumn(
            "🔢 Recommended Qty", 
            format="%d units",
            width="small"
        ),
        "supplier": st.column_config.TextColumn("🏭 Supplier", width="medium"),
        "forecast_gap": st.column_config.NumberColumn("📊 Gap", format="%d units", width="small"),
        "reason": st.column_config.TextColumn("💡 Reason", width="large"),
        "status": st.column_config.TextColumn("✓ Status", width="medium"),
    },
    hide_index=True,
    use_container_width=True,
    num_rows="dynamic",
    disabled=True,
)

# Row chooser
st.divider()
left, right = st.columns([3, 1])
with left:
    if len(df) > 0:
        chosen_id = st.selectbox(
            "🔍 Select a recommendation to review", 
            options=df["rec_id"].tolist()
        )
        chosen = df[df["rec_id"] == chosen_id].iloc[0].to_dict()
    else:
        st.info("No recommendations match your filters")
        st.stop()

with right:
    st.download_button(
        "📥 Download CSV", 
        data=df.to_csv(index=False), 
        file_name="po_recommendations.csv",
        use_container_width=True
    )

# -----------------------------
# Detail & approval panel
# -----------------------------
with st.container(border=True):
    st.subheader("📄 Recommendation Details")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 SKU", chosen["sku"])
    c2.metric("📍 Location", chosen["location"])
    c3.metric("📅 Shortage Date", chosen["shortage_date"])
    c4.metric("🔢 Recommended Qty", int(chosen["recommended_qty"]))

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write(f"**🏭 Supplier:** {chosen['supplier']}")
        st.write(f"**💡 Reason:** {chosen['reason']}")
    with col_b:
        st.write(f"**📊 Forecast Gap:** {int(chosen['forecast_gap'])} units")
        st.write(f"**✓ Status:** {chosen['status']}")

    st.divider()

    # Validation warnings
    warnings = []
    if chosen["recommended_qty"] > 5000:
        warnings.append("⚠️ Large quantity order - requires additional approval")
    if chosen["on_hand"] < chosen["safety_stock"] * 0.2:
        warnings.append("🔴 Critical stock level - expedited shipping recommended")

    if warnings:
        for w in warnings:
            st.warning(w)

    st.markdown("### 📝 Business Justification")
    justification = st.text_area(
        "Justification",
        value=f"Auto-generated: {chosen['reason']} (gap {int(chosen['forecast_gap'])} units)",
        height=90,
        label_visibility="collapsed"
    )

    st.markdown("### ✅ Policy Checks")
    check_col1, check_col2, check_col3 = st.columns(3)
    with check_col1:
        st.checkbox("✓ Supplier is preferred", value=True, disabled=True)
    with check_col2:
        st.checkbox("✓ Within buyer authority", value=True, disabled=True)
    with check_col3:
        st.checkbox("✓ Delivery window OK", value=True, disabled=True)

    pc_ok = chosen["recommended_qty"] >= 0 and chosen["recommended_qty"] <= CONFIG['MAX_QTY_LIMIT']

    st.divider()
    colA, colB, colC = st.columns([2, 2, 3])

    def build_payload(row):
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
        approve = st.button(
            "✅ Approve & Create PO", 
            type="primary", 
            use_container_width=True, 
            disabled=not pc_ok or chosen["status"] != "Pending"
        )
    with colB:
        reject = st.button(
            "❌ Reject", 
            use_container_width=True,
            disabled=chosen["status"] != "Pending"
        )
    with colC:
        if dry_run:
            st.caption("🧪 Dry Run Mode Active")
        else:
            st.caption("⚡ Live Mode: " + erp)

    if approve:
        payload = build_payload(chosen)
        with st.status("🔄 Creating PO via SnapLogic…", expanded=True) as status:
            st.write("📤 Posting payload...")
            time.sleep(0.8)
            
            try:
                endpoint_base = "https://elastic.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/"
                endpoint_path = "Dylan%20Vetter/DemoBucket/Amazon%20PO%20creation%20Task"
                SL_ENDPOINT = f"{endpoint_base}{endpoint_path}?bearer_token=12345&accountName={accountName_param}"

                res = requests.post(SL_ENDPOINT, json=payload, timeout=CONFIG['API_TIMEOUT'])

                if 200 <= res.status_code < 300:
                    po_number = f"PO-{chosen['rec_id']}-{int(time.time())}"
                    st.success(f"✅ PO Created: {po_number}")
                    status.update(label="✅ PO created successfully!", state="complete")
                    
                    st.session_state.recs.loc[
                        st.session_state.recs["rec_id"] == chosen["rec_id"], "status"
                    ] = f"Created: {po_number}"
                    st.toast("🎉 PO created successfully!", icon="✅")
                    time.sleep(1)
                    st.rerun()
                else:
                    raise Exception(f"Non-2xx status code: {res.status_code}")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.recs.loc[
                    st.session_state.recs["rec_id"] == chosen["rec_id"], "status"
                ] = "Failed"
                status.update(label="❌ Failed", state="error")

    if reject:
        st.session_state.recs.loc[
            st.session_state.recs["rec_id"] == chosen["rec_id"], "status"
        ] = "Rejected"
        st.toast(f"🚫 Recommendation {chosen['rec_id']} rejected", icon="❌")
        st.rerun()

# -----------------------------
# Activity log
# -----------------------------
st.divider()
st.subheader("📜 Activity Log")
log_df = st.session_state.recs[["rec_id", "sku", "location", "status"]].copy()
st.dataframe(log_df, use_container_width=True, hide_index=True)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 Powered by SnapLogic")
with col2:
    st.caption(f"📅 {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
with col3:
    st.caption(f"🌐 {env} | {erp}")
