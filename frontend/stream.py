import streamlit as st
import sseclient
import json
import os


# Backend URL (Update if deploying externally)
API_BASE_URL = os.getenv("API_BASE_URL")

# Session state to preserve user chat and checkpoint
if "messages" not in st.session_state:
    st.session_state.messages = []

if "checkpoint_id" not in st.session_state:
    st.session_state.checkpoint_id = None

st.title("🤖 LangGraph Chatbot (Streaming with Tools)")

user_input = st.text_input("Type your message:", key="user_message")

if st.button("Send") and user_input:
    # Append user's message to chat history
    st.session_state.messages.append({"sender": "user", "text": user_input})
    status_text = st.empty()
    # Start streaming request
    with st.spinner("Waiting for response..."):
        try:
            endpoint = f"{API_BASE_URL}/chat_stream/{user_input}"
            params = {}
            if st.session_state.checkpoint_id:
                params["checkpoint_id"] = st.session_state.checkpoint_id
                url = f"{endpoint}?{params['checkpoint_id']}"
            else:
                url = f"{endpoint}"
            # response = requests.get(endpoint, params=params, stream=True)
            print(url)
            # client = sseclient.SSEClient(response)
            client = sseclient.SSEClient(url)
            # print(client.events())
            bot_response = ""
            search_urls = []
            print("reached here")
            for event in client.iter_content():
                print("EVENT:")
                print(event)
                if not event:
                    continue

                try:
                    # Decode bytes to string if needed
                    decoded_str = event.decode('utf-8') if isinstance(event, bytes) else event
                    
                    # Look for line starting with "data:"
                    for line in decoded_str.splitlines():
                        if line.startswith("data: "):
                            json_part = line[len("data: "):].strip()
                            data = json.loads(json_part)
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"Skipping invalid message: {e}")

                if data["type"] == "checkpoint":
                    st.session_state.checkpoint_id = data["checkpoint_id"]

                elif data["type"] == "content":
                    bot_response += data["content"]
                    # Display live update (optional)
                    # st.write(bot_response + "▌")
                    status_text.text(bot_response)
                elif data["type"] == "search_start":
                    st.info(f"🔎 Searching for: {data['query']}")

                elif data["type"] == "search_results":
                    search_urls = data["urls"]

                elif data["type"] == "end":
                    break

            # Final bot message
            st.session_state.messages.append({"sender": "bot", "text": bot_response})

            # Add search URLs if any
            for url in search_urls:
                st.session_state.messages.append({"sender": "search", "text": url})

        except Exception as e:
            st.error(f"Error: {e}")

# Display chat messages
print(st.session_state)
st.markdown("---")

for msg in st.session_state.messages:
    if msg["sender"] == "user":
        st.markdown(f"🧑‍💬 **You:** {msg['text']}")
    elif msg["sender"] == "bot":
        st.markdown(f"🤖 **Bot:** {msg['text']}")
    elif msg["sender"] == "search":
        st.markdown(f"🔗 [Search Result]({msg['text']})")

