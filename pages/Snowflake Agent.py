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

# Initialize session state
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

# Show the Q&A thread
for pair in st.session_state.qa_history:
    st.markdown(f"**You:** {pair['question']}")
    st.code(pair["response"], language="json")

# Input
prompt = st.text_input("Ask a question")

# Submit
if prompt:
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
                pretty_result = json.dumps(result, indent=2)

                # Append to thread
                st.session_state.qa_history.append({
                    "question": prompt,
                    "response": pretty_result
                })

                st.rerun()  # rerun to immediately display updated thread
            else:
                st.error(f"❌ Error from SnapLogic API: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")
