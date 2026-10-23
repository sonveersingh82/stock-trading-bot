from __future__ import annotations

import logging
from typing import Dict, List

import pandas as pd

from app.config import Settings
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
        self.trade_history: List[dict] = []
        self.current_prices: Dict[str, float] = {}

    def position_size(self, symbol: str, price: float) -> int:
        max_risk = self.settings.cash * self.settings.risk_per_trade
        share_value = max_risk / max(price, 1.0)
        return max(1, int(share_value))

    def run(self, data_by_symbol: Dict[str, pd.DataFrame]):
        for symbol, df in data_by_symbol.items():
            if df.empty:
                continue
            signal = self.strategy.signals_for_symbol(symbol, df)
            if signal is None or signal.action == "hold":
                continue

            price = float(df["close"].iloc[-1])
            self.current_prices[symbol] = price

            if signal.action == "buy":
                if len(self.positions) >= self.settings.max_positions:
                    logger.info("Max positions reached; skipping buy for %s", symbol)
                    continue

                qty = self.position_size(symbol, price)
                if qty <= 0:
                    continue

                total = qty * price
                if total > self.cash:
                    qty = max(1, int(self.cash / max(price, 1.0)))

                if qty <= 0:
                    continue

                self.positions[symbol] = {"symbol": symbol, "quantity": qty, "entry_price": price}
                self.cash -= qty * price * (1 + self.settings.trade_fee)
                self.trade_history.append({"symbol": symbol, "action": "buy", "quantity": qty, "price": price})
                logger.info("Bought %s shares of %s at %.2f", qty, symbol, price)

            elif signal.action == "sell":
                if symbol not in self.positions:
                    continue

                pos = self.positions[symbol]
                qty = pos["quantity"]
                self.cash += qty * price * (1 - self.settings.trade_fee)
                self.trade_history.append({"symbol": symbol, "action": "sell", "quantity": qty, "price": price})
                del self.positions[symbol]
                logger.info("Sold %s shares of %s at %.2f", qty, symbol, price)

    def summary(self) -> Dict[str, float]:
        return {
            "cash": self.cash,
            "positions": len(self.positions),
            "portfolio_value": self.cash + sum(pos["quantity"] * self.current_prices.get(pos["symbol"], pos["entry_price"]) for pos in self.positions.values()),
        }
