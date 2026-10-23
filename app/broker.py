from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd


logger = logging.getLogger(__name__)


@dataclass
class Position:
    symbol: str
    side: str
    quantity: int
    entry_price: float
    value: float


class PaperBroker:
    def __init__(self, cash: float = 100000.0, trade_fee: float = 0.001):
        self.cash = cash
        self.trade_fee = trade_fee
        self.positions: Dict[str, Position] = {}
        self.trade_log: List[Dict[str, float]] = []

    def buy(self, symbol: str, quantity: int, price: float) -> Dict[str, float]:
        notional = quantity * price
        fee = notional * self.trade_fee
        total = notional + fee

        if total > self.cash:
            raise ValueError(f"Not enough cash for {symbol}")

        self.cash -= total
        self.positions[symbol] = Position(
            symbol=symbol,
            side="long",
            quantity=quantity,
            entry_price=price,
            value=notional,
        )
        self.trade_log.append({"symbol": symbol, "side": "buy", "quantity": quantity, "price": price, "fee": fee})
        logger.info("Bought %s %s at %.2f", quantity, symbol, price)
        return {"symbol": symbol, "quantity": quantity, "price": price, "fee": fee}

    def sell(self, symbol: str, quantity: int, price: float) -> Dict[str, float]:
        if symbol not in self.positions:
            raise ValueError(f"No position to sell for {symbol}")

        pos = self.positions[symbol]
        if quantity > pos.quantity:
            raise ValueError(f"Trying to sell too many shares of {symbol}")

        sale_value = quantity * price
        fee = sale_value * self.trade_fee
        self.cash += sale_value - fee

        remaining = pos.quantity - quantity
        if remaining <= 0:
            del self.positions[symbol]
        else:
            pos.quantity = remaining
            pos.value = remaining * price

        self.trade_log.append({"symbol": symbol, "side": "sell", "quantity": quantity, "price": price, "fee": fee})
        logger.info("Sold %s %s at %.2f", quantity, symbol, price)
        return {"symbol": symbol, "quantity": quantity, "price": price, "fee": fee}

    def market_value(self, prices: Dict[str, float]) -> float:
        value = self.cash
        for symbol, pos in self.positions.items():
            value += pos.quantity * prices.get(symbol, pos.entry_price)
        return value
