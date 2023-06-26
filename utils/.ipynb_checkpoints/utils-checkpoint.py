import os
import json
import pytz
import finlab
import openai
from datetime import datetime, timedelta
from utils.FinLab import get_data
# from pandas.tseries.offsets import BDay
ROOT = os.path.expanduser("~")

with open(os.path.join(ROOT,'Finlab','name_dic.json'), 'r') as f:
    name_dic = json.load(f)

finlab_api_key = os.environ['FINLAB_API_KEY']
openai_api_key = os.environ['OPENAI_API_KEY']

def update_check(filename):
    today = datetime.now().date().strftime('%Y-%m-%d')
    modified = datetime.fromtimestamp(os.path.getmtime(filename)).date().strftime('%Y-%m-%d') if os.path.exists(filename) else None
    return modified == today if modified else False

# def prev_day(n):
#     data['close_price'].index[-1]
#     tz = pytz.timezone('Asia/Taipei')
#     current_datetime = datetime.now(tz)
#     current_date = current_datetime.date()
#     return (current_date - BDay(n)).strftime('%Y-%m-%d')

def prev_day(n):
    data = get_data()
    day = data['close_price'].index[-n]
    return day.strftime('%Y-%m-%d')
