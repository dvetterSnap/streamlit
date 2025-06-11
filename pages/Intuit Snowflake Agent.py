import streamlit as st
import requests
import time
import os
import json

# Load environment variables using os
URL = os.getenv("SL_SF_TASK_URL", "https://elastic.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/Dylan%20Vetter/Intuit/Snowflake%20Agent%20Task")
BEARER_TOKEN = os.getenv("SL_SF_TASK_TOKEN", "1234")
timeout = int(os.getenv("SL_TASK_TIMEOUT", "1000"))
page_title = os.getenv("SF_PAGE_TITLE", "Intuit Snowflake Agent")
title = os.getenv("SF_TITLE", "Intuit Snowflake Agent")

def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)

def render_json_as_bullets(json_obj, indent=0):
    """Recursively render a dict or list as Markdown bullets."""
    md = ""
    prefix = "    " * indent + "- "
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            if isinstance(v, (dict, list)):
                md += f"{prefix}**{k}:**\n" + render_json_as_bullets(v, indent + 1)
            else:
                md += f"{prefix}**{k}:** {v}\n"
    elif isinstance(json_obj, list):
        for idx, item in enumerate(json_obj):
            md += f"{prefix}{idx + 1}.\n" + render_json_as_bullets(item, indent + 1)
    else:
        md += f"{prefix}{json_obj}\n"
    return md

st.set_page_config(page_title=page_title)
st.title(title)

st.markdown(
    """  
    ### This is a Snowflake Agent that allows Intuit users to gather information using Natural Language
    Example Questions
    - Show me opportunities with amount over 500000 with their related account details.
    - What campaigns are completed and what were their performance metrics? Include names 
    - How many tax payers missed the deadline in 2024?
    """
)

if "SF_messages" not in st.session_state:
    st.session_state.SF_messages = []

for message in st.session_state.SF_messages:
    with st.chat_message(message["role"]):
        if message["content"].startswith("```json"):
            # Old format fallback
            st.markdown(message["content"])
        else:
            st.markdown(message["content"])

prompt = st.chat_input("Ask me anything")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.SF_messages.append({"role": "user", "content": prompt})
    with st.spinner("Working..."):
        try:
            data = {"prompt": prompt}
            headers = {
                'Authorization': f'Bearer {BEARER_TOKEN}'
            }
            response = requests.post(
                url=URL,
                json=data,
                headers=headers,
                timeout=timeout,
                verify=False
            )
            if response.status_code == 200:
                result = response.json()
                bullet_md = render_json_as_bullets(result)
                st.session_state.SF_messages.append({
                    "role": "assistant",
                    "content": bullet_md
                })
                st.rerun()
            else:
                st.error(f"❌ Error from SnapLogic API: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")
