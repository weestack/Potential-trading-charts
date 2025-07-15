from rich.table import Table
from rich.console import Console
from rich.text import Text
from colorama import Fore, init
class Printer:
    ignore_headers = ['open', 'high', 'low', 'close', 'vwap', 'volume', 'date', 't', 'n', 'ticker', 'exchange', 'age', 'volume_percent_change' ]
    def __init__(self):
        init(autoreset=True)

    def base_stats(self, df):
        pass


    def display_results(self, results):
        console = Console()

        table = Table(title=f"{len(results)} stocks in total", header_style="bold magenta")

        table.add_column("Ticker", justify="center", style="bold")
        table.add_column("Age", justify="center", style="bold")
        table.add_column("Price", justify="left", style="bold cyan")
        table.add_column("Volume", justify="right", style="bold cyan")
        columns = []
        for column, _ in results[0][0].items():
            if column not in self.ignore_headers:
                table.add_column(column.capitalize(), justify="center", style="bold")
                columns.append(column)
        table.add_column("TradingView Link", justify="left", style="bold blue")

        for stocks in results:
            for stock in stocks:
                close_price = stock['close']
                open_price = stock['open']

                # Determine color and arrow based on price change
                if close_price > open_price:
                    color = Fore.GREEN
                    arrow = "▲"
                elif close_price < open_price:
                    color = Fore.RED
                    arrow = "▼"
                else:
                    color = Fore.WHITE
                    arrow = " "

                # Calculate price change percentage
                price_change_pct = ((close_price - open_price) / open_price) * 100
                price_change_text = Text(f"{price_change_pct:.2f}% {arrow}",
                                         style="green" if close_price > open_price else "red" if close_price < open_price else "white")

                # Format volume with colors
                volume_bar_combined = f"{stock['volume_percent_change']:.2f}% {arrow}"
                volume_text = Text(f"{stock['volume']:6} - {volume_bar_combined}",
                                   style="green" if close_price > open_price else "red" if close_price < open_price else "white")

                display_row = [stock['ticker'], stock['age'], price_change_text, volume_text]
                for column in columns:
                    if isinstance(stock[column], str):
                        display_row.append(stock[column])
                    else:
                        display_row.append(f"{stock[column]:.2f}")

                display_row.append(f"https://www.tradingview.com/chart/h21vSXJC/?symbol={stock['exchange']}:{stock['ticker']}")

                table.add_row(*display_row)
        console.print(table)