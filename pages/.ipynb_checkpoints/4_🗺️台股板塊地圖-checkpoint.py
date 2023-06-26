import os
import finlab
import datetime
import numpy as np
import pandas as pd
import plotly.express as px
from finlab import data
from utils.FinLab import prev_day

import streamlit as st
ROOT = os.path.expanduser("~")

def df_date_filter(df, start=None, end=None):
    if start:
        df = df[df.index >= start]
    if end:
        df = df[df.index <= end]
    return df


def create_treemap_data(start, end, item, clip=None):
    close = data.get('price:收盤價')
    basic_info = data.get('company_basic_info')
    turnover = data.get('price:成交金額')
    close_data = df_date_filter(close, start, end)
    turnover_data = df_date_filter(turnover, start, end).iloc[1:].sum() / 100000000
    return_ratio = (close_data.iloc[-1] / close_data.iloc[-2]).dropna().replace(np.inf, 0)
    return_ratio = round((return_ratio - 1) * 100, 2)

    concat_list = [close_data.iloc[-1], turnover_data, return_ratio]
    col_names = ['stock_id', 'close', 'turnover', 'return_ratio']
    if item not in ["return_ratio", "turnover_ratio"]:
        try:
            custom_item = df_date_filter(data.get(item), start, end).iloc[-1].fillna(0)
        except Exception as e:
            logger.error('data error, check the data is existed between start and end.')
            logger.error(e)
            return None
        if clip:
            custom_item = custom_item.clip(*clip)
        concat_list.append(custom_item)
        col_names.append(item)

    df = pd.concat(concat_list, axis=1).dropna()
    df = df.reset_index()
    df.columns = col_names

    basic_info_df = basic_info.copy()
    basic_info_df['stock_id_name'] = basic_info_df['stock_id']+basic_info_df['公司簡稱']

    df = df.merge(basic_info_df[['stock_id', 'stock_id_name', '產業類別', '市場別', '實收資本額(元)']], how='left',
                  on='stock_id')
    df = df.rename(columns={'產業類別': 'category', '市場別': 'market', '實收資本額(元)': 'base'})
    df = df.dropna(thresh=5)
    df['market_value'] = round(df['base'] / 10 * df['close'] / 100000000, 2)
    df['turnover_ratio'] = df['turnover'] / (df['turnover'].sum()) * 100
    df['country'] = 'TW-Stock'
    return df


def plot_tw_stock_treemap(start=None, end=None, area_ind='market_value', item='return_ratio', clip=None,
                          color_scales='Temps'):
    """Plot treemap chart for tw_stock

    Treemap charts visualize hierarchical data using nested rectangles,
    it is good for judging the overall market dynamics.

    Args:
      start(str): The date of data start point.ex:2021-01-02
      end(str):The date of data end point.ex:2021-01-05
      area_ind(str):The indicator to control treemap area size .
                    Select range is in ["market_value","turnover","turnover_ratio"]
      item(str): The indicator to control treemap area color .
                 Select range is in ["return_ratio", "turnover_ratio"]
                 or use the other customized data which you could find from finlab database page,
                 ex:'price_earning_ratio:本益比'
      clip(tuple):lower and upper pd.clip() setting for item values to make distinct colors.ex:(0,100)
      color_scales(str):Used for the built-in named continuous
                        (sequential, diverging and cyclical) color scales in Plotly
                        Ref:https://plotly.com/python/builtin-colorscales/
    Returns:
        figure
    """
    df = create_treemap_data(start, end, item, clip)
    if df is None:
        return None
    df['custom_item_label'] = round(df[item], 2).astype(str)

    if area_ind not in ["market_value", "turnover", "turnover_ratio"]:
        return None

    if item in ['return_ratio']:
        color_continuous_midpoint = 0
    else:
        color_continuous_midpoint = np.average(df[item], weights=df[area_ind])

    fig = px.treemap(df,
                     # path=['country', 'market', 'category', 'stock_id_name'],
                     path=['country','category', 'stock_id_name'],
                     values=area_ind,
                     color=item,
                     color_continuous_scale=color_scales,
                     color_continuous_midpoint=color_continuous_midpoint,
                     custom_data=['custom_item_label', 'close', 'turnover'],
                     width=800,
                     height=1600)
                              
    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        textposition='middle center',
        textfont_size=24,
        texttemplate="%{label}(%{customdata[1]})<br>%{customdata[0]}",
                      )
    return fig

st.set_page_config(
    page_title="韭菜實驗室",
    page_icon="🧪",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.markdown('### 台股板塊地圖')
    st.markdown('''一目瞭然各板塊漲跌幅表現，依照顯示顏色紅綠深淺，很快就可以知道市場的熱門族群分佈。族群面積大小照市值排行，輕易看出各板塊的權值股代表。''')
    
st.markdown('# 🗺️台股板塊地圖')
                              
area_ind="market_value"
item="return_ratio"
clip=1000
#@title 台股漲跌與市值板塊圖
start= st.date_input("開始日",datetime.datetime.strptime(prev_day(2), '%Y-%m-%d')).strftime('%Y-%m-%d')
end = st.date_input("結束日",datetime.datetime.strptime(prev_day(1), '%Y-%m-%d')).strftime('%Y-%m-%d')
if start < end:
    fig = plot_tw_stock_treemap(start,end,area_ind,item, clip)
    st.plotly_chart(fig,use_container_width=True)
else :
    st.error('結束日必須大於開始日', icon="🚨")