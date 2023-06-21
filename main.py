import os
import streamlit as st
ROOT = os.path.expanduser("~")

st.set_page_config(
    page_title="韭菜實驗室",
    page_icon="🧪",
    initial_sidebar_state="expanded"
)

st.markdown('# 🧪 韭菜實驗室')
st.markdown('#')
st.markdown('### LeekLab 提供台股量化交易最韭的技術、資料庫、演算法，幫助您開發選股策略，年年虧損繼續當社畜')
st.markdown('#')
st.image(os.path.join(ROOT,'Finlab','meme','1.jpg'))