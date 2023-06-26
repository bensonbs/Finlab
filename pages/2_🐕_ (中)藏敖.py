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
    st.markdown('''動能策略，押寶股價領先營收突破，大多頭會打出兇悍的一波流，勝率一半一半，但勝手常持有後一去不回，回檔小。因此停損設8%，偏低位置，保留多數獲利部位與下檔波動，遇到中期回檔也砍得快。
    開盤價進出，月底換股，押寶下月營收公布利多。
    持股用流動性條件篩成5檔，每檔最多持有 33.3% ，避免只選到1-2檔股票時的重壓個股風險。
    ''')
    

with open(os.path.join(ROOT,'Finlab','name_dic.json'), 'r') as f:
    name_dic = json.load(f)

st.markdown('# 🐕 藏獒')
with st.spinner('資料讀取中...'):
    df = get_data(44)

area = st.empty()
area.info('投資組合計算中...')
st.markdown('')
filename = os.path.join(ROOT,'Finlab','temp','mastiff.csv')
if not update_check(filename):
    data, selecteds = Mastiff()
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

styled_data = data.style.apply(highlight_color, axis=1).format("{:.2f}", subset=['買入', '現價', '停損', '損益'])
area.dataframe(styled_data, use_container_width=True)

for selected,tab in zip(selecteds,tab_list):
    with tab[2]:
        p = report_plot(selected)
        st.plotly_chart(p,use_container_width=True)
        if st.button('AI 分析',type='primary',key=f'button {selected}'):
            temp_area = st.empty()
            temp_area.info('財報分析中')
            temp_area.write(report_analyze(selected))

    with tab[3]:
        industry, concept = cnyes_tags(selected)
        st.markdown(f'{industry}')
        st.markdown(f'{concept}')
