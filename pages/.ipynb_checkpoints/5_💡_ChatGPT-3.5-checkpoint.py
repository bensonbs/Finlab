import os
import openai
import streamlit as st
from opencc import OpenCC

# 創建一個簡繁轉換的實例
cc = OpenCC('s2t')

# Setting page title and header
st.set_page_config(page_title="ChatGPT", page_icon="💡")
st.markdown("<h1 style='text-align: center;'>💡 ChatGPT</h1>", unsafe_allow_html=True)

# Set OpenAI API key from Streamlit secrets
openai.api_key = os.environ['OPENAI_API_KEY']

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"
    # st.session_state["openai_model"] = 'gpt-4'

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "user", "content": '簡短回答問題，並避免回答重複內容'})
    st.session_state.messages.append({"role": "assistant", "content": '是的，我會簡短回答'})

with st.chat_message("assistant"):
    ('本平台不保存任何數據😉，讓我們開始吧。')
        
# Display chat messages from history on app rerun
for message in st.session_state.messages[2:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
    
        # 嘗試以下的操作，若出現錯誤則捕捉並顯示警告
        try:
            # 初始化全體回應內容
            full_response = ""
            
            # 將session中的訊息轉換成適合OpenAI Chat模型的形式
            model_input = []
            for m in st.session_state.messages[-3:]:
                message_dict = {"role": m["role"], "content": m["content"]}
                model_input.append(message_dict)
        
            
            # 創建一個chat完成實例並以stream模式接收結果，最大token數為1024
            chat_completion = openai.ChatCompletion.create(
                    model=st.session_state["openai_model"],
                    messages=model_input,
                    stream=True,
                    max_tokens=1024
                )
            
            # 迭代處理chat完成實例的回應內容，並將內容加到全體回應中
            for response in chat_completion:
                response_content = response.choices[0].delta.get("content", "")
                response_content = cc.convert(response_content)
                full_response += response_content
                message_placeholder.markdown(full_response + " ")
        
            # 將最終的全體回應顯示出來
            message_placeholder.markdown(full_response)
        
            # 將回應加到session的訊息列表中
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    
        # 若在上述過程中出現任何錯誤，則顯示警告訊息
        except:
            st.warning('🐞 發生錯誤，請重新整理')
