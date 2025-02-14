import yfinance as yf
import pandas as pd
from typing import Union, List

class DataRetriever:
    def __init__(self,duration = None, start_date = None, end_date = None, interval = '1h'):

        self.duration = duration
        self.start_date = start_date
        self.end_date = end_date
        self.interval = interval

        if self.duration is not None and self.start_date is None and self.end_date is None:
            self.start_date = pd.Timestamp.today() - pd.Timedelta(days=self.duration)
            self.end_date = pd.Timestamp.today()

        elif self.duration is None and self.start_date is not None and self.end_date is not None:
            self.start_date = pd.Timestamp(start_date)
            self.end_date = pd.Timestamp(end_date)
        
        elif self.duration is None and self.start_date is None and self.end_date is None:
            raise ValueError("Please provide either duration or start_date and end_date")
        
    def get_data(self,ticker:Union[str,List[str]] = None , sector:str = None):
       
        data = {}

        if sector is not None:
            tickers = self.get_sector_tickers(self.sector)
        elif ticker is not None and type(ticker) == list:
            tickers = ticker
        elif ticker is not None and type(ticker) == str:
            tickers = [ticker]
        else:
            raise ValueError("Please provide either ticker or sector")
        
        for ticker in tickers:
            ticker_data = self.get_ticker_data(ticker)
            data[ticker] = ticker_data

        return data

    def get_sector_tickers(self, sector):
        
        url = f"https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        sp_data = pd.read_html(url)
        sector_tickers = sp_data[sp_data['GICS Sector'] == sector]['Symbol'].tolist()
        return sector_tickers


    def get_ticker_data(self,id )-> pd.DataFrame:
        ticker = yf.Ticker(id)
        data = pd.DataFrame()
        try:
            data = ticker.history(start=self.start_date, end=self.end_date, interval=self.interval,raise_errors=True) 
        except Exception as e:
            print('Set Duration to Max')
            while data.empty:
                print('Trying Again')
                data = ticker.history(period = 'max', interval=self.interval)
            # print(data)
        # print(data.head())
        return data