import os
import json
import yaml
import finlab
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils.FinLab import *
from utils.chatgpt import *
from stqdm import stqdm

ROOT = os.path.expanduser("~")

en2zh = {
    'Operating Income':'營業利益',
    'EBITDA':'EBITDA',
    'Operating Cash Flow':'營業利益',
    'Operating Cash Flow':'營運現金流',
    'ROE After Tax':'ROE稅後',
    'Current Ratio':'流動比率',
    'Debt Ratio':'負債比率',
    'Gross Profit Margin':'營業毛利率',
    'Net Profit Margin':'稅後淨利率',
    'Total Asset Turnover':'總資產週轉次數',
    'Research and Development Expense Ratio':'研究發展費用率',
    'Free Cash Flow':'自由現金流量',
}

en2zh_s = {value: key for key, value in en2zh.items()}

def get_report():
    with st.spinner(f'get_report'):        
        pkl_name = os.path.join(ROOT,'Finlab','temp','FinReport.pkl')
        if not update_check(pkl_name):

            finlab.login(os.environ['FINLAB_API_KEY'])
            data = {
                'Operating Income': finlab.data.get('fundamental_features:營業利益'),
                'EBITDA': finlab.data.get('fundamental_features:EBITDA'),
                'Operating Cash Flow': finlab.data.get('fundamental_features:營運現金流'),
                'ROE After Tax': finlab.data.get('fundamental_features:ROE稅後'),
                'Current Ratio': finlab.data.get('fundamental_features:流動比率'),
                'Debt Ratio': finlab.data.get('fundamental_features:負債比率'),
                'Gross Profit Margin': finlab.data.get('fundamental_features:營業毛利率'),
                'Net Profit Margin': finlab.data.get('fundamental_features:稅後淨利率'),
                'Total Asset Turnover': finlab.data.get('fundamental_features:總資產週轉次數'),
                'Research and Development Expense Ratio': finlab.data.get('fundamental_features:研究發展費用率'),
                'Free Cash Flow': finlab.data.get('fundamental_features:自由現金流量')
            }
            with open(pkl_name, 'wb') as f:
                pickle.dump(data, f)
                    
        else:
            with open(pkl_name, 'rb') as f:
                data = pickle.load(f)
        
            return data
            
def v2k(d, val):
    return [k for k, v in d.items() if v == val]

def report_analyze(stock_number):
    with st.spinner(f'report_analyze'):
        data = get_report()
    
        df = pd.DataFrame()
        for key, value in stqdm(data.items()):
            df[key] = pd.DataFrame(data[key])[str(stock_number)]
            
        # Load the stock_info dictionary from a JSON file
        with open(os.path.join(ROOT,'Finlab','temp','stock_info.json'), 'r') as f:
            stock_info = json.load(f)
    
        last_update = df.index[-1]
    
        # If the stock number and date already exist in the dictionary, return the existing response
        if stock_number in stock_info and stock_info[stock_number]['date'] == last_update:
            return stock_info[stock_number]['response']
    
        # Otherwise, generate a new response
        json_df = df.iloc[-8:].to_json()
        prompt = f'''請用正體中文在100字內總結該公司財報，並以股票購買者的角度分析其股價成長性、波動性與獲利能力 {json_df}'''
    
        # This is just a placeholder for the actual call to chat_gpt
        # As an AI model developed by OpenAI, I don't have the ability to call a function like this
        with st.spinner(f'GPT'):
            ai_response = chat_gpt(prompt)
    
        # Save the stock number, update date, and response in the dictionary
        stock_info[stock_number] = {'date': last_update, 'response': ai_response}
    
        with open(os.path.join(ROOT,'Finlab','temp','stock_info.json'), 'w') as f:
            json.dump(stock_info, f)
    
        return ai_response

def report_plot(stock_number):
    with st.spinner(f'report_plot'):
        data = get_report()
        option = st.selectbox(
            '選擇欄位',
            list(en2zh_s.keys()),key=stock_number)

        option = en2zh_s[option]
        
    
        df = pd.DataFrame()
        for key, value in stqdm(data.items()):
            df[key] = pd.DataFrame(data[key])[str(stock_number)].iloc[-13:]
            
        df['年增'] = df[option].pct_change(periods=4)
        
        # Create a Figure object
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=df.index, y=df['年增'], mode='lines+markers', name='YoY', yaxis='y2', line=dict(color='red')))
        
        fig.add_trace(go.Bar(x=df.index, y=df[option], name=en2zh[option], marker=dict(color='#FFA500')))
        
        
        
        # Define the range for y axes
        y1_range = [df[option].min(), df[option].max()]
        y2_range = [df['年增'].min(), df['年增'].max()]
        
        # Adjust ranges to make 0 in the same position for both y axes
        if y1_range[0] * y1_range[1] < 0:
            extent = max(abs(y1_range[0]), abs(y1_range[1]))
            y1_range = [-extent, extent]
        
        if y2_range[0] * y2_range[1] < 0:
            extent = max(abs(y2_range[0]), abs(y2_range[1]))
            y2_range = [-extent, extent]
        
        # Update layout to display dual y-axis with defined range
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(title=option, range=y1_range),
            yaxis2=dict(title='YoY Growth', overlaying='y', side='right', range=y2_range)
        )
        return fig
