"""Simple explanations and recommended diagnostic actions."""
from inference import InferenceResult


def get_recommendations(result: InferenceResult) -> list[str]:
    items: list[str] = []
    values = result.inputs
    if values["errors"] >= 4:
        items.append("Проверить сетевое оборудование, кабели, порты и счётчики ошибок интерфейсов.")
    elif values["errors"] >= 1:
        items.append("Проанализировать причины ошибок передачи и состояние интерфейсов.")
    if values["latency"] >= 160:
        items.append("Проверить маршрутизацию, очереди и задержки по пути (ping/traceroute).")
    elif values["latency"] >= 60:
        items.append("Проверить задержки и качество маршрута до целевого узла.")
    if values["load"] >= 75:
        items.append("Уменьшить фоновую нагрузку, настроить QoS или увеличить пропускную способность канала.")
    elif values["load"] >= 50:
        items.append("Проконтролировать загрузку канала и наиболее активные потоки трафика.")
    if not items:
        items.append("Сеть выглядит стабильной по выбранным метрикам. Продолжать мониторинг.")
    return items
