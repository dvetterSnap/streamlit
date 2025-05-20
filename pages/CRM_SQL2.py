import streamlit as st
import requests
import time
import os

# Load environment variables
URL = os.getenv("SL_CRM_SQL_TASK_URL", "https://demo-fm.snaplogic.io/api/1/rest/feed-master/queue/ConnectFasterInc/Dylan%20Vetter/CRM_Agent/CRM_Ultra")
BEARER_TOKEN = os.getenv("SL_CRM_SQL_TASK_TOKEN", "12345")
timeout = int(os.getenv("SL_TASK_TIMEOUT", "1000"))
page_title = os.getenv("CRM_SQL_PAGE_TITLE", "CRM Agent")
title = os.getenv("CRM_SQL_TITLE", "CRM Agent")

# Page config
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

# Typewriter effect
def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)

# Initialize chat history
if "CRM_SQL_messages" not in st.session_state:
    st.session_state.CRM_SQL_messages = []

# Display message history
for message in st.session_state.CRM_SQL_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle input
prompt = st.chat_input("Ask me anything")
if prompt:
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.CRM_SQL_messages.append({"role": "USER", "content": prompt})

    with st.spinner("Working..."):
        # Send full message history as array
        data = {
            "messages": st.session_state.CRM_SQL_messages
        }
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
            if 'choices' in result:
                reply = result['choices'][0]['message']['content'].replace("NEWLINE ", "**") + "**\n\n"
                with st.chat_message("assistant"):
                    typewriter(text=reply, speed=35)
                st.session_state.CRM_SQL_messages.append({"role": "assistant", "content": reply})
            else:
                with st.chat_message("assistant"):
                    st.error("❌ SnapLogic API response did not contain 'choices'")
        else:
            with st.chat_message("assistant"):
                st.error(f"❌ SnapLogic API returned error: {response.status_code}")
    
    # Rerun to render full thread
    st.rerun()
