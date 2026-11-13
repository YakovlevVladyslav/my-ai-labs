import numpy as np
import pytest
from fuzzy_model import RULES
from inference import infer, validate_inputs, evaluate_expression


def test_all_rules_present():
    assert len(RULES) >= 9
    assert {r.code for r in RULES}.issuperset({f"R{i}" for i in range(1,10)})


def test_classic_cases():
    normal = infer(0, 0, 0)
    overloaded = infer(100, 300, 0)
    critical = infer(100, 300, 10)
    assert normal.label == "Нормальное"
    assert overloaded.label == "Перегруженное"
    assert critical.label == "Критическое"
    assert normal.score < overloaded.score < critical.score


def test_or_is_max():
    values = {"load": {"high": .2}, "latency": {"high": .8}}
    assert evaluate_expression(("or", ("atom", "load", "high"), ("atom", "latency", "high")), values) == .8


@pytest.mark.parametrize("values", [(101, 10, 1), (10, -1, 1), (10, 10, 11), (float("nan"), 10, 1), (None, 10, 1), ("wrong", 10, 1)])
def test_bad_inputs(values):
    with pytest.raises(ValueError):
        validate_inputs(*values)


def test_outputs_are_finite_and_aggregated():
    for load in (0, 20, 40, 60, 80, 100):
        for latency in (0, 60, 120, 180, 240, 300):
            for errors in (0, 1, 3, 5, 8, 10):
                result = infer(load, latency, errors)
                assert np.isfinite(result.score)
                assert 0 <= result.score <= 100
                assert np.any(result.aggregated > 0)
