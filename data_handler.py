import pandas as pd
import yfinance as yf
from queue import Queue
from events import MarketEvent

class HistoricDataHandler:
    """Downloads and streams historical daily market data for KO and PEP."""
    def __init__(self, events_queue: Queue, symbol_list: list, start_date:str, end_date:str):
        self.events_queue = events_queue
        self.symbol_list = symbol_list
        self.start_date = start_date
        self.end_date = end_date

        self.data_stream = self._download_and_align_data()

    def _download_and_align_data(self) -> pd.DataFrame:
        """Downloads data via yfinance and inner-joins on Date."""
        print(f"Downloading historical data for {self.symbol_list}...")
        df_list = []
        
        for symbol in self.symbol_list:
            df = yf.download(symbol, start=self.start_date, end=self.end_date, progress=False)

            if isinstance(df.columns, pd.MultiIndex):
                df = df['Close']
            else:
                df = df[['Close']]

            df.columns = [f"{symbol}_Close"]
            df_list.append(df)

        combined_df = pd.concat(df_list, axis=1).dropna()
        return combined_df
    def stream_next_bar(self) -> bool:
        """
        Pushes the next row of market data into the event queue as a MarketEvent.
        Returns False when out of data.
        """
        if self.data_stream.empty:
            return False

        timestamp = str(self.data_stream.index[0].date())
        row=self.data_stream.iloc[0]

        bar_dict = {}
        for symbol in self.symbol_list:
            bar_dict[symbol] = {'close': float(row[f"{symbol}_Close"])}

        event = MarketEvent(timestamp=timestamp, data=bar_dict)
        self.events_queue.put(event)

        self.data_stream = self.data_stream.iloc[1:]
        return True