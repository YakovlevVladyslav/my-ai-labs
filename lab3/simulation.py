import numpy as np

from animal import boids_acceleration, limit_vectors
from config import Config
from resource import Resource, resource_acceleration, update_resources
from predator import Predator, predator_avoidance, update_predators


class Simulation:
    def __init__(self, config: Config):
        self.config = config
        self.rng = np.random.default_rng(config.seed)
        self.positions = self.rng.uniform(
            [0, 0], [config.world_width, config.world_height],
            size=(config.animal_count, 2),
        )
        angles = self.rng.uniform(0, 2 * np.pi, size=config.animal_count)
        self.velocities = np.column_stack((np.cos(angles), np.sin(angles))) * config.max_speed * 0.6
        self.resources = [
            Resource('food', np.array([20.0, 25.0]), 8.0),
            Resource('food', np.array([78.0, 75.0]), 9.0),
            Resource('water', np.array([25.0, 80.0]), 7.0),
            Resource('water', np.array([80.0, 25.0]), 8.0),
        ]
        if config.predator_count < 0:
            raise ValueError('predator_count must be non-negative')
        self.predators = []
        size = np.array([config.world_width, config.world_height])
        for _ in range(config.predator_count):
            # Avoid a predator starting directly on top of an animal.
            for attempt in range(1000):
                pos = self.rng.uniform([0, 0], size)
                delta = self.positions - pos
                delta -= size * np.round(delta / size)
                if np.min(np.linalg.norm(delta, axis=1)) >= config.predator_safe_spawn_distance:
                    break
            else:
                raise ValueError('Cannot place predators safely; reduce predator_count or safe spawn distance')
            angle = self.rng.uniform(0, 2 * np.pi)
            vel = np.array([np.cos(angle), np.sin(angle)]) * config.predator_speed * 0.5
            self.predators.append(Predator(pos, vel))
        self.threatened = np.zeros(config.animal_count, dtype=bool)
        self.step_number = 0

    @property
    def season(self) -> str:
        return 'Влажный' if (self.step_number // self.config.season_length) % 2 == 0 else 'Сухой'

    def step(self):
        cfg = self.config
        boids = boids_acceleration(self.positions, self.velocities, cfg)
        foraging = resource_acceleration(self.positions, self.resources, cfg)
        escape, self.threatened = predator_avoidance(self.positions, self.predators, cfg)
        # Nearby threats override foraging: prioritize escape over resources.
        combined = (boids + cfg.foraging_weight * foraging * (~self.threatened)[:, None]
                    + cfg.predator_avoidance_weight * escape)
        acceleration = limit_vectors(combined, cfg.max_force)
        self.velocities = limit_vectors(self.velocities + acceleration, cfg.max_speed)
        size = np.array([cfg.world_width, cfg.world_height])
        self.positions = (self.positions + self.velocities) % size
        self.step_number += 1
        update_resources(self.resources, self.positions, self.step_number, cfg, self.rng)
        update_predators(self.predators, self.positions, cfg, self.rng)
