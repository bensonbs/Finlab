import sys
sys.path.append('/home/jovyan/Finlab/utils')  # 替换为实际路径
import os
import json
import numpy as np
import pandas as pd
import streamlit as st
from utils.plot import *
from utils.FinLab import *
from utils.FinReport import *
from utils.WebScrapying import *

ROOT = os.path.expanduser("~")   

with st.sidebar:
    st.markdown('### 投資策略')
    st.markdown(''' ''')
    

with open(os.path.join(ROOT,'Finlab','name_dic.json'), 'r') as f:
    name_dic = json.load(f)

st.markdown('# 🌊 低波動')
with st.spinner('資料讀取中...'):
    df = get_data(44)

area = st.empty()
area.info('投資組合計算中...')
st.markdown('')
filename = os.path.join(ROOT,'Finlab','temp','low_volatility.csv')
if not update_check(filename):
    data, selecteds = low_volatility()
else :
    data = pd.read_csv(filename)
    selecteds = data['代號'].astype('str')

tab_list = []
for selected in selecteds:
    st.subheader(f'{name_dic[selected]}')
    metric(selected, df)
    tab = st.tabs(["技術", "三大法人", "財報分析",'產業與相關概念'])
    tab_list.append(tab)
    with tab[0]:
        p = k_chart(selected, df)
        st.plotly_chart(p,use_container_width=True)
        
    with tab[1]:
        p = institutional_chart(selected, df)
        st.plotly_chart(p,use_container_width=True)

data.index = data.iloc[:,1]
data = data.iloc[:,2:]
styled_data = data.style.apply(highlight_color, axis=1).format("{:.2f}", subset=['買入', '現價', '停損', '損益'])
area.dataframe(styled_data, use_container_width=True)

for selected,tab in zip(selecteds,tab_list):
    with tab[2]:
        p = report_plot(selected)
        st.plotly_chart(p,use_container_width=True)
        with st.expander('😀 AI分析', expanded=False):
            temp_area = st.empty()
            temp_area.info('財報分析中')
            temp_area.write(report_analyze(selected))

    with tab[3]:
        industry, concept = cnyes_tags(selected)
        st.markdown(f'{industry}')
        st.markdown(f'{concept}')