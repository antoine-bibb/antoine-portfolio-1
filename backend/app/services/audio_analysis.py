from statistics import mean


def normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    low, high = min(values), max(values)
    if high == low:
        return [50.0 for _ in values]
    return [((x - low) / (high - low)) * 100 for x in values]


def detect_loudness_peaks(rms_windows: list[float]) -> list[float]:
    baseline = mean(rms_windows) if rms_windows else 0
    return [max(0.0, x - baseline) for x in rms_windows]
