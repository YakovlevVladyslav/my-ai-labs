"""Reproducible headless experiments, CSV results and Matplotlib plots."""
import argparse
import csv
from dataclasses import replace
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Save figures without opening animation windows.
import matplotlib.pyplot as plt
import numpy as np

from config import Config
from metrics import measure
from simulation import Simulation

# One parameter at a time relative to the baseline; equal random seed and steps.
CASES = [
    ('baseline', {}),
    ('resources_fast_consumption', {'consumption_per_animal': 3.0}),
    ('resources_slow_regeneration', {'regeneration_wet': 0.2, 'regeneration_dry': 0.02}),
    ('predators_none', {'predator_count': 0}),
    ('predators_three', {'predator_count': 3}),
    ('predators_fast', {'predator_speed': 1.8}),
    ('resources_short_detection', {'resource_detection_radius': 20.0}),
    ('threats_long_detection', {'predator_detection_radius': 30.0}),
]

METRICS = {
    'polarization': 'Heading alignment (0 to 1)',
    'mean_nearest_distance': 'Mean nearest-neighbor distance',
    'threatened_fraction': 'Fraction of animals near predators',
    'animals_at_resources': 'Animals inside resource zones',
    'mean_resource_fraction': 'Mean remaining resource fraction',
}


def csv_write(path, rows):
    if not rows:
        return
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_case(name, changes, baseline, out):
    cfg = replace(baseline, **changes)
    sim = Simulation(cfg)
    history = []
    for _ in range(cfg.steps):
        sim.step()
        history.append(measure(sim))
    for row in history:
        row['experiment'] = name
    csv_write(out / f'{name}_steps.csv', history)
    # Average over whole simulation; no cherry-picked end frame.
    result = {'experiment': name, 'changes': '; '.join(f'{k}={v}' for k, v in changes.items()) or 'baseline',
              'seed': cfg.seed, 'steps': cfg.steps}
    for metric in METRICS:
        result[metric] = float(np.mean([row[metric] for row in history]))
    result['min_predator_distance'] = float(np.min([r['min_predator_distance'] for r in history])) if cfg.predator_count else float('nan')
    return result, history


def draw_chart(histories, key, label, path):
    fig, ax = plt.subplots(figsize=(10, 5))
    for name, data in histories.items():
        ax.plot([r['step'] for r in data], [r[key] for r in data], label=name, linewidth=1.2)
    ax.set(xlabel='Simulation step', ylabel=label, title=label)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, loc='best')
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description='Run Boids experiments and export results.')
    parser.add_argument('--output', default='results', help='Output directory')
    parser.add_argument('--steps', type=int, default=600)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    if args.steps <= 0:
        parser.error('--steps must be positive')
    baseline = Config(steps=args.steps, seed=args.seed)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    summaries, histories = [], {}
    for name, changes in CASES:
        summary, history = run_case(name, changes, baseline, out)
        summaries.append(summary)
        histories[name] = history
        print(f'{name}: polarization={summary["polarization"]:.3f}; '
              f'threatened={summary["threatened_fraction"]:.3f}; '
              f'resources={summary["mean_resource_fraction"]:.3f}')
    csv_write(out / 'summary.csv', summaries)
    for key, label in METRICS.items():
        draw_chart(histories, key, label, out / f'{key}.png')
    print(f'\nSaved {len(CASES)} runs, summary and {len(METRICS)} plots to {out.resolve()}')


if __name__ == '__main__':
    main()
