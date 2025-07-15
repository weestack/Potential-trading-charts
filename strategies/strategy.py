class Strategy:
    name: str = "Bolog"
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_name(self):
        return self.name

    def process(self, data, ticker, exchange):
        raise NotImplementedError

    def calculate_base_stats(self, df):
        # Calculate volume change
        df["volume_percent_change"] = df["volume"].pct_change().abs() * 100
        df.fillna({"volume_percent_change": 0}, inplace=True)
        return df

class DemoStrategy(Strategy):
    name = "Demo Strategy"
    RSI_PERIOD = 14
    def process(self, data, ticker, exchange):
        results = self.calculate_rsi(data)
        # Check if any of the last three RSI values are above 70 or below 30
        last_three_rsi = results['RSI'].tail(3)
        age = 3
        for rsi in last_three_rsi:
            if rsi >= 70 or rsi <= 30:
                df = self.calculate_base_stats(results)
                df = df.iloc[-(age)]
                df_copy = df.copy()
                df_copy['age'] = f"{age - 1}d"
                df_copy['ticker'] = ticker
                df_copy['exchange'] = exchange

                return df_copy, True
            age -= 1

        return rsi, False


    def calculate_rsi(self, df, column="close"):
        """Calculate RSI using RMA (similar to Pine Script)."""
        period = self.RSI_PERIOD
        delta = df[column].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))
        return df