"""Predator pursuit and steering away from nearby threats."""
from dataclasses import dataclass
import numpy as np
from animal import limit_vectors


@dataclass
class Predator:
    position: np.ndarray
    velocity: np.ndarray


def wrapped_displacement(destination, origin, world_size):
    """Shortest vector from origin to destination on a toroidal map."""
    delta = np.asarray(destination) - np.asarray(origin)
    return delta - world_size * np.round(delta / world_size)


def predator_avoidance(positions, predators: list[Predator], cfg):
    """Return an escape direction and mask of animals detecting a predator."""
    steering = np.zeros_like(positions)
    threatened = np.zeros(len(positions), dtype=bool)
    if not predators:
        return steering, threatened
    size = np.array([cfg.world_width, cfg.world_height])
    for predator in predators:
        delta = wrapped_displacement(positions, predator.position, size)
        distances = np.linalg.norm(delta, axis=1)
        nearby = distances < cfg.predator_detection_radius
        threatened |= nearby
        # Weight close threats more strongly; avoid division by zero.
        steering[nearby] += delta[nearby] / np.maximum(distances[nearby, None], 0.01) ** 2
    lengths = np.linalg.norm(steering, axis=1, keepdims=True)
    active = lengths[:, 0] > 1e-12
    steering[active] /= lengths[active]
    return steering, threatened


def update_predators(predators: list[Predator], animal_positions, cfg, rng):
    """Chase the nearest visible animal, otherwise wander slightly."""
    size = np.array([cfg.world_width, cfg.world_height])
    for predator in predators:
        delta = wrapped_displacement(animal_positions, predator.position, size)
        distances = np.linalg.norm(delta, axis=1)
        nearest = int(np.argmin(distances))
        if distances[nearest] <= cfg.predator_chase_radius:
            desired = delta[nearest] / max(distances[nearest], 1e-12) * cfg.predator_speed
        else:
            desired = predator.velocity + rng.normal(0, cfg.predator_wander_weight, 2)
            desired = limit_vectors(desired, cfg.predator_speed)
        acceleration = limit_vectors(desired - predator.velocity, cfg.predator_max_force)
        predator.velocity = limit_vectors(predator.velocity + acceleration, cfg.predator_speed)
        predator.position = (predator.position + predator.velocity) % size
