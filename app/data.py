from __future__ import annotations

from typing import Dict, List

import pandas as pd
import yfinance as yf


def download_price_data(symbols: List[str], start: str, end: str) -> Dict[str, pd.DataFrame]:
    data: Dict[str, pd.DataFrame] = {}
    for symbol in symbols:
        ticker = yf.download(symbol, start=start, end=end, auto_adjust=False, progress=False, threads=False)
        if ticker.empty:
            continue
        ticker = ticker.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        })
        ticker.index.name = "date"
        data[symbol] = ticker
    return data
