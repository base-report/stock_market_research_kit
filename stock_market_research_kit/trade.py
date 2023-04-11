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
    partial_target: dict = None
    # partial_target: dict = field(
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
