import streamlit as st
import requests
import time
import os

# Load environment variables using os
URL = os.getenv("SL_Class_Code_TASK_URL", "https://demo-fm.snaplogic.io/api/1/rest/feed-master/queue/ConnectFasterInc/Dylan%20Vetter/00_Embroker_Underwriting/output%20Task")
BEARER_TOKEN = os.getenv("SL_Class_Code_TASK_TOKEN", "12345")
timeout = int(os.getenv("SL_TASK_TIMEOUT", "1000"))
page_title = os.getenv("Class_Code_PAGE_TITLE", "Class Code Recommendation Agent")
title = os.getenv("Class_Code_TITLE", "Class Code Recommendation Agent")

# Streamlit Page Properties
def typewriter(text: str, speed: int):
    tokens = text.split()
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = " ".join(tokens[:index])
        container.markdown(curr_full_text)
        time.sleep(1 / speed)

st.set_page_config(page_title=page_title)
st.title(title)

# Add space between the title and the rest of the content
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """  
    ### This is a Class Code Recommendation Agent that allows employees to submit a file for class code prediction.










 """
)

# Add space between the description and the input box
st.markdown("<br><br>", unsafe_allow_html=True)

# Initialize chat history
if "Class_Code_messages" not in st.session_state:
    st.session_state.Class_Code_messages = []

# Display chat messages from history on app rerun
for message in st.session_state.Class_Code_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
prompt = st.text_input("Enter the file name (e.g., gdrive/Applications/Datashapes.pdf)")

# Create two columns for the suggestion buttons to appear side by side
col1, col2 = st.columns(2)

# Button to suggest first input
with col1:
    if st.button("gdrive/Applications/Datashapes.pdf"):
        prompt = "gdrive/Applications/Datashapes.pdf"

# Button to suggest second input
with col2:
    if st.button("C://Users/Documents/Datashapes.pdf"):
        prompt = r"C://Users/Documents/CompanyABC_Application_2024.pdf"

if prompt:
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.Class_Code_messages.append({"role": "user", "content": prompt})
    with st.spinner("Working..."):
        data = {"prompt": prompt}
        headers = {
            'Authorization': f'Bearer {BEARER_TOKEN}'
        }
        response = requests.post(
            url=URL,
            data=data,
            headers=headers,
            timeout=timeout,
            verify=False
        )

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result:
                response = result['choices'][0]['message']['content'].replace("NEWLINE ", "**") + "**" + "\n\n"
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    typewriter(text=response, speed=90)
                # Add assistant response to chat history
                st.session_state.Class_Code_messages.append({"role": "assistant", "content": response})
            else:
                with st.chat_message("assistant"):
                    st.error(f"❌ Error in the SnapLogic API response")
                    st.error(f"{result['reason']}")
        else:
            with st.chat_message("assistant"):
                st.error(f"❌ Error while calling the SnapLogic API")
        st.rerun()
