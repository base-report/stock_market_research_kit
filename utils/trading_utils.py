import math
from datetime import datetime
from typing import List, Tuple


def calculate_sma(candles: List[Tuple[float]]) -> float:
    if len(candles) == 0:
        return 0
    return sum([candle[3] for candle in candles]) / len(candles)


def calculate_volume(candles: List[Tuple[float]], x: int = 20) -> float:
    last_x = candles[-x:]
    if len(last_x) == 0:
        return 0
    return sum([d[4] for d in last_x]) / len(last_x)


def get_high_low(
    candles: List[Tuple[float]], days: int = 20
) -> Tuple[float, str, float, str]:
    start = len(candles) - days if len(candles) > days else 0
    candles = candles[start:]
    high, high_timestamp, low, low_timestamp = -1, -1, -1, -1

    for _, h, l, _, _, t in candles:
        if h == math.inf or l == math.inf:
            continue
        if high_timestamp == -1:
            high, high_timestamp, low, low_timestamp = h, t, l, t
        else:
            if h >= high:
                high, high_timestamp = h, t
            if l <= low:
                low, low_timestamp = l, t

    return high, high_timestamp, low, low_timestamp


def calculate_adr_pct(candles: List[Tuple[float]], x: int = 20) -> float:
    last_x = candles[-x:]
    if len(candles) == 0:
        return 0
    adr = sum([d[1] / d[2] if d[2] != 0 else 0 for d in last_x]) / len(last_x) - 1
    return 0 if math.isnan(adr) else adr


def get_prior_range(candles, days=20):
    high, high_timestamp, low, low_timestamp = get_high_low(candles, days)

    # Convert timestamps to datetime objects
    high_date = datetime.strptime(high_timestamp, "%Y-%m-%d")
    low_date = datetime.strptime(low_timestamp, "%Y-%m-%d")

    if high == 0 or low == 0:
        return {"range": 0, "high": 0, "low": 0}

    if high_date > low_date:
        range_result = (high - low) / low
        return {"range": range_result, "high": high, "low": low}
    else:
        range_result = (low - high) / high
        return {"range": range_result, "high": high, "low": low}


def get_consolidation_candles(
    candles: List[Tuple[float]],
    min_days: int = 5,
    max_days: int = 15,
    range_percent: float = 0.3,
) -> List[Tuple[float]]:
    consolidation_candles = []

    for days in range(min_days, max_days + 1):
        current_segment = candles[-days:]
        high, _, low, _ = get_high_low(current_segment, days)
        range_ = high - low

        if range_ / low <= range_percent:
            consolidation_candles = current_segment

    return consolidation_candles if len(consolidation_candles) >= min_days else []


def calculate_theil_sen_slope(candles: List[Tuple[float]]) -> float:
    n = len(candles)
    slopes = []

    for i in range(n - 1):
        for j in range(i + 1, n):
            slope = (candles[j][1] - candles[i][1]) / (j - i)
            slopes.append(slope)

    slopes.sort()
    return slopes[len(slopes) // 2]


def calculate_theil_sen_intercept(
    candles: List[Tuple[float]], median_slope: float
) -> float:
    n = len(candles)
    intercepts = []

    for i in range(n):
        intercept = candles[i][1] - median_slope * i
        intercepts.append(intercept)

    intercepts.sort()
    return intercepts[len(intercepts) // 2]


def is_breakout(
    new_close: float,
    prev_close: float,
    consolidation_candles: List[Tuple[float]],
    breakout_pct: float,
) -> bool:
    median_slope = calculate_theil_sen_slope(consolidation_candles)
    median_intercept = calculate_theil_sen_intercept(
        consolidation_candles, median_slope
    )
    last_idx = len(consolidation_candles) - 1
    trendline_value = median_slope * last_idx + median_intercept

    return new_close > prev_close and new_close > trendline_value * (1 + breakout_pct)
