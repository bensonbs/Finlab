import os
import requests
from lxml import html
# os.environ['SERPAPI_API_KEY'] = 'fd3bac28079a9009f50bed8365e1e681567cd6c8b7082c0cf84a8d310fdad1ea'
os.environ['OPENAI_API_KEY']  = os.environ['OPENAI_API_KEY']
os.environ["GOOGLE_CSE_ID"] = ""
os.environ["GOOGLE_API_KEY"] = ""
import streamlit as st
from streamlit_agent.clear_results import with_clear_container
from streamlit_agent.callbacks.capturing_callback_handler import playback_callbacks

from langchain import OpenAI, GoogleSearchAPIWrapper, LLMChain
from langchain.chains import LLMMathChain
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.retrievers import KNNRetriever
from langchain.callbacks import StreamlitCallbackHandler
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import WebBaseLoader

from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader

def test_func(inp: str) -> str:
    loader = PyPDFLoader("/home/jovyan/Finlab/pages/runs/FE_20230721_00000.pdf")
    pages = loader.load_and_split()
    faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
    docs = faiss_index.similarity_search(inp, k=2)
    output_text = ''
    for doc in docs:
        text = '在第{}頁,提到:{}'.format(str(doc.metadata["page"]),doc.page_content)
        output_text += text
    return output_text

def cnyes_tags(inp: str) -> str:
    url = f"https://www.cnyes.com/twstock/{inp}/relation/overview"
    
    # 发送HTTP GET请求获取网页内容
    response = requests.get(url)
    html_content = response.text
    
    # 使用lxml解析HTML
    tree = html.fromstring(html_content)
    
    concept = ''
    
    industry = ''

    xpath_str = f'//*[@id="tw-stock-tabs"]/section[1]/div[2]/a'
    elements = tree.xpath(xpath_str)
    for element in elements:
        industry = industry + f'`{element.text}` ' 
    
    for n in range(1, 10):  # 設定你想要的範圍
        xpath_str = f'//*[@id="tw-stock-tabs"]/section[1]/div[2]/div/span[{n}]'
        elements = tree.xpath(xpath_str)
        for element in elements:
    
            concept = concept + f'`{element.text}` '
            
    return  f'相關概念： {industry} {concept}'

def cnyes_price(inp: str) -> str:
    # 獲取網頁內容
    url = f'https://www.cnyes.com/twstock/{inp}/analysis/performance'
    response = requests.get(url)
    
    # 解析網頁內容
    tree = html.fromstring(response.content)
    
    # 使用XPath選擇元素
    real_time_price = tree.xpath('//*[@id="anue-ga-wrapper"]/div[4]/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/div/h3/text()')[0]
    return '{}股價為： {:.2f}'.format(inp,float(real_time_price))

SAVED_SESSIONS  = {}
st.set_page_config(
    page_title="MRKL", page_icon="🦜", layout="wide", initial_sidebar_state="collapsed"
)

"# 🦜🔗 MRKL"
search = GoogleSearchAPIWrapper()
llm = OpenAI(temperature=0, openai_api_key=os.environ['OPENAI_API_KEY'], streaming=True)
llm_math_chain = LLMMathChain.from_llm(llm)


tools = [
    Tool(
        name="Search",
        func=search.run,
        description="當您需要回答有關時事的問題時很有用。 你應該提出有針對性的問題",
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="當您需要回答數學問題時很有用",
    ),
    Tool(
        name="cnyes_tags",
        func=cnyes_tags,
        description="當詢問有關公司相關概念股時使用，但你需要先知道該公司的股票號碼並作為輸入，股票號碼通常由四位數字組成",
    ),
    Tool(
        name="cnyes_price",
        func=cnyes_tags,
        description="當詢問有關股票價格時使用，但你需要先知道該公司的股票號碼並作為輸入，股票號碼通常由四位數字組成",
    ),
    Tool(
        name="test_func",
        func=test_func,
        description="當您需要回答有關教育訓練的問題時很有用。 你應該提出有針對性的問題",
    ),
]


mrkl = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

sample = st.checkbox("使用範例",True)
with st.form(key="form"):
    text="緯創的股價現在是多少? 最近有哪些概念股？" if sample else ""
    user_input = st.text_input("輸入你的問題",text)
    submit_clicked = st.form_submit_button("Submit Question")

output_container = st.empty()
if with_clear_container(submit_clicked):
    output_container = output_container.container()
    output_container.chat_message("user").write(user_input)

    answer_container = output_container.chat_message("assistant", avatar="🦜")
    st_callback = StreamlitCallbackHandler(answer_container)

    # If we've saved this question, play it back instead of actually running LangChain
    # (so that we don't exhaust our API calls unnecessarily)
    if user_input in SAVED_SESSIONS:
        session_name = SAVED_SESSIONS[user_input]
        session_path = Path(__file__).parent / "runs" / session_name
        print(f"Playing saved session: {session_path}")
        answer = playback_callbacks([st_callback], str(session_path), max_pause_time=2)
    else:
        answer = mrkl.run(user_input, callbacks=[st_callback])

    answer_container.write(answer)