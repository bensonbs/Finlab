import sys
sys.path.append('/home/jovyan/Finlab/utils')  # 替换为实际路径
import os
import json
import numpy as np
import pandas as pd
import streamlit as st
from utils.plot import *
from utils.FinLab import get_data
from utils.FinReport import *
from utils.WebScrapying import *

ROOT = os.path.expanduser("~")   

with st.sidebar:
    st.markdown('### 投資策略')
    st.markdown('''標的選擇前日跌幅>8%且外資大量買，站上開盤價有支撐後可選擇時機進場''')
with open(os.path.join(ROOT,'Finlab','name_dic.json'), 'r') as f:
    name_dic = json.load(f)
    
with st.spinner('資料讀取中...'):
    df = get_data(14)
    
with st.spinner('計算價差'):
    change = (df['close_price'].loc[prev_day(1)] - df['close_price'].loc[prev_day(2)]) / df['close_price'].loc[prev_day(2)]

#跌幅 > 8%
selecteds = df['close_price'].iloc[-1].T[change < -0.08].index

st.markdown('# 📉 外資買跌停')

selecteds = [selected for selected in selecteds if df['foreign_invest'][selected].loc[prev_day(1)]>0]

if len(selecteds) == 0:
    st.info('🐸 蛙咧，今天沒有當沖標，改天再來看看吧')

for selected in selecteds:
        # with st.expander(f'{selected}'):
        st.subheader(f'{name_dic[selected]}')
        metric(selected, df)
        tab = st.tabs(["技術", "三大法人", "財報分析",'產業與相關概念'])
        with tab[0]:
            p = k_chart(selected, df)
            st.plotly_chart(p,use_container_width=True)
            
        with tab[1]:
            p = institutional_chart(selected, df)
            st.plotly_chart(p,use_container_width=True)
            
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