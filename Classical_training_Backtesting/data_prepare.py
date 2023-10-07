import pandas as pd
from datetime import datetime as dt
from binance.client import Client
import numpy as np

client = Client("SlzG7834qBY6kZXFsylAV3g5gzurYzol4mYStWyXILfUsVuN2axG5vRd38BeJHWU"
                , "Gfi8z5Kd1wYNtitedv4bBG3fpn4UrPYmvAl2lyAxlJzdO0LIn7WbEgSTAeRUWOzc")


klines_full = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_30MINUTE, "1 Jan, 2017", "05 Mar, 2023")

klines_train = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_30MINUTE, "1 Jan, 2017", "30 Jan, 2020")

klines_test = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_30MINUTE, "30 Jan, 2020", "5 Mar, 2023")

def binanceDataFrame(klines):
    df = pd.DataFrame(klines.reshape(-1,12),dtype=float, columns = ('date',
                                                                    'open',
                                                                    'high',
                                                                    'low',
                                                                    'close',
                                                                    'Volume',
                                                                    'Close time',
                                                                    'Quote asset volume',
                                                                    'Number of trades',
                                                                    'Taker buy base asset volume',
                                                                    'Taker buy quote asset volume',
                                                                    'Ignore'))

    df['date'] = pd.to_datetime(df['date'], unit='ms')
    df.index = pd.to_datetime(df['date'])
    df = df.dropna()


    return df

df_full = binanceDataFrame(np.array(klines_full))
df_train = binanceDataFrame(np.array(klines_train))
df_test = binanceDataFrame(np.array(klines_test))

#############################################################################################################
df_full.to_csv(r'C:\Users\Sid ali\Documents\PFE_Backtesting\zurichStrategy\data/data_BTCUSDT_30m_full.csv')

df_train.to_csv(r'C:\Users\Sid ali\Documents\PFE_Backtesting\zurichStrategy\data/data_BTCUSDT_30m_train.csv')

df_test.to_csv(r'C:\Users\Sid ali\Documents\PFE_Backtesting\zurichStrategy\data/data_BTCUSDT_30m_test.csv')
