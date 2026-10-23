"""Seasonal resource zones and the attraction they exert on animals."""
from dataclasses import dataclass
import numpy as np


@dataclass
class Resource:
    kind: str
    position: np.ndarray
    radius: float
    capacity: float = 100.0
    amount: float = 100.0
    available: bool = True

    @property
    def fraction(self) -> float:
        return self.amount / self.capacity


def resource_acceleration(positions: np.ndarray, resources: list[Resource], cfg) -> np.ndarray:
    """Point each animal towards its nearest detectable non-empty resource."""
    steering = np.zeros_like(positions)
    active = [r for r in resources if r.available and r.amount > 0]
    if not active:
        return steering

    world_size = np.array([cfg.world_width, cfg.world_height])
    for i, animal_pos in enumerate(positions):
        best_distance = float('inf')
        best_displacement = None
        for resource in active:
            delta = resource.position - animal_pos
            delta -= world_size * np.round(delta / world_size)
            distance = np.linalg.norm(delta)
            if distance < cfg.resource_detection_radius and distance < best_distance:
                best_distance = distance
                best_displacement = delta if distance > resource.radius else np.zeros(2)
        if best_displacement is not None:
            length = np.linalg.norm(best_displacement)
            if length > 1e-12:
                steering[i] = best_displacement / length * cfg.max_speed
    return steering


def update_resources(resources: list[Resource], positions: np.ndarray, step: int, cfg, rng) -> None:
    """Consume resources in occupied zones, replenish seasonally, relocate at season changes.

    A season lasts cfg.season_length steps. New seasons begin after step 0.
    During a dry season resources slowly regenerate; during a wet season
    they regenerate faster. Resource sites migrate to new locations at the
    beginning of each season, representing seasonally available patches.
    """
    if step > 0 and step % cfg.season_length == 0:
        for r in resources:
            r.position = rng.uniform([10, 10], [cfg.world_width - 10, cfg.world_height - 10])
            r.amount = cfg.season_start_fraction * r.capacity
            r.available = r.amount > 0

    season = (step // cfg.season_length) % 2
    regeneration = cfg.regeneration_wet if season == 0 else cfg.regeneration_dry
    size = np.array([cfg.world_width, cfg.world_height])
    for r in resources:
        delta = positions - r.position
        delta -= size * np.round(delta / size)
        inside = np.count_nonzero(np.linalg.norm(delta, axis=1) <= r.radius)
        r.amount = float(np.clip(
            r.amount + regeneration - inside * cfg.consumption_per_animal,
            0.0, r.capacity,
        ))
        r.available = r.amount > 0
