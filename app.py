I'mimport streamlit as st
import openai
import requests
import json
import re
import time

# ------------------------- PAGE SETUP -------------------------
st.set_page_config(
    page_title="Smart Diamond",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ------------------------- CUSTOM CSS FOR STYLING -------------------------
# This makes the app look more professional
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #0e1117;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subheader {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stChatInput {
        position: fixed;
        bottom: 20px;
        width: 80%;
    }
    .assistant-message {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------- SIDEBAR CONFIGURATION -------------------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/diamond.png", width=80)
    st.title("Smart Diamond Setup 🔧")
    st.markdown("---")
    
    st.subheader("API Keys Required")
    openai_api_key = st.text_input("OpenAI API Key:", type="password", help="Get this from platform.openai.com")
    serper_api_key = st.text_input("Serper API Key:", type="password", help="Get this from serper.dev (free tier available)")
    
    if openai_api_key:
        openai.api_key = openai_api_key
    if serper_api_key:
        SERPER_API_KEY = serper_api_key
    
    st.markdown("---")
    st.subheader("About")
    st.info("""
    💎 **Smart Diamond** is your multifaceted AI assistant capable of:
    - Answering general knowledge questions
    - Real-time web searches
    - Mathematical calculations
    - Creative writing and coding
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.success("Chat history cleared!")

# ------------------------- APP HEADER -------------------------
st.markdown('<h1 class="main-header">💎 Smart Diamond</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Your multifaceted guide to knowledge</p>', unsafe_allow_html=True)

# ------------------------- INITIALIZE SESSION STATE -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Smart Diamond, your AI assistant. How can I help you today?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    avatar = "💎" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ------------------------- CORE FUNCTIONS (THE BRAIN) -------------------------
def classify_query(user_input):
    user_input_lower = user_input.lower()
    real_time_keywords = ['current', 'latest', 'recent', 'today', 'now', 'this week', 'new', 'price of', 'news', 'update', 'weather', 'forecast', 'stock', 'bitcoin', 'ethereum', 'crypto', 'score', 'live', 'just happened']
    math_keywords = ['calculate', 'solve', 'what is', 'times', 'plus', 'minus', 'divided by', 'multiplied by', '^', '/', '*', '+', '-', 'equation', 'root of', 'log', 'sin', 'cos', 'tan', 'derivative', 'integral', 'pi', 'math', '=']

    if any(keyword in user_input_lower for keyword in real_time_keywords):
        return "search"
    elif any(keyword in user_input_lower for keyword in math_keywords):
        if re.match(r'^[\d\s\+\-\*\/\(\)\.\^]+$', user_input.replace(' ', '')):
            return "math"
        return "math"
    else:
        return "general"

def execute_math(expression):
    try:
        sanitized_expr = re.sub(r'[^\d\+\-\*\/\(\)\.\s]', '', expression)
        result = eval(sanitized_expr, {"__builtins__": None}, {})
        return f"**Calculation Result:** {result}"
    except Exception as e:
        return f"❌ I couldn't calculate that. Please check your expression."

def perform_web_search(query):
    if 'SERPER_API_KEY' not in globals():
        return "🔑 Please add your Serper API key in the sidebar to enable web search."
    
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    
    try:
        with st.spinner("🔍 Searching the web..."):
            response = requests.post(url, headers=headers, data=payload)
            response_data = response.json()
            
            if 'answerBox' in response_data and 'answer' in response_data['answerBox']:
                return f"**Web Result:** {response_data['answerBox']['answer']}"
            
            if 'organic' in response_data and response_data['organic']:
                top_result = response_data['organic'][0]
                return f"**Web Result:** {top_result.get('snippet', 'Information found')}\n\n*Source: [{top_result.get('title', 'Link')}]({top_result.get('link', '')})*"
            else:
                return "❌ No relevant information found in recent search results."
                
    except Exception as e:
        return f"❌ Search error: {str(e)}"

def ask_openai(prompt, max_tokens=500):
    if not openai.api_key:
        return "🔑 Please add your OpenAI API key in the sidebar to get started."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
            stream=True  # Enable streaming
        )
        return response
    except Exception as e:
        return f"❌ OpenAI error: {str(e)}"

# ------------------------- CHAT INPUT & PROCESSING -------------------------
if prompt := st.chat_input("Ask Smart Diamond anything..."):
    if not openai.api_key:
        st.warning("Please enter your OpenAI API key in the sidebar first!")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Classify query and generate response
    query_type = classify_query(prompt)
    
    with st.chat_message("assistant", avatar="💎"):
        message_placeholder = st.empty()
        full_response = ""
        
        if prompt.lower() in ['quit', 'exit', 'goodbye', 'bye']:
            full_response = "Thank you for chatting with me! 💎 Have a wonderful day!"
        
        elif query_type == "math":
            full_response = execute_math(prompt)
            message_placeholder.markdown(full_response)
        
        elif query_type == "search":
            full_response = perform_web_search(prompt)
            message_placeholder.markdown(full_response)
        
        else:
            # For streaming responses from OpenAI
            response = ask_openai(prompt)
            if isinstance(response, str):
                # It's an error message
                message_placeholder.markdown(response)
                full_response = response
            else:
                # It's a streaming response
                for chunk in response:
                    if chunk.choices[0].delta.get("content"):
                        chunk_content = chunk.choices[0].delta.content
                        full_response += chunk_content
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
