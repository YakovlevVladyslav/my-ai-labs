"""Membership functions and rule base for lab 4, variant 7."""
from dataclasses import dataclass
from typing import Literal

import numpy as np
import skfuzzy as fuzz

Term = Literal["low", "medium", "high"]
State = Literal["normal", "overloaded", "critical"]

# Universes: channel utilization %, round-trip latency ms, error rate %, health severity /100.
UNIVERSES = {
    "load": np.linspace(0, 100, 1001),
    "latency": np.linspace(0, 300, 1201),
    "errors": np.linspace(0, 10, 1001),
    "state": np.linspace(0, 100, 1001),
}

MEMBERSHIPS = {
    "load": {
        "low": fuzz.trapmf(UNIVERSES["load"], [0, 0, 20, 45]),
        "medium": fuzz.trimf(UNIVERSES["load"], [25, 50, 75]),
        "high": fuzz.trapmf(UNIVERSES["load"], [55, 80, 100, 100]),
    },
    "latency": {
        "low": fuzz.trapmf(UNIVERSES["latency"], [0, 0, 30, 100]),
        "medium": fuzz.trimf(UNIVERSES["latency"], [60, 130, 200]),
        "high": fuzz.trapmf(UNIVERSES["latency"], [160, 230, 300, 300]),
    },
    "errors": {
        "low": fuzz.trapmf(UNIVERSES["errors"], [0, 0, 0.5, 2]),
        "medium": fuzz.trimf(UNIVERSES["errors"], [1, 3, 5]),
        "high": fuzz.trapmf(UNIVERSES["errors"], [4, 6, 10, 10]),
    },
    "state": {
        "normal": fuzz.trapmf(UNIVERSES["state"], [0, 0, 15, 40]),
        "overloaded": fuzz.trimf(UNIVERSES["state"], [30, 50, 70]),
        "critical": fuzz.trapmf(UNIVERSES["state"], [60, 85, 100, 100]),
    },
}

# Each leaf is a pair (variable, term); an expression is a tree of AND/OR operators.
Expression = tuple


def atom(variable: str, term: str) -> Expression:
    return ("atom", variable, term)


def AND(*children: Expression) -> Expression:
    return ("and", *children)


def OR(*children: Expression) -> Expression:
    return ("or", *children)


@dataclass(frozen=True)
class Rule:
    code: str
    description: str
    condition: Expression
    output: State


# The first nine correspond to the task statement (translated into English labels).
RULES = [
    Rule("R1", "Low load AND low latency → Normal", AND(atom("load", "low"), atom("latency", "low")), "normal"),
    Rule("R2", "High load AND high latency → Overloaded", AND(atom("load", "high"), atom("latency", "high")), "overloaded"),
    Rule("R3", "High load AND high errors → Critical", AND(atom("load", "high"), atom("errors", "high")), "critical"),
    Rule("R4", "Medium load AND medium latency → Overloaded", AND(atom("load", "medium"), atom("latency", "medium")), "overloaded"),
    Rule("R5", "Low errors AND low latency → Normal", AND(atom("errors", "low"), atom("latency", "low")), "normal"),
    Rule("R6", "High errors → Critical", atom("errors", "high"), "critical"),
    Rule("R7", "Low load AND high latency → Overloaded", AND(atom("load", "low"), atom("latency", "high")), "overloaded"),
    Rule("R8", "Medium load AND high errors → Critical", AND(atom("load", "medium"), atom("errors", "high")), "critical"),
    Rule("R9", "High load AND medium latency → Overloaded", AND(atom("load", "high"), atom("latency", "medium")), "overloaded"),
    # Additional rules cover network conditions omitted from the supplied examples.
    Rule("R10", "High load AND low latency → Overloaded", AND(atom("load", "high"), atom("latency", "low")), "overloaded"),
    Rule("R11", "Medium load AND low latency AND low errors → Normal", AND(atom("load", "medium"), atom("latency", "low"), atom("errors", "low")), "normal"),
    Rule("R12", "Low load AND medium latency → Normal", AND(atom("load", "low"), atom("latency", "medium")), "normal"),
    Rule("R13", "Medium load AND high latency → Overloaded", AND(atom("load", "medium"), atom("latency", "high")), "overloaded"),
    Rule("R14", "Medium errors AND (medium OR high latency) → Overloaded", AND(atom("errors", "medium"), OR(atom("latency", "medium"), atom("latency", "high"))), "overloaded"),
    Rule("R15", "Medium errors AND low latency → Overloaded", AND(atom("errors", "medium"), atom("latency", "low")), "overloaded"),
    Rule("R16", "High load AND medium errors → Overloaded", AND(atom("load", "high"), atom("errors", "medium")), "overloaded"),
    Rule("R17", "Low load AND medium errors → Overloaded", AND(atom("load", "low"), atom("errors", "medium")), "overloaded"),
]

LABELS = {
    "load": ("Загрузка канала", "%"),
    "latency": ("Задержка RTT", "мс"),
    "errors": ("Доля ошибок", "%"),
    "state": ("Состояние сети", "баллов"),
}
TERM_LABELS = {
    "load": {"low": "Низкая", "medium": "Средняя", "high": "Высокая"},
    "latency": {"low": "Малая", "medium": "Средняя", "high": "Большая"},
    "errors": {"low": "Низкая", "medium": "Средняя", "high": "Высокая"},
    "state": {"normal": "Нормальное", "overloaded": "Перегруженное", "critical": "Критическое"},
}
