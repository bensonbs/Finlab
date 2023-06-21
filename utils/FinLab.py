import os
import pickle
import finlab
from stqdm import stqdm
from utils.utils import *

def get_data(days=None):
    finlab.login(config["finlab_api_key"])
    data_get_dict = {
        'open_price': 'price:開盤價',
        'high_price': 'price:最高價',
        'low_price': 'price:最低價',
        'close_price': 'price:收盤價',
        'volume': 'price:成交股數',
        'market_ind': 'etl:finlab_tw_stock_market_ind',
        'monthly_rev': 'monthly_revenue:當月營收',
        'rev_year_growth': 'monthly_revenue:去年同月增減(%)',
        'rev_month_growth': 'monthly_revenue:上月比較增減(%)',
        'foreign_invest': 'institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)',
        'investment_trust': 'institutional_investors_trading_summary:投信買賣超股數',
        'dealer_trade': 'institutional_investors_trading_summary:自營商買賣超股數(自行買賣)',
        'pe_ratio':'price_earning_ratio:本益比',
        'profit_growth': 'fundamental_features:營業利益成長率',
        'investment_cashflow': 'financial_statement:投資活動之淨現金流入_流出',
        'business_cashflow': 'financial_statement:營業活動之淨現金流入_流出',
        'adj_close': 'etl:adj_close',
        'loan_usage': 'margin_transactions:融資使用率',
        'non_operating_ratio': 'fundamental_features:業外收支營收率'
    }



    pkl_name = os.path.join(ROOT,'Finlab','temp','stock.pkl')
    if not update_check(pkl_name):
        ar = st.empty()
        data = {}
        for key, value in stqdm(data_get_dict.items()):
            data[key] = finlab.data.get(value)
            ar.info(f'正在下載{key}')
            with open(pkl_name, 'wb') as f:
                pickle.dump(data, f)
        ar.empty()
    else:
        with open(pkl_name, 'rb') as f:
            data = pickle.load(f)

    if days != None:
        for key, value in data_get_dict.items():
            data[key] = data[key].loc[prev_day(days):]

    return data

def Mastiff():
    data = get_data()
    rev_year_growth = data['rev_year_growth']
    rev_month_growth = 	data['rev_month_growth']
    score = data['market_ind']['score']
    close = data["close_price"]
    vol = data["volume"]
    vol_ma = vol.average(10)
    rev = data['monthly_rev']
    rev_year_growth = data['rev_year_growth']
    rev_month_growth = 	data['rev_month_growth']
    
    # 股價創年新高
    cond1 = (close == close.rolling(250).max())
    
    # 排除月營收連3月衰退10%以上
    cond2 = ~(rev_year_growth < -10).sustain(3) 
    
    # 排除月營收成長趨勢過老
    cond3 = ~(rev_year_growth > 60).sustain(12,8) 
    
    # 確認營收底部
    cond4 = ((rev.rolling(12).min())/(rev) < 0.8).sustain(3)
    
    # 排除營收跳動劇烈者
    cond5 = (rev_month_growth > -40).sustain(3)
    
    # 流動性條件
    cond6 = vol_ma > 200*1000

    # 流動性條件
    cond7 = close < 100
    
    buy = cond1 & cond2  & cond3 & cond4 & cond5 & cond6 & cond7
    
    # 買比較冷門的股票
    buy = vol_ma*buy
    buy = buy[buy>0]
    buy = buy.is_smallest(5)
    long_position = buy.resample('M').last().reindex(close.index,method='ffill')
    
    score_df = score >= 4
    long_position *= score_df
    
    # 做空訊號～多單遇大盤訊號轉空時出場，並反手做空指數避險
    short_target = '00632R'
    short_position = ~close[[short_target]].isna() * ~score_df
    position = pd.concat([long_position, short_position], axis=1)
    position = position.loc[prev_day(180):prev_day(1)]
    temp = position.iloc[-1].T[position.loc[prev_day(1)]==1]
    selecteds = list(temp.index)

    rows = []

    # 現在，我們可以在循環中直接創建這些數據
    for selected in selecteds:
        temp = pd.DataFrame(position[selected])
        series = temp.iloc[:, 0]
        series['block'] = (series.diff(1) != 0).astype('int').cumsum()
        index = series['block'].values.argmax()  # 這樣寫可以簡化代碼，並提高效率
        buy_time = temp.iloc[index].name
        buy_price = close.loc[buy_time, selected]
        sell_price = round(buy_price * 0.92, 2)
        price = close.loc[prev_day(1), selected]
        Benefit = round((price-buy_price)/price*100,2)
        # 直接將每一行的數據添加到我們之前創建的列表中
        rows.append([selected, name_dic[selected], buy_price, price, Benefit, sell_price, buy_time])

    df = pd.DataFrame(rows, columns=['代號', '名稱', '買入', '現價','損益', '停損', '買入時間']).round(2)
    filename = os.path.join(ROOT,'Finlab','temp','mastiff.csv')
    df.to_csv(filename,index=False)

    return df, selecteds

def low_volatility():
    data = get_data()
    pe = data['pe_ratio']
    rev = data['monthly_rev']
    rev_ma3 = rev.average(3)
    rev_ma12 = rev.average(12)
    d1 = data['profit_growth']
    peg =pe/d1
    price = data['close_price']
    
    cond1 = rev_ma3/rev_ma12>1.1
    cond2 = rev/rev.shift(1)>0.9
    # 新增過濾
    df1 = data['investment_cashflow']
    df2 = data['business_cashflow']
    自由現金流 = (df1 + df2).rolling(4).mean()
    
    # 進場訊號波動率
    atr = finlab.data.indicator('ATR', adjust_price=True,timeperiod=10)
    adj_close = data['adj_close']
    entry_volatility = atr/adj_close
    
    # 低波動因子
    d4 = data['loan_usage']
    d5 = data['non_operating_ratio']
    tree_select_factor = ((d4 <= 34) 
                          & (entry_volatility <= 0.032) 
                          & (d5 < 5.2))
    
    #考慮到資金問題，限制購買價格
    #考慮到風險新增自由現金流，但似乎限制價格就可以達到效果且較佳
    cond3= price<40 #(20%到18.3%, 勝率提升, 報酬上升到34.5%)
    #cond4 = 自由現金流 > 0(不用考慮比較好)
    
    cond_all = cond1 & cond2 & cond3 & tree_select_factor
    
    position = peg[cond_all & (peg > 0)]\
                .is_smallest(10)\
                .reindex(rev.index_str_to_date().index, method='ffill')
    position = position.loc[prev_day(180):prev_day(1)]
    temp = position.iloc[-1].T[position.loc[position.iloc[-1].name]==1]
    selecteds = list(temp.index)

    rows = []

    # 現在，我們可以在循環中直接創建這些數據
    for selected in selecteds:
        temp = pd.DataFrame(position[selected])
        series = temp.iloc[:, 0]
        series['block'] = (series.diff(1) != 0).astype('int').cumsum()
        index = series['block'].values.argmax()  # 這樣寫可以簡化代碼，並提高效率
        buy_time = temp.iloc[index].name
        buy_price = data['close_price'].loc[buy_time, selected]
        sell_price = round(buy_price * 0.92, 2)
        price = data['close_price'].loc[prev_day(1), selected]
        Benefit = round((price-buy_price)/price*100,2)
        # 直接將每一行的數據添加到我們之前創建的列表中
        rows.append([selected, name_dic[selected], buy_price, price, Benefit, sell_price, buy_time])

    df = pd.DataFrame(rows, columns=['代號', '名稱', '買入', '現價','損益', '停損', '買入時間']).round(2)
    filename = os.path.join(ROOT,'Finlab','temp','low_volatility.csv')
    df.to_csv(filename,index=False)

    return df, selecteds