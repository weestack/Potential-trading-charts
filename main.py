from dotenv import load_dotenv
import os

import multiprocessing as mp

from data import DataFetcher, Polygon
from strategies.strategy import Strategy, DemoStrategy
from strategies.Harmonic_SR import HarmonicSR
from printer import Printer

def process_single_stock(stock, result_list, data_fetcher, strategy):
    try:
        dataframe, exchange = data_fetcher.fetch_ticker(stock)
        if dataframe is None:
            # print(f"No data for {stock['ticker']}")
            return

        strategy_results, match = strategy.process(dataframe, stock['ticker'], exchange)
        if match:
            result_list.append(strategy_results)
    except Exception as e:
        print(f"Error processing {stock['ticker']}: {e}")


class StockAnalyzer:
    dataFetcher: DataFetcher

    def __init__(self, dataFetcher: DataFetcher, strategy: Strategy):
        self.dataFetcher = dataFetcher
        self.strategy = strategy
        self.printer = Printer()
        self.prominent_stocks = []

    def print_prominent_stocks(self):
        self.printer.display_results(self.prominent_stocks)

    def run(self):
        # Set the maximum number of processes
        num_processes = mp.cpu_count()
        print(f"Using {num_processes} processes")

        stocks_page = self.dataFetcher.fetch_all_stocks()

        # Create a manager to handle shared resources between processes
        manager = mp.Manager()
        results = manager.list()  # Shared list for results

        # Get all stocks first
        all_stocks = []
        for stocks in stocks_page:
            all_stocks.extend(stocks["results"])

        # Using a process pool for better resource management
        with mp.Pool(processes=num_processes) as pool:
            # Map each stock to a worker
            pool_args = [(stock, results, self.dataFetcher, self.strategy) for stock in all_stocks]
            pool.starmap(process_single_stock, pool_args)

        # Convert the manager list to a normal list
        self.prominent_stocks = list(results)
        return self.prominent_stocks

if __name__ == "__main__":
    # Required for multiprocessing on macOS
    mp.set_start_method('spawn', force=True)

    import time

    start_time = time.time()

    load_dotenv()
    analyzer = StockAnalyzer(
        dataFetcher=Polygon(
            API_KEY=os.getenv('POLYGON_API_KEY')
        ),
        strategy=HarmonicSR(
            # Args
        )
    )

    analyzer.run()

    # Calculate and display the execution time
    end_time = time.time()
    execution_time = end_time - start_time

    # Format the time nicely
    hours, remainder = divmod(execution_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"\nTotal execution time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
    print(f"Total seconds: {execution_time:.2f}")
    analyzer.print_prominent_stocks()
