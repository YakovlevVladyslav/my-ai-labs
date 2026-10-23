import numpy as np

from config import Config


def limit_vectors(vectors: np.ndarray, maximum: float) -> np.ndarray:
    """Limit vector lengths while preserving their directions."""
    lengths = np.linalg.norm(vectors, axis=-1, keepdims=True)
    factors = np.minimum(1.0, maximum / np.maximum(lengths, 1e-12))
    return vectors * factors


def boids_acceleration(positions: np.ndarray, velocities: np.ndarray, cfg: Config) -> np.ndarray:
    """Compute steering for all animals from the same snapshot.

    Positions have shape (N, 2). Distances use toroidal (wrap-around) geometry.
    """
    n = len(positions)
    acceleration = np.zeros_like(positions)
    world_size = np.array([cfg.world_width, cfg.world_height])

    for i in range(n):
        displacement = positions - positions[i]
        displacement -= world_size * np.round(displacement / world_size)
        distances = np.linalg.norm(displacement, axis=1)

        neighbors = (distances > 0) & (distances < cfg.neighbor_radius)
        close = (distances > 0) & (distances < cfg.separation_radius)

        cohesion = np.zeros(2)
        alignment = np.zeros(2)
        separation = np.zeros(2)

        if np.any(neighbors):
            cohesion = displacement[neighbors].mean(axis=0)
            alignment = velocities[neighbors].mean(axis=0) - velocities[i]

        if np.any(close):
            # Displacement points from us to the neighbor, so invert it to repel.
            separation = (-displacement[close] / np.maximum(distances[close, None] ** 2, 1e-9)).mean(axis=0)

        steering = (
            cfg.cohesion_weight * cohesion
            + cfg.alignment_weight * alignment
            + cfg.separation_weight * separation
        )
        acceleration[i] = limit_vectors(steering, cfg.max_force)

    return acceleration
