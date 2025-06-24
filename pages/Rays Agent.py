import streamlit as st
from dotenv import dotenv_values
import requests
import time
import os
import uuid

# Load environment variables
URL = os.getenv("SL_Tampa_TASK_URL", "https://demo-fm.snaplogic.io/api/1/rest/feed-master/queue/ConnectFasterInc/Dylan%20Vetter/TampaBayRays/Driver%20Task")
BEARER_TOKEN = os.getenv("SL_Tampa_TASK_TOKEN", "1234")
timeout = int(os.getenv("SL_TASK_TIMEOUT", "1000"))
page_title = os.getenv("Tampa_PAGE_TITLE", "CRM Agent")
title = os.getenv("Tampa_TITLE", "CRM Agent")

# Streamlit Page Properties
st.set_page_config(page_title=page_title)
st.title(title)

def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)

# Description block
st.markdown(
    """  
    ### This is a CRM Agent that allows fans to interact with the Tampa Bay Rays Website and Schedule using Natural Language
    Example Questions
    - Tell me about the lastest headlines?
    - What is the upcomign schedule?
    """
)

# Initialize session state
if "Tampa_messages" not in st.session_state:
    st.session_state.Tampa_messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display chat history
for message in st.session_state.Tampa_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
prompt = st.chat_input("Ask me anything")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.Tampa_messages.append({"role": "user", "content": prompt})

    # Format message history to SnapLogic's expected format
    sl_messages = [
        {"sl_role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]}
        for msg in st.session_state.Tampa_messages
    ]

    payload = {
        "messages": sl_messages,
        "session_id": st.session_state.session_id,
        "deployment_id": "end_turn"
    }

    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }

    with st.chat_message("assistant"):
        with st.spinner("Working..."):
            try:
                response = requests.post(
                    url=URL,
                    json=payload,
                    headers=headers,
                    timeout=timeout,
                    verify=False
                )

                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result:
                        reply = result['choices'][0]['message']['content'].replace("NEWLINE ", "**") + "**\n\n"
                    elif 'response' in result:
                        reply = result['response']
                    else:
                        reply = "No response returned from SnapLogic."

                    typewriter(reply, speed=35)
                    st.session_state.Tampa_messages.append({"role": "assistant", "content": reply})
                else:
                    st.error(f"❌ Error while calling the SnapLogic API: {response.status_code}")
                    st.error(response.text)
            except Exception as e:
                st.error(f"❌ Exception occurred: {str(e)}")

    st.rerun()
