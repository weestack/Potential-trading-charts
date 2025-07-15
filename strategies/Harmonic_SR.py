from . import strategy
from qa_trading.price_channels.price_channels import PriceChannels
from qa_trading.harmonic_patterns.harmonic_patterns import HarmonicPatterns
from datetime import datetime, timedelta
import pandas as pd
from datetime import datetime
import numpy as np

class HarmonicSR(strategy.Strategy):
    name = "Harmonic_SR"

    def process(self, data, ticker, exchange):

        channels = PriceChannels(data)
        channels.predictive_channels(data)

        harmonic_patterns = HarmonicPatterns(data)
        harmonic_patterns.first_time_processing(data, channels=channels)

        harmonic_match, harmonic_signal = self.is_index_within_past_3_days(harmonic_patterns.harmonicpattern_signals)
        abcd_match, abcd_signal = self.is_index_within_past_3_days(harmonic_patterns.abcd_signals)
        doublepattern_match, doublepattern_signal = self.is_index_within_past_3_days(harmonic_patterns.doublepattern_signals)

        if any([harmonic_match, abcd_match, doublepattern_match]):
            result_list = []
            self.calculate_rsi(data)
            df_copy = data.tail(5).copy()
            df_copy = self.calculate_base_stats(df_copy)
            df_copy['ticker'] = ticker
            df_copy['exchange'] = exchange

            # RSI disagree lets skip it
            last_three_rsi = data['RSI'].iloc[-3:].values

            # Check if none of the values are in extreme ranges (0-35 or 65-100)
            if not any(rsi <= 35 or rsi >= 65 for rsi in last_three_rsi):
                return [], False

            days = self.apply_pattern_stats(df_copy, harmonic_match, harmonic_signal, 'Harmonic')
            if days:
                result_list.append(df_copy.iloc[-(days + 1)])

            days = self.apply_pattern_stats(df_copy, abcd_match, abcd_signal, 'ABCD')
            if days:
                result_list.append(df_copy.iloc[-(days + 1)])

            days = self.apply_pattern_stats(df_copy, doublepattern_match, doublepattern_signal, 'Double')
            if days:
                result_list.append(df_copy.iloc[-(days + 1)])

            # no harmonic patterns matched up, skip
            if not result_list:
                return [], False

            return result_list, True
        return [], False

    def apply_pattern_stats(self, df, match, signal, key):
        if match:
            days = self.days_since_timestamp(signal).iloc[-1]['days_since']
            df[f'age'] = f"{days}d - {key}"

            signal = signal.iloc[-1]
            df[f'pattern'] = signal['match']

            trend = "Bullish" if signal['trend'] == 1 else "Bearish"
            df[f'signal'] = f"{trend} - {signal['accuracy']:.2f}"
            return days
        else:
            df[f'age'] = "-"
            df[f'pattern'] = "-"
            df[f'signal'] = "-"

    def calculate_rsi(self, df, column="close"):
        """Calculate RSI using RMA (similar to Pine Script)."""
        period = 14
        delta = df[column].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))
        return df

    def days_since_timestamp(self, df):
        df = df.copy()
        # Get current datetime
        now = pd.Timestamp.now()

        # Create a new column or Series with the result
        # You can either add it to the DataFrame:
        df.loc[:,'days_since'] = (now - df.index).days

        # Or return it as a separate Series:
        # return pd.Series(days_elapsed, index=df.index, name='days_since')

        return df

    def is_index_within_past_3_days(self, df):
        # Get current time
        now = datetime.now()

        # Calculate the date 3 days ago
        three_days_ago = now - timedelta(days=3)

        # Check if any index is within the past 3 days
        recent_data = df[df.index >= three_days_ago]

        # Return True if there are any rows with index in the past 3 days
        return not recent_data.empty, recent_data
