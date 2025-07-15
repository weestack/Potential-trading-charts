import time
import requests
import concurrent.futures
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self, **kwargs):
        self.today = datetime.today().strftime('%Y-%m-%d')
        self.six_months_ago = (datetime.today() - timedelta(days=4000)).strftime('%Y-%m-%d')
        for key, value in kwargs.items():
            setattr(self, key, value)

    def fetch(self):
        raise NotImplementedError

    def fetch_ticker(self, stock):
        raise NotImplementedError

    def fetch_all_stocks(self):
        raise NotImplementedError


class Polygon(DataFetcher):
    BASE_URL: str = "https://api.polygon.io"
    API_KEY: str = None

    EXCHANGES = {
        'XNYS': 'NYSE',
        'XNAS': 'NASDAQ',
        'XASE': 'AMEX',
        'ARCX': 'ARCA',
        'BATS': 'BATS'
    }
    # Rate limit, avoid throttling by staying under 100 requests per second
    # (1 / 100) * number of threads = 12 = 0.12 requests per second per thread
    time_per_request = (1 / 100) * 10

    def fetch_all_stocks(self):
        url = f"{self.BASE_URL}/v3/reference/tickers?market=stocks&active=true&order=asc&limit=1000&sort=ticker&apiKey={self.API_KEY}"
        data_entries = []

        data = self.fetch(url)
        yield data
        while data.get("next_url"):
            data = self.fetch(data["next_url"] + "&apiKey=" + self.API_KEY)
            yield data

    def fetch(self, url: str):
        """Fetch data with request throttling (max 100 requests per second)."""
        time_per_request = self.time_per_request
        start_time = time.time()
        response = requests.get(url)
        elapsed = time.time() - start_time
        if elapsed < time_per_request:
            time.sleep(time_per_request - elapsed)
        return response.json()

    def fetch_ticker(self, stock):
        ticker = stock["ticker"]
        exchange = self.EXCHANGES.get(stock["primary_exchange"], "Unknown")
        url = f"{self.BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{self.six_months_ago}/{self.today}?adjusted=true&sort=asc&limit=50000&apiKey={self.API_KEY}"
        frame = self.fetch(url)
        if frame.get("count", -1) < 1000:
            return None, None

        df = pd.DataFrame(frame["results"])
        df["date"] = pd.to_datetime(df["t"], unit="ms")
        df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "vw": "vwap"},
                  inplace=True)
        df.set_index('date', inplace=True)
        return df, exchange