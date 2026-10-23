import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

from simulation import Simulation

RESOURCE_STYLES = {'food': ('forestgreen', 'Пища'), 'water': ('dodgerblue', 'Вода')}


def run_animation(simulation: Simulation) -> None:
    cfg = simulation.config
    fig, ax = plt.subplots(figsize=(9, 8))
    fig.subplots_adjust(right=0.81)
    ax.set_xlim(0, cfg.world_width)
    ax.set_ylim(0, cfg.world_height)
    ax.set_aspect('equal')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    title = ax.set_title('Миграция животных — шаг 0')

    patches = []
    labels = []
    for resource in simulation.resources:
        color, label = RESOURCE_STYLES[resource.kind]
        patch = Circle(resource.position, resource.radius, facecolor=color,
                       edgecolor=color, alpha=0.22, linewidth=2)
        ax.add_patch(patch)
        text = ax.text(*resource.position, '', ha='center', va='center',
                       color=color, weight='bold', fontsize=9)
        patches.append(patch)
        labels.append((text, label))

    arrows = ax.quiver(
        simulation.positions[:, 0], simulation.positions[:, 1],
        simulation.velocities[:, 0], simulation.velocities[:, 1],
        color='darkorange', angles='xy', scale_units='xy', scale=0.22, width=0.006,
    )
    predator_markers = ax.scatter(
        [p.position[0] for p in simulation.predators],
        [p.position[1] for p in simulation.predators],
        c='crimson', marker='X', s=140, label='Хищники', zorder=5,
    )
    if simulation.predators:
        ax.legend(loc='lower left')
    info = fig.text(0.83, 0.78, '', fontsize=10, va='top')

    def update_display():
        for resource, patch, (label_artist, label) in zip(simulation.resources, patches, labels):
            patch.center = resource.position
            patch.set_alpha(0.08 + 0.35 * resource.fraction)
            label_artist.set_position(resource.position)
            label_artist.set_text(f'{label}\n{resource.amount:.0f}%')
        title.set_text(f'Миграция животных — шаг {simulation.step_number}/{cfg.steps}')
        info.set_text(f'Сезон:\n{simulation.season}\n\nХищники: {len(simulation.predators)}'
                      f'\nВ опасности: {simulation.threatened.sum()}\n\nРесурсы:\n' + '\n'.join(
            f'{r.kind}: {r.amount:.0f}%' for r in simulation.resources))

    update_display()

    def update(_frame):
        simulation.step()
        arrows.set_offsets(simulation.positions)
        arrows.set_UVC(simulation.velocities[:, 0], simulation.velocities[:, 1])
        if simulation.predators:
            predator_markers.set_offsets([p.position for p in simulation.predators])
        else:
            predator_markers.set_offsets(np.empty((0, 2)))
        arrows.set_color(['crimson' if danger else 'darkorange' for danger in simulation.threatened])
        update_display()
        return (arrows, predator_markers, title, info, *patches, *(t for t, _ in labels))

    animation = FuncAnimation(fig, update, frames=cfg.steps,
                              interval=cfg.interval_ms, blit=False, repeat=False)
    plt.show()
    _ = animation
