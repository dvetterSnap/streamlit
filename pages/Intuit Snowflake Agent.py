import streamlit as st
import requests
import time
import os
import json

# Load environment variables using os
URL = os.getenv("SL_CRM_SQL_TASK_URL", "https://elastic.snaplogic.com/api/1/rest/slsched/feed/ConnectFasterInc/Dylan%20Vetter/Intuit/Snowflake%20Agent%20Task")
BEARER_TOKEN = os.getenv("SL_CRM_SQL_TASK_TOKEN", "1234")
timeout = int(os.getenv("SL_TASK_TIMEOUT", "1000"))
page_title = os.getenv("CRM_SQL_PAGE_TITLE", "CRM Agent")
title = os.getenv("CRM_SQL_TITLE", "CRM Agent")

def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)

st.set_page_config(page_title=page_title)
st.title(title)

st.markdown(
    """  
    ### This is a CRM Agent that allows employees to interact with Production Systems using Natural Language
    Example Questions
    - What accounts are in New York?
    - What campaigns are completed and what were their performance metrics? Include names 
    - What are my 3 top opportunities? Please include information about the respective account
    - What is the names of the opportunities are sourced from partners and what the total amount?
    """
)

if "CRM_SQL_messages" not in st.session_state:
    st.session_state.CRM_SQL_messages = []

for message in st.session_state.CRM_SQL_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask me anything")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.CRM_SQL_messages.append({"role": "user", "content": prompt})
    with st.spinner("Working..."):
        try:
            data = {"prompt": prompt}
            headers = {
                'Authorization': f'Bearer {BEARER_TOKEN}'
            }
            response = requests.post(
                url=URL,
                json=data,  # changed to json for proper payload
                headers=headers,
                timeout=timeout,
                verify=False
            )
            if response.status_code == 200:
                result = response.json()
                pretty_result = json.dumps(result, indent=2)
                st.session_state.CRM_SQL_messages.append({"role": "assistant", "content": f"```json\n{pretty_result}\n```"})
                st.rerun()
            else:
                st.error(f"❌ Error from SnapLogic API: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")
