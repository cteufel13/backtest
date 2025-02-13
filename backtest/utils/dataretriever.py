import yfinance as yf
import pandas as pd

class DataRetriever:
    def __init__(self):
        self.tickers = []
        self.sector = None

    def get_data(self, tickers, start_date, end_date):

        pass

    def get_sector_tickers(self, sector):
        
        url = f"https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        sp_data = pd.read_html(url)
        sector_tickers = sp_data[sp_data['GICS Sector'] == sector]['Symbol'].tolist()
        return sector_tickers


    def get_ticker_data(self,id):
        
        pass