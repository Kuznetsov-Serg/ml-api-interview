# app/core/metrics.py
from prometheus_client import Counter, Histogram

# Счетчики для кэша
cache_hits_total = Counter(
    "cache_hits_total", "Total number of cache hits", ["endpoint"]
)

cache_misses_total = Counter(
    "cache_misses_total", "Total number of cache misses", ["endpoint"]
)

# Гистограмма для времени предсказания модели
model_prediction_latency = Histogram(
    "model_prediction_latency_seconds",
    "Latency of model predictions in seconds",
    ["endpoint", "model_type"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
