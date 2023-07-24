import sys
sys.path.append('/home/jovyan/Finlab/utils')  # 替换为实际路径
import os
import json
import numpy as np
import pandas as pd
import streamlit as st
from stqdm import stqdm
from utils.plot import *
from utils.FinLab import *
from utils.FinReport import *
from utils.WebScrapying import *

with open(os.path.join(ROOT,'Finlab','name_dic.json'), 'r') as f:
    name_dic = json.load(f)

def get_name(selected):
    if selected in name_dic:
        return name_dic[selected]
    else:
        return str(selected)



def highlight_color(row):
    color_list = ['' for _ in row.index]
    # Check if '損益' is less than 8%
    if row['損益%'] < 0:
        # color_list[row.index.get_loc('損益')] = 'color: green'
        color_list[row.index.get_loc('損益%')] = 'color: green'
    else:
        # color_list[row.index.get_loc('損益')] = 'color: red'
        color_list[row.index.get_loc('損益%')] = 'color: red'
    if row['損益%'] < -8:
        # color_list[row.index.get_loc('損益')] = 'color: black'
        color_list[row.index.get_loc('損益%')] = 'color: black'
        # color_list[row.index.get_loc('損益')] = 'background-color: #5eae76'
        color_list[row.index.get_loc('損益%')] = 'background-color: #5eae76'
    elif row['損益%'] > 8:
        # color_list[row.index.get_loc('損益')] = 'color: black'
        color_list[row.index.get_loc('損益%')] = 'color: black'
        # color_list[row.index.get_loc('損益')] = 'background-color: #de796e'
        color_list[row.index.get_loc('損益%')] = 'background-color: #de796e'
        
    return color_list
    
st.markdown('# 🆚 韭是要對決')
data = get_data()


close_price = data['close_price'].iloc[-1]
with open(os.path.join(ROOT,'Finlab','vs.pkl'), 'rb') as f:
    dic = pickle.load(f)
    
# 選擇股票代號
options = list(close_price.index)

# 創建輸入表單
with st.form("my_form1"):
    user = st.text_input('**輸入暱稱**')
    submitted = st.form_submit_button("Submit")

if user:
    defult = [] if user not in dic else list(dic[user]['代號'])
    selecteds = st.multiselect('**輸入你的股票組合代號**', options,defult)
    # 創建數據框
    if selecteds:
        with st.form("my_form2"):
            if user in dic:
                df = dic[user]
                df['名稱'] = list(df.index)
                for s in selecteds:
                    if s not in dic[user]['代號'].to_list():
                        d = [[s, get_name(s), close_price[s], 1, 0]]
                        new_df = pd.DataFrame(d, columns=['代號', '名稱','現價','張數','平均成本'])
                        new_df.index = new_df['名稱']
                        df = pd.concat((df,new_df))
                for n in df['名稱']:
                    if n not in [get_name(selected) for selected in selecteds]:
                        df = df.drop(n)
                        if n in selecteds:
                            selecteds.remove(n)
            else:
                df = pd.DataFrame(data, columns=['代號', '名稱','現價','張數','平均成本'])
                for s in selecteds:
                    d = [[s, get_name(s), close_price[s], 1, 0]]
                    new_df = pd.DataFrame(d, columns=['代號', '名稱','現價','張數','平均成本'])
                    new_df.index = new_df['名稱']
                    df = pd.concat((df,new_df))
            df[['現價','張數','平均成本']] = df[['現價','張數','平均成本']].astype(float).apply(lambda x: np.round(x, 2))
            # df[['張數']] = df[['張數']].astype(int)
            df[['名稱']] = df[['名稱']].astype(str)
            st.info('填入張數與平均成本')
            df_copy = df.copy()
            df_copy.index = df_copy['名稱'].to_list()
            df_copy = df_copy[['代號','現價','張數','平均成本']]
            ed_df = st.data_editor(df_copy)
            submitted = st.form_submit_button("Submit")
        if submitted:
            # ed_df.index = ed_df['名稱'].to_list()
            dic[user] = ed_df[['代號', '現價','張數','平均成本']]
            # dic[user]['名稱'] = df['selecteds']
            st.success('新增成功')
            # 處理提交的數據
    else:
        if st.button(f'**刪除使用者** `{user}`',key=user):
            if user in dic:
                del dic[user]
                st.success('刪除成功')

# 在表單外部寫入
st.write("### 一畝韭菜田")
for user, ed_df in dic.items():
    with st.expander('',expanded=True):
        st.write(f'### {user}')
        show_df = ed_df.copy()
        # show_df['現價'] =  close_price[show_df['代號']].to_list()
        show_df['現價'] =  [cnyes_price(n) for n in stqdm(show_df['代號'])]
        show_df['損益'] = (show_df['現價'] - show_df['平均成本'])*show_df['張數']*1000
        show_df['損益%'] = ((show_df['現價'] - show_df['平均成本']) / show_df['平均成本']) * 100
        show_df = show_df[['代號', '現價','張數','平均成本', '損益', '損益%']]
        show_df[['現價','張數','平均成本','損益%']] = show_df[['現價','張數','平均成本','損益%']].astype(float).apply(lambda x: np.round(x, 2))
        show_df[['損益']] = show_df[[ '損益']].astype(int)
        show_df[['代號']] = show_df[['代號']].astype(str)
        styled_data = show_df.style.apply(highlight_color, axis=1).format("{:.2f}", subset=['現價','張數','平均成本', '損益%'])
        st.write(styled_data)
        bef = int(show_df['損益'].sum())
        total_investment = (show_df['平均成本'] * show_df['張數']).sum()
        total_market_value = (show_df['現價'] * show_df['張數']).sum()
        total_profit_loss_percentage = ((total_market_value - total_investment) / total_investment) * 100
        st.write(f'**總損益:** `{bef}`')
        st.write(f'**總損益比:** `{total_profit_loss_percentage:.2f}` **%**')

with open(os.path.join(ROOT,'Finlab','vs.pkl'), 'wb') as f:
    pickle.dump(dic, f)