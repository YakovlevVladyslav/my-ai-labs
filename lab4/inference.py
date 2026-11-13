"""Explicit Mamdani: fuzzification, min/max inference, aggregation, centroid."""
from dataclasses import dataclass
import math

import numpy as np
import skfuzzy as fuzz

from fuzzy_model import MEMBERSHIPS, RULES, UNIVERSES, Expression


@dataclass
class InferenceResult:
    inputs: dict[str, float]
    memberships: dict[str, dict[str, float]]
    activations: dict[str, float]
    clipped: dict[str, np.ndarray]
    aggregated: np.ndarray
    score: float
    label: str


def validate_inputs(load: float, latency: float, errors: float) -> dict[str, float]:
    bounds = {"load": (load, 0, 100), "latency": (latency, 0, 300), "errors": (errors, 0, 10)}
    cleaned = {}
    for name, (raw, minimum, maximum) in bounds.items():
        if raw is None or isinstance(raw, bool):
            raise ValueError(f"Параметр '{name}' должен быть числом.")
        try:
            value = float(raw)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Параметр '{name}' должен быть числом.") from exc
        if not math.isfinite(value) or not minimum <= value <= maximum:
            raise ValueError(f"Параметр '{name}' должен находиться в диапазоне {minimum}–{maximum}.")
        cleaned[name] = value
    return cleaned


def evaluate_expression(expression: Expression, memberships: dict[str, dict[str, float]]) -> float:
    operator, *args = expression
    if operator == "atom":
        variable, term = args
        return memberships[variable][term]
    if operator == "and":
        return min(evaluate_expression(child, memberships) for child in args)
    if operator == "or":
        return max(evaluate_expression(child, memberships) for child in args)
    raise ValueError(f"Unknown operator: {operator}")


def interpret(score: float) -> str:
    if score <= 33:
        return "Нормальное"
    if score <= 66:
        return "Перегруженное"
    return "Критическое"


def infer(load: float, latency: float, errors: float) -> InferenceResult:
    inputs = validate_inputs(load, latency, errors)
    memberships = {
        variable: {
            term: float(fuzz.interp_membership(UNIVERSES[variable], values, inputs[variable]))
            for term, values in MEMBERSHIPS[variable].items()
        }
        for variable in inputs
    }
    activations = {rule.code: evaluate_expression(rule.condition, memberships) for rule in RULES}
    output_x = UNIVERSES["state"]
    clipped = {
        rule.code: np.minimum(activations[rule.code], MEMBERSHIPS["state"][rule.output])
        for rule in RULES
    }
    aggregated = np.maximum.reduce(list(clipped.values()))
    if not np.any(aggregated > 0):
        raise ValueError("Ни одно правило не активировалось: центроид не определён.")
    score = float(fuzz.defuzz(output_x, aggregated, "centroid"))
    return InferenceResult(inputs, memberships, activations, clipped, aggregated, score, interpret(score))
