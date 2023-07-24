import os
import base64
import streamlit as st
ROOT = os.path.expanduser("~")

st.set_page_config(
    page_title="LeekLab",
    page_icon="🪙",
    initial_sidebar_state="expanded" 
)

st.markdown('#     ⚜ LeekLab 韭菜實驗室')
st.markdown('#')
st.write(' -    🐕 **LeekLab 韭菜實驗室提供您短、中、長台股量化交易**',unsafe_allow_html =True)
st.write(' -    🤖 **有最先進的ChatGPT語言模型，協助您分析財報**',unsafe_allow_html =True)
st.write(' -    🗺️ **台股板塊地圖分析熱門族群分佈，不用一直滑app查半天**',unsafe_allow_html =True)
st.write(' -    📉 **讓最韭的演算法幫助您開發選股策略，年年虧損繼續當社畜**',unsafe_allow_html =True)
st.markdown('#')
# st.image(os.path.join(ROOT,'Finlab','meme','1.jpg'))
# with st.sidebar:
#     st.markdown("![Alt Text](https://media.tenor.com/xFVGWLhMJegAAAAC/burn-money.gif)")
