import streamlit as st
from openai import OpenAI
import requests
import json
from tavily import TavilyClient
import speech_recognition as sr

st.set_page_config(page_title="OpenRouter Chatbot", page_icon="🤖")

st.title("🤖 OpenRouter Tester")
st.caption("A simple Streamlit chatbot powered by OpenRouter with Web Search!")

# Define the search function
def search_web(query: str, tavily_api_key: str) -> str:
    """Use this function to search the web for real-time data, current events, or facts you don't know."""
    if not tavily_api_key:
        return "Tavily Error: No API key provided. Please enter it in the sidebar."
        
    try:
        tavily = TavilyClient(api_key=tavily_api_key)
        response = tavily.search(query=query, search_depth="basic", max_results=3)
        
        results = response.get("results", [])
        if not results:
            return "No useful information found on the web."
            
        snippets = []
        for r in results:
            if "title" in r and "content" in r:
                snippets.append(f"{r['title']}: {r['content']}")
                
        if not snippets:
            return f"No standard snippets found. Raw API response snippet: {str(response)[:500]}"
            
        return "\n\n".join(snippets)
    except Exception as e:
        return f"Failed to search the web using Tavily: {str(e)}"

# Setup OpenRouter client
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your OpenRouter API Key", value="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", type="password")
    st.markdown("[Get your OpenRouter API key here](https://openrouter.ai/keys)")
    
    st.divider()
    
    tavily_api_key = st.text_input("Enter your Tavily API Key (for Web Search)", value="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", type="password")
    st.markdown("[Get your Tavily key here](https://app.tavily.com/home)")
    
    # Model selection
    free_models = [
        "google/gemini-1.5-flash-exp:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "Apodex: Apodex 1.1 Mini (free)",
        "inception/mercury-decide:free",
        "respan/span-01-lite:free",
        "inclusionai/ling-3.0-flash-sante:free",
        "liquid/lfm-2.5-embedding-350m:free"
    ]
    selected_model = st.selectbox("Select Model", free_models)
    
    st.divider()
    st.subheader("Chat Management")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
        
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        chat_text = "Chat History:\n\n"
        for m in st.session_state.messages:
            if m.get("role") != "tool":
                role = "User" if m["role"] == "user" else "AI"
                chat_text += f"[{role}]: {m.get('content', '')}\n\n"
                
        st.download_button(
            label="💾 Download Chat History",
            data=chat_text,
            file_name="chat_history.txt",
            mime="text/plain"
        )
    
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "tool":
        # Don't show tool call internal data or tool responses to the user directly
        with st.chat_message(message["role"]):
            if "content" in message and message["content"]:
                st.markdown(message["content"])

# Web search toggle (must be outside the loop)
use_web_search = st.toggle("Enable Web Search for real-time info")

# Voice input handling
audio_value = st.audio_input("Or record a voice message instead of typing")
voice_prompt = None
if audio_value:
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_value) as source:
            audio = r.record(source)
            voice_prompt = r.recognize_google(audio)
    except Exception as e:
        st.error(f"Could not transcribe audio: {e}")

text_prompt = st.chat_input("Type your message here...")
prompt = text_prompt or voice_prompt

if prompt:
    if not api_key:
        st.error("Please enter your API Key in the sidebar.")
        st.stop()

    # If web search is enabled, do it before talking to the model
    search_context = ""
    if use_web_search:
        with st.spinner("Searching the web..."):
            search_context = search_web(prompt, tavily_api_key)

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if search_context:
            with st.expander("🔍 View Raw Web Search Results (What the AI sees)"):
                st.text(search_context)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            model_name = selected_model
            
            # Prepare messages
            messages_to_send = [{"role": m["role"], "content": m.get("content", "")} for m in st.session_state.messages if m["role"] != "tool"]
            
            # Inject context if we searched
            if search_context:
                messages_to_send[-1]["content"] = f"Real-time information from web search:\n{search_context}\n\nPlease answer the user's question using this information if relevant.\n\nUser Question: {prompt}"

            with st.spinner(f"Thinking (using {model_name})..."):
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages_to_send
                )
                
            final_reply = response.choices[0].message.content
            message_placeholder.markdown(final_reply)
            st.session_state.messages.append({"role": "assistant", "content": final_reply})
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
