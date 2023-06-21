import os
import json
import pytz
import yaml
import pickle
import finlab
import openai
import requests
import numpy as np
import pandas as pd
from lxml import html
import streamlit as st
from finlab import data
from functools import reduce
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay
ROOT = os.path.expanduser("~")

with open(os.path.join(ROOT,'Finlab','name_dic.json'), 'r') as f:
    name_dic = json.load(f)

finlab_api_key = os.environ['FINLAB_API_KEY']
openai_api_key = os.environ['OPENAI_API_KEY']
config = {
    'finlab_api_key':finlab_api_key,
    'openai_api_key':openai_api_key
    }

def update_check(filename):
    today = datetime.now().date().strftime('%Y-%m-%d')
    modified = datetime.fromtimestamp(os.path.getmtime(filename)).date().strftime('%Y-%m-%d') if os.path.exists(filename) else None
    return modified == today if modified else False

def prev_day(n):
    tz = pytz.timezone('Asia/Taipei')
    current_datetime = datetime.now(tz)
    current_date = current_datetime.date()
    return (current_date - BDay(n)).strftime('%Y-%m-%d')
