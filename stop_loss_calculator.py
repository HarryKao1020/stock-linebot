import numpy as np
import pandas as pd
import requests
import shioaji as sj
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from datetime import date, timedelta
from dotenv import load_dotenv

# 加載 .env 文件中的環境變數
load_dotenv()
# 建立API物件，simulation=True是代表測試帳號
api = sj.Shioaji(simulation=True)

shioaji_secret = os.getenv('SHIOAJI_SECRETKEY', None)
shioaji_apikey = os.getenv('SHIOAJI_APIKEY', None)


# 登入你的key
# accounts = api.login("YOUR_API_KEY", "YOUR_SECRET_KEY")
accounts = api.login(shioaji_apikey, shioaji_secret)


def calculate_stop_loss(buy_price):
    stop_loss_five_percent = round(buy_price*0.95, 1)
    stop_loss_four_percent = round(buy_price*0.96, 1)
    return stop_loss_five_percent, stop_loss_four_percent  # 設定停損價格為買進價格的90%


def calculate_moving_averages(stock_code, window=60, buy_price=None):
    # 創建，比如現在時間的前180天
    today = date.today()
    delta = timedelta(days=180)
    date_180 = today - delta
    # 取得歷史股價資料
    # k棒的api使用方式
    kbars = api.kbars(
        contract=api.Contracts.Stocks[stock_code],
        start=str(date_180),
        end=str(today),
    )
    df = pd.DataFrame({**kbars})
    df.ts = pd.to_datetime(df.ts)
    df.set_index('ts', inplace=True)

    # 日k13:30的K棒
    df = df.resample('D').last().dropna()

    # 計算移動平均線
    df['5MA'] = df['Close'].rolling(window=5).mean()
    df['10MA'] = df['Close'].rolling(window=10).mean()
    df['20MA'] = df['Close'].rolling(window=20).mean()
    df['60MA'] = df['Close'].rolling(window=60).mean()
    df['20MA/60MA'] = df['20MA'] / df['60MA']
    # 計算價格差距百分比
    if buy_price is not None:
        df['5MA_diff'] = (buy_price - df['5MA']) / buy_price * 100
        df['10MA_diff'] = (buy_price - df['10MA']) / buy_price * 100
        df['20MA_diff'] = (buy_price - df['20MA']) / buy_price * 100
        df['60MA_diff'] = (buy_price - df['60MA']) / buy_price * 100

    return df[['5MA', '10MA', '20MA', '60MA', '20MA/60MA', '5MA_diff', '10MA_diff', '20MA_diff', '60MA_diff']].dropna()
