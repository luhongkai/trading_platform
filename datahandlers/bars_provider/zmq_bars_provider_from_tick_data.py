import string
import time

from datahandlers.bars_provider.zmq import DWX_ZeroMQ_Connector_v2_0_1_RC8
from loggers.logger import Logger
from oanda.stream import Stream as OandaPriceStream
from oanda.symbol_name_converter import SymbolNameConverter
from timeframe.timeframe import TimeFrame
import pandas as pd
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datahandlers.bars_provider.bars_provider import BarsProvider
import queue


class ZmqBarsProviderFromTickData(BarsProvider):
    def __init__(self, symbols: List[str], time_frame: TimeFrame, logger: Logger):
        self.symbols = symbols
        self.time_frame = time_frame
        self.logger = logger

        self.queues = dict((symbol, queue.Queue()) for (symbol) in symbols)

        self.opened_bars = dict((symbol, pd.DataFrame()) for (symbol) in symbols)
        self.opened_bars_finishes_at = dict((symbol, None) for (symbol) in symbols)
        self.opened_bars_starts_at = dict((symbol, None) for (symbol) in symbols)
        self.heartbeat_in_seconds = 1

    def get_queue(self, symbol: str) -> queue.Queue:
        return self.queues[symbol]

    def start_providing_bars(self) -> None:
        zmq = DWX_ZeroMQ_Connector_v2_0_1_RC8.DWX_ZeroMQ_Connector()
        symbols_normalized = SymbolNameConverter().convert_oanda_symbol_names_to_normalized_names(self.symbols)

        for symbol in symbols_normalized:
            zmq._DWX_MTX_SUBSCRIBE_MARKETDATA_(symbol)

        while True:
            for symbol in symbols_normalized:
                if symbol in zmq._Market_Data_DB and len(zmq._Market_Data_DB[symbol]) > 0:
                    last_datetime = list(zmq._Market_Data_DB[symbol].keys())[-1]
                    price_bid = zmq._Market_Data_DB[symbol][last_datetime][0]
                    price_ask = zmq._Market_Data_DB[symbol][last_datetime][1]

                    pass

            time.sleep(self.heartbeat_in_seconds)