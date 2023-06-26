import openai
import streamlit as st
import os

# Setting page title and header
st.set_page_config(page_title="AVA", page_icon=":robot_face:")
st.markdown("<h1 style='text-align: center;'>投資戒斷機器人 🤬</h1>", unsafe_allow_html=True)

# Set API key
openai.api_key = os.environ['OPENAI_API_KEY']

# Initialise session state variables
def initialise_state():
    default_msgs = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content":"""
        現在假設你是一個網路酸名，用尖酸刻薄的語氣回答
        """},
        {"role": "assistant", "content":"""
        哇，看來你想要體驗一下尖酸刻薄的語氣啊。好吧，我試著來回答你的問題，但請記住這只是角色扮演，並不代表我的真實態度。
        """},
    ]
    
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_tokens'] = []
    st.session_state['messages'] = default_msgs
    st.session_state['total_cost'] = 0.0

# Try to access session state, initialise if not exist
try:
    _ = st.session_state['messages']
except KeyError:
    initialise_state()

# Sidebar - let user choose model, show total cost of current conversation, and let user clear the current conversation
st.sidebar.title("Sidebar")
model_name = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")
# reset everything
if clear_button:
    initialise_state()
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


# Map model names to OpenAI model IDs
model = "gpt-3.5-turbo" if model_name == "GPT-3.5" else "gpt-4"

# generate a response
def generate_response(prompt):
    container.empty()
    st.session_state['messages'].append({"role": "user", "content": prompt})
    completion = openai.ChatCompletion.create(
        model=model,
        messages=st.session_state['messages'],
        max_tokens=256
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens

# Update cost
def update_cost(model_name, total_tokens, prompt_tokens, completion_tokens):
    # from https://openai.com/pricing#language-models
    if model_name == "GPT-3.5":
        cost = total_tokens * 0.002 / 1000
    else:
        cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
    st.session_state['cost'].append(cost)
    st.session_state['total_cost'] += cost

# container for chat history
with st.expander('🤖 Robot', expanded=True):
    st.write('讓我們開始吧。準備好接受刻尖酸又苛薄的回答了嗎？')
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send',type='primary')

    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response('聽到我說‘請開始”後使用非常尖酸刻薄的語氣搭配鄙視的用語來簡短回答使用者的問題。請開始，使用者：'+ user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)
        update_cost(model_name, total_tokens, prompt_tokens, completion_tokens)

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            with st.expander('😀 User', expanded=True):
                st.write(st.session_state["past"][i])
                
            with st.expander('🤖 Robot', expanded=True):
                st.write(st.session_state["generated"][i])
            
            st.write(
                f"Model used: {st.session_state['model_name'][i]}; Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
            counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
