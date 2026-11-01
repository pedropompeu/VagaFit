from prometheus_client import Counter


def counter_value(counter: Counter, **labels: str) -> float:
    """Valor atual de um contador (com rótulos, se houver)."""
    for metric in counter.collect():
        for sample in metric.samples:
            if sample.name.endswith("_total") and sample.labels == labels:
                return sample.value
    return 0.0
