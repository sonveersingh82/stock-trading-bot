from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import yaml


@dataclass
class Settings:
    symbols: list[str]
    start_date: str
    end_date: str
    cash: float
    risk_per_trade: float
    max_positions: int
    fast_window: int
    slow_window: int
    trade_fee: float
    log_level: str


def load_settings(path: str = "config/settings.yaml") -> Settings:
    with open(path, "r", encoding="utf-8") as f:
        data: Dict[str, Any] = yaml.safe_load(f) or {}

    return Settings(
        symbols=data.get("symbols", ["AAPL", "MSFT"]),
        start_date=data.get("start_date", "2022-01-01"),
        end_date=data.get("end_date", "2024-01-01"),
        cash=float(data.get("cash", 100000)),
        risk_per_trade=float(data.get("risk_per_trade", 0.01)),
        max_positions=int(data.get("max_positions", 3)),
        fast_window=int(data.get("fast_window", 10)),
        slow_window=int(data.get("slow_window", 30)),
        trade_fee=float(data.get("trade_fee", 0.001)),
        log_level=str(data.get("log_level", "INFO")),
    )


def get_api_key(name: str) -> Optional[str]:
    return os.getenv(name)
