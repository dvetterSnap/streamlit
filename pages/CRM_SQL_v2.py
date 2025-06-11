import streamlit as st
import requests
import os
import json

# Load environment variables
URL = os.getenv("SL_CRM_SQL_TASK_URL", "https://elastic.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/Dylan%20Vetter/Intuit/Snowflake%20Agent%20Task")
BEARER_TOKEN = os.getenv("SL_CRM_SQL_TASK_TOKEN", "1234")
timeout = int(os.getenv("SL_TASK_TIMEOUT", "1000"))
page_title = os.getenv("CRM_SQL_PAGE_TITLE", "CRM Agent")
title = os.getenv("CRM_SQL_TITLE", "CRM Agent")

# Page config
st.set_page_config(page_title=page_title)
st.title(title)

st.markdown(
    """  
    ### Ask a question about CRM data
    Example Questions:
    - What accounts are in New York?
    - What are my 3 top opportunities?
    - What campaigns are completed?
    """
)

if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = ""

def submit_prompt():
    st.session_state.submitted_prompt = st.session_state.current_prompt
    st.session_state.current_prompt = ""

# Display chat thread first
for pair in st.session_state.qa_history:
    with st.chat_message("user"):
        st.markdown(f"**{pair['question']}**")
    with st.chat_message("assistant"):
        st.markdown(pair["response"])

# Chat input stays at bottom
st.chat_input("Ask a question", key="current_prompt", on_submit=submit_prompt)

# Handle submission
if "submitted_prompt" in st.session_state:
    prompt = st.session_state.submitted_prompt
    del st.session_state.submitted_prompt

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            data = {"prompt": prompt}
            headers = {
                'Authorization': f'Bearer {BEARER_TOKEN}',
                'Content-Type': 'application/json'
            }

            try:
                response = requests.post(
                    url=URL,
                    json=data,
                    headers=headers,
                    timeout=timeout,
                    verify=False
                )

                if response.status_code == 200:
                    result = response.json()
                    reply = json.dumps(result, indent=2)
                    st.session_state.qa_history.append({
                        "question": prompt,
                        "response": reply
                    })
                    st.rerun()
                else:
                    st.error(f"❌ Error from SnapLogic API: {response.status_code}")
                    st.error(response.text)
            except Exception as e:
                st.error(f"❌ Exception occurred: {e}")
