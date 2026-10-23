from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    world_width: float = 100.0
    world_height: float = 100.0
    animal_count: int = 40
    neighbor_radius: float = 16.0
    separation_radius: float = 5.0
    cohesion_weight: float = 0.015
    alignment_weight: float = 0.08
    separation_weight: float = 0.18
    foraging_weight: float = 0.11
    resource_detection_radius: float = 48.0
    max_speed: float = 1.4
    max_force: float = 0.12

    # Stage 3: seasons and resource consumption.
    season_length: int = 150
    consumption_per_animal: float = 1.5
    regeneration_wet: float = 0.8
    regeneration_dry: float = 0.1
    season_start_fraction: float = 0.65

    # Stage 4: predators and danger response.
    predator_count: int = 2
    predator_speed: float = 1.15
    predator_max_force: float = 0.09
    predator_detection_radius: float = 19.0
    predator_avoidance_weight: float = 0.85
    predator_chase_radius: float = 55.0
    predator_wander_weight: float = 0.18
    predator_safe_spawn_distance: float = 12.0

    steps: int = 600
    interval_ms: int = 30
    seed: int = 42
