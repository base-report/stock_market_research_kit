from .trade import Trade
from utils.trading_utils import (
    calculate_sma,
    calculate_adr_pct,
    calculate_volume,
    get_prior_range,
    get_consolidation_candles,
    is_breakout,
)

# Entry parameters
min_prior_move = 0.5
prior_move_days = 50
min_adr_percent = 0.035
min_volume = 100000
min_consolidation_days = 5
max_consolidation_days = 40
consolidation_range_mult = 2
breakout_percent_mult = 0.75

# Partial sell parameters
partial_sell_day_start = 3
partial_sell_day_end = 5
partial_sell_adr_mult = 1

# Exit parameters
exit_sma_days = 10


def backtest(daily_candles):
    # Array to store trades
    trades = []

    # Current combo being formed
    current_combo = None
    trade = None

    for i in range(len(daily_candles)):
        if i <= exit_sma_days:
            continue

        new_candle = daily_candles[i - 1]

        if not current_combo or not trade:
            # Check for entry
            prev_candle = daily_candles[i - 2]
            prior_range_candles = daily_candles[i - (prior_move_days + 2) : i - 1]
            possible_consolidation_candles = daily_candles[
                i - (max_consolidation_days + 2) : i - 1
            ]
            entry = look_for_entry(
                prev_candle,
                new_candle,
                prior_range_candles,
                possible_consolidation_candles,
            )

            # If entry, start a new combo
            if entry:
                current_combo = [new_candle]
                trade = Trade()
                trade.entry = entry
        else:
            # Add to current combo
            current_combo.append(new_candle)

            # Check for partial sell
            current_day = len(current_combo)
            partial_target = look_for_partial_target(trade, current_day, new_candle)
            if partial_target:
                trade.partial_target = partial_target

            # Check for exit
            end_sma = calculate_sma(daily_candles[i - exit_sma_days : i])
            exit = look_for_exit(trade, current_combo, end_sma)

            if exit:
                trade.exit = exit
                trades.append(trade)

                # Reset the current combo
                current_combo = None

                # Reset the trade
                trade = None

    return trades


def look_for_entry(
    prev_candle, new_candle, prior_range_candles, possible_consolidation_candles
):
    adr20 = calculate_adr_pct(prior_range_candles, 20)
    if adr20 < min_adr_percent:
        return None

    volume20 = calculate_volume(prior_range_candles)
    if volume20 < min_volume:
        return None

    prior_range = get_prior_range(prior_range_candles, prior_move_days)
    if prior_range["range"] <= min_prior_move:
        return None

    is_entry_above_half_range = (
        new_candle[0]
        >= prior_range["low"] + (prior_range["high"] - prior_range["low"]) * 0.5
    )
    if not is_entry_above_half_range:
        return None

    consolidation_range_pct = consolidation_range_mult * adr20
    consolidation_candles = get_consolidation_candles(
        possible_consolidation_candles,
        min_consolidation_days,
        max_consolidation_days,
        consolidation_range_pct,
    )

    if not consolidation_candles:
        return None

    breakout_pct = breakout_percent_mult * adr20
    breakout = is_breakout(
        new_candle[3], prev_candle[3], consolidation_candles, breakout_pct
    )

    if breakout:
        return {
            "date": new_candle[5],
            "entry_price": new_candle[3],
            "initial_stop": new_candle[2],
            "consolidation_days": len(consolidation_candles),
            "adr20": round(adr20, 4),
            "volume20": round(volume20, 0),
        }
    else:
        return None


def look_for_partial_target(trade, current_day, new_candle):
    # Make partial sell between partial_sell_day_start and partial_sell_day_end
    # if sell target is met, sell at that price, otherwise sell at the close of day 5
    if partial_sell_day_start <= current_day <= partial_sell_day_end:
        if trade.partial_target:
            return None

        target_price = trade.entry["entry_price"] * (
            1 + trade.entry["adr20"] * partial_sell_adr_mult
        )

        if new_candle[1] >= target_price:
            return {
                "date": new_candle[5],
                "sell_price": round(target_price, 4),
                "target_reached": True,
            }
        elif current_day == partial_sell_day_end:
            return {
                "date": new_candle[5],
                "sell_price": round(new_candle[3], 4),
                "target_reached": False,
            }


def look_for_exit(trade, current_combo, end_sma):
    candle = current_combo[-1]
    hit_initial_stop = candle[2] <= trade.entry["initial_stop"]
    made_partial_sale_and_close_below_entry_price = (
        trade.partial_target
        and candle[3] <= trade.entry["entry_price"]
        and trade.partial_target["date"] != candle[5]
    )
    close_below_end_sma = candle[3] <= end_sma
    met_exit_condition = (
        hit_initial_stop
        or made_partial_sale_and_close_below_entry_price
        or close_below_end_sma
    )

    if met_exit_condition:
        exit_price = candle[3]
        reason = "HIT_INITIAL_STOP"

        if hit_initial_stop:
            gap_down = trade.entry["initial_stop"] < candle[0]
            if gap_down:
                exit_price = candle[0]
            else:
                exit_price = trade.entry["initial_stop"]
        elif made_partial_sale_and_close_below_entry_price:
            gap_down = trade.entry["entry_price"] < candle[0]
            reason = "TRY_BREAKEVEN_STOP"
            if gap_down:
                exit_price = candle[0]
            else:
                exit_price = trade.entry["entry_price"]
        elif close_below_end_sma:
            reason = "CLOSE_BELOW_SMA"

        return {
            "date": candle[5],
            "exit_price": exit_price,
            "reason": reason,
            "days_held": len(current_combo),
        }
    else:
        return None