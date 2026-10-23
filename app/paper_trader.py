from __future__ import annotations

import logging
from typing import Dict

import pandas as pd

from app.config import Settings
from app.data import download_price_data
from app.paper_trader import PaperTrader

logger = logging.getLogger(__name__)


def run_backtest(settings: Settings) -> Dict[str, float]:
    price_data = download_price_data(settings.symbols, settings.start_date, settings.end_date)
    trader = PaperTrader(settings)
    trader.run(price_data)
    return trader.summary()
