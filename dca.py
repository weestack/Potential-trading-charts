import yfinance as yf
import pandas as pd
from datetime import datetime

dat = yf.Tickers("NVDA").download(period="10Y", interval='1d')
final = dat.tail(1)['Close'].iloc[0].iloc[0]  # Get the final close price
start = datetime(2015, 1, 1)
end = datetime(2025, 12, 31)

dates = pd.date_range(start, end, freq='5D')
wallet = []
buy_each_interval = 5

for date in dates:
    if date in dat.index:
        row = dat.loc[date]
        close = row['Close'].iloc[0]  # Remove the .iloc[0] if not needed
        quantity = buy_each_interval  # Number of shares to buy
        wallet.append((quantity, close))  # Store as (quantity, price)

# Calculate totals correctly
total_investment = sum(quantity * price for quantity, price in wallet)
total_return = sum(quantity * final for quantity, price in wallet)

print("Total shares:     ", len(wallet) * buy_each_interval)
print("Total investment: ", total_investment)
print("Total return:     ", total_return)
print("Profit/Loss:      ", total_return - total_investment)
print("Return %:         ", ((total_return - total_investment) / total_investment) * 100, "%")
print("Average return:   ", total_return / (len(wallet)*buy_each_interval))