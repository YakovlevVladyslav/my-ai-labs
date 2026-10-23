"""Metrics for Boids migration experiments (toroidal map)."""
import numpy as np


def measure(sim):
    """Measure after a completed simulation step."""
    cfg = sim.config
    pos, vel = sim.positions, sim.velocities
    size = np.array([cfg.world_width, cfg.world_height])
    n = len(pos)
    d = pos[:, None, :] - pos[None, :, :]
    d -= size * np.round(d / size)
    dist = np.linalg.norm(d, axis=2)
    np.fill_diagonal(dist, np.inf)
    nearest = dist.min(axis=1)
    speed = np.linalg.norm(vel, axis=1)
    unit = np.divide(vel, speed[:, None], out=np.zeros_like(vel), where=speed[:, None] > 1e-12)
    # Polarization is 1 if headings are aligned and near 0 if they cancel out.
    polarization = float(np.linalg.norm(unit.mean(axis=0)))
    resource_occupancy = 0
    for r in sim.resources:
        if r.available:
            delta = pos - r.position
            delta -= size * np.round(delta / size)
            resource_occupancy += int((np.linalg.norm(delta, axis=1) <= r.radius).sum())
    min_pred_distance = float('nan')
    if sim.predators:
        pred = np.array([p.position for p in sim.predators])
        pd = pos[:, None, :] - pred[None, :, :]
        pd -= size * np.round(pd / size)
        min_pred_distance = float(np.linalg.norm(pd, axis=2).min())
    # Recalculate danger from current positions, not the previous step's mask.
    threatened_now = 0
    if sim.predators:
        pred = np.array([p.position for p in sim.predators])
        pd = pos[:, None, :] - pred[None, :, :]
        pd -= size * np.round(pd / size)
        threatened_now = int((np.linalg.norm(pd, axis=2) < cfg.predator_detection_radius).any(axis=1).sum())
    return dict(
        step=sim.step_number,
        polarization=polarization,
        mean_nearest_distance=float(nearest.mean()),
        threatened_fraction=threatened_now / n,
        animals_at_resources=resource_occupancy,
        mean_resource_fraction=float(np.mean([r.fraction for r in sim.resources])),
        min_predator_distance=min_pred_distance,
    )
