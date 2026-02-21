import streamlit as st

st.set_page_config(
    page_title="SnapLogic Pitch Deck Generator",
    page_icon="⚡",
    layout="centered"
)

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0f2e 0%, #0d2352 50%, #0a1a3e 100%);
  }
  [data-testid="stHeader"] { background: transparent; }
  [data-testid="stSidebar"] { display: none; }
  .main .block-container { max-width: 780px; padding-top: 2rem; padding-bottom: 2rem; }
  h1, h2, h3, label, p, .stMarkdown { color: #ffffff !important; }
  .logo-bar { display: flex; align-items: center; gap: 14px; margin-bottom: 8px; }
  .logo-icon {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, #00d4ff, #0077ff);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; font-weight: 900; color: white;
  }
  .logo-title { font-size: 22px; font-weight: 700; color: #fff; }
  .logo-sub   { font-size: 13px; color: rgba(255,255,255,0.5); margin-top: 2px; }
  .badge {
    display: inline-block; padding: 4px 12px;
    background: rgba(0,212,255,0.12); border: 1px solid rgba(0,212,255,0.3);
    border-radius: 20px; font-size: 11px; color: #00d4ff; font-weight: 600;
    letter-spacing: 0.5px; margin-bottom: 24px;
  }
  textarea {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important; color: #ffffff !important;
  }
  .stSelectbox > div > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important; color: #fff !important;
  }
  .stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #00d4ff 0%, #0077ff 100%) !important;
    color: white !important; font-weight: 700 !important; font-size: 16px !important;
    border: none !important; border-radius: 12px !important; padding: 14px !important; margin-top: 12px !important;
  }
  .divider { border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0; }
  .next-steps {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px; padding: 16px 20px; margin-top: 16px;
  }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="logo-bar">
  <div class="logo-icon">SL</div>
  <div>
    <div class="logo-title">SnapLogic Pitch Deck Generator</div>
    <div class="logo-sub">Fill in details → copy prompt → paste into Claude.ai → download PPTX</div>
  </div>
</div>
<div class="badge">✦ Powered by Claude.ai</div>
""", unsafe_allow_html=True)

customer = st.text_area(
    "🏢 About the Customer",
    placeholder="e.g. Acme Corp is a Fortune 500 retail company with 200+ locations. They struggle with siloed data across SAP, Salesforce, and legacy ERPs. Their IT team of 40 spends most time on manual integrations...",
    height=140
)

snaplogic = st.text_area(
    "⚡ How SnapLogic Can Help",
    placeholder="e.g. SnapLogic can unify their data pipelines with pre-built Snaps for SAP and Salesforce, reduce integration time by 80%, enable real-time inventory visibility, and empower citizen integrators...",
    height=140
)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    slide_count = st.selectbox("📊 Slide Count", ["6 Slides (Quick)", "8 Slides (Standard)", "10 Slides (Full)"], index=1)
with col2:
    tone = st.selectbox("🎯 Tone", ["Executive", "Technical", "Consultative"], index=2)

slide_num = int(slide_count.split()[0])
tone_val  = tone.lower()

def build_prompt(customer, snaplogic, slide_count, tone):
    return f"""Please create a SnapLogic pitch deck PowerPoint file for me and provide it as a downloadable .pptx file.

---
CUSTOMER INFORMATION:
{customer}

HOW SNAPLOGIC CAN HELP:
{snaplogic}
---

REQUIREMENTS:
- {slide_count} slides, {tone} tone
- Professional dark navy/cyan design: navy #0A1628, blue #0A4FA8, cyan #00D4FF
- All content must be 100% specific to this customer — no generic filler
- Slide types: Title, Customer Challenges, SnapLogic Solution, Business Value (3 large bold ROI stats e.g. "80%", "3x", "40h saved"), Platform Capabilities, Use Cases, Why SnapLogic, Next Steps with CTA
- Every slide needs colored header bars, shapes, and visual layout — no plain text slides
- Please generate the .pptx file and provide it as a download"""

if st.button("✦ Generate My Claude Prompt"):
    if not customer.strip() or not snaplogic.strip():
        st.error("⚠️ Please fill in both fields before continuing.")
    else:
        st.session_state["prompt"] = build_prompt(customer, snaplogic, slide_num, tone_val)

if "prompt" in st.session_state:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📋 Copy this → paste into Claude.ai → get your PPTX")
    st.code(st.session_state["prompt"], language=None)

    st.markdown("""
    <div class="next-steps">
      <div style="color:#00d4ff;font-weight:700;font-size:12px;letter-spacing:0.5px;margin-bottom:10px;">💡 NEXT STEPS</div>
      <div style="color:rgba(255,255,255,0.65);font-size:13px;line-height:2.2;">
        1️⃣ &nbsp;Click <strong style="color:white">Copy</strong> on the prompt above<br>
        2️⃣ &nbsp;Open <strong style="color:white">claude.ai</strong> in a new tab<br>
        3️⃣ &nbsp;Paste &amp; send — Claude builds your deck<br>
        4️⃣ &nbsp;Download the <code style="color:#00d4ff">.pptx</code> file directly from Claude 🎉
      </div>
    </div>
    """, unsafe_allow_html=True)
