from dataclasses import dataclass, field


@dataclass
class Trade:
    entry: dict = field(
        default_factory=lambda: {
            "date": "",
            "entry_price": -1,
            "initial_stop": -1,
            "consolidation_days": -1,
            "adr20": -1,
            "volume20": -1,
        }
    )
    partial: dict = None
    # partial: dict = field(
    #     default_factory=lambda: {
    #         "date": "",
    #         "sell_price": -1,
    #         "target_reached": False,
    #     }
    # )
    exit: dict = field(
        default_factory=lambda: {
            "date": "",
            "exit_price": -1,
            "reason": "TRY_INITIAL_STOP",  # TRY_INITIAL_STOP, TRY_BREAKEVEN_STOP, CLOSE_BELOW_SMA
            "days_held": -1,
        }
    )

    def to_db_format(self, symbol: str):
        return {
            "symbol": symbol,
            "entry_date": self.entry["date"],
            "entry_price": self.entry["entry_price"],
            "initial_stop": self.entry["initial_stop"],
            "consolidation_days": self.entry["consolidation_days"],
            "adr20": self.entry["adr20"],
            "volume20": self.entry["volume20"],
            "partial_target_date": None
            if self.partial is None
            else self.partial["date"],
            "partial_target_price": None
            if self.partial is None
            else self.partial["sell_price"],
            "partial_target_reached": None
            if self.partial is None
            else self.partial["target_reached"],
            "exit_date": self.exit["date"],
            "exit_price": self.exit["exit_price"],
            "exit_reason": self.exit["reason"],
            "days_held": self.exit["days_held"],
        }
