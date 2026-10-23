from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class Signal:
    symbol: str
    action: str
    confidence: float
    reason: str


class SimpleMovingAverageStrategy:
    def __init__(self, fast_window: int = 10, slow_window: int = 30):
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self, df: pd.DataFrame) -> Optional[Signal]:
        if df.empty:
            return None

        close = df["close"].astype(float)
        if len(close) < self.slow_window:
            return None

        fast_ma = close.rolling(self.fast_window).mean()
        slow_ma = close.rolling(self.slow_window).mean()

        current_close = float(close.iloc[-1])
        prev_fast = float(fast_ma.iloc[-2]) if len(fast_ma) >= 2 else float(fast_ma.iloc[-1])
        prev_slow = float(slow_ma.iloc[-2]) if len(slow_ma) >= 2 else float(slow_ma.iloc[-1])
        current_fast = float(fast_ma.iloc[-1])
        current_slow = float(slow_ma.iloc[-1])

        if prev_fast <= prev_slow and current_fast > current_slow:
            return Signal(
                symbol="",
                action="buy",
                confidence=min(0.99, max(0.5, (current_fast / current_slow) - 1 + 0.5)),
                reason="Fast MA crossed above slow MA",
            )

        if prev_fast >= prev_slow and current_fast < current_slow:
            return Signal(
                symbol="",
                action="sell",
                confidence=min(0.99, max(0.5, (current_slow / current_fast) - 1 + 0.5)),
                reason="Fast MA crossed below slow MA",
            )

        return Signal(
            symbol="",
            action="hold",
            confidence=0.0,
            reason="No signal",
        )

    def signals_for_symbol(self, symbol: str, df: pd.DataFrame) -> Optional[Signal]:
        signal = self.generate_signals(df)
        if signal is None:
            return None
        signal.symbol = symbol
        return signal
