import streamlit as st
from ollama import chat
import sys

# Streamlit app title
st.title("Intelligent ChatBot")

# Initialize session state for chat history and generation control
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stop_generation" not in st.session_state:
    st.session_state.stop_generation = False

# Sidebar for chat history
st.sidebar.title("Chat History")
for i, message in enumerate(st.session_state.messages):
    role = "User" if message["role"] == "user" else "Assistant"
    st.sidebar.write(f"{i + 1}. {role}: {message['content']}")

# Button to stop generation
if st.button("Stop Generation"):
    st.session_state.stop_generation = True

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        reasoning_content = ""  # Initialize reasoning_content
        in_thinking = False  # Initialize in_thinking
        st.session_state.stop_generation = False  # Reset stop flag

        try:
            stream = chat(
                model='deepseek-r1:7b',
                messages=[{'role': 'user', 'content': prompt}],
                stream=True,
            )

            for chunk in stream:
                if st.session_state.stop_generation:
                    st.warning("Generation stopped by user.")
                    break

                if chunk and 'message' in chunk and chunk['message'].content:
                    chunk_content = chunk['message'].content

                    # Store in appropriate buffer
                    if chunk_content.startswith('<think>'):
                        in_thinking = True
                    elif chunk_content.startswith('</think>'):
                        in_thinking = False
                    else:
                        if in_thinking:
                            reasoning_content += chunk_content
                        else:
                            full_response += chunk_content

                    # Update the response placeholder with the new content
                    response_placeholder.markdown(full_response)

            # Add assistant response to chat history
            if not st.session_state.stop_generation:
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            print(f"Error type: {type(e).__name__}, Error message: {str(e)}")