from __future__ import annotations

import logging
from typing import Dict

import pandas as pd

from app.config import Settings
from app.data import download_price_data
from app.strategies import SimpleMovingAverageStrategy

logger = logging.getLogger(__name__)


class PaperTrader:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.strategy = SimpleMovingAverageStrategy(
            fast_window=settings.fast_window,
            slow_window=settings.slow_window,
        )
        self.positions: Dict[str, dict] = {}
        self.cash = settings.cash
        self.trade_history = []
        self.current_prices: Dict[str, float] = {}

    def position_size(self, price: float) -> int:
        risk_budget = self.settings.cash * self.settings.risk_per_trade
        quantity = int(risk_budget / max(price, 1.0))
        return max(1, quantity)

    def run(self, data_by_symbol: Dict[str, pd.DataFrame]):
        for symbol, df in data_by_symbol.items():
            if df.empty:
                continue

            signal = self.strategy.signals_for_symbol(symbol, df)
            if signal is None:
                continue

            price = float(df["close"].iloc[-1])
            self.current_prices[symbol] = price

            if signal.action == "buy" and len(self.positions) < self.settings.max_positions:
                qty = self.position_size(price)
                if qty * price > self.cash:
                    qty = max(1, int(self.cash / max(price, 1.0)))

                self.positions[symbol] = {"symbol": symbol, "quantity": qty, "entry_price": price}
                self.cash -= qty * price * (1 + self.settings.trade_fee)
                self.trade_history.append({"symbol": symbol, "action": "buy", "quantity": qty, "price": price})
                logger.info("BUY %s @ %.2f", symbol, price)

            elif signal.action == "sell" and symbol in self.positions:
                qty = self.positions[symbol]["quantity"]
                self.cash += qty * price * (1 - self.settings.trade_fee)
                self.trade_history.append({"symbol": symbol, "action": "sell", "quantity": qty, "price": price})
                del self.positions[symbol]
                logger.info("SELL %s @ %.2f", symbol, price)

    def summary(self) -> Dict[str, float]:
        portfolio_value = self.cash + sum(
            pos["quantity"] * self.current_prices.get(pos["symbol"], pos["entry_price"]) for pos in self.positions.values()
        )
        return {
            "cash": self.cash,
            "positions": len(self.positions),
            "portfolio_value": portfolio_value,
            "trade_count": len(self.trade_history),
        }
