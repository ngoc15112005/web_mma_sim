from __future__ import annotations

import random

from fighter_class import FIGHTER_CLASSES
from finish_method import FIGHTER_ARCHETYPES
from models import Fighter
from fight import Fight

SIMS_PER_PAIR = 2000
NUM_ROUNDS = 3
TARGET_ARCHETYPES = [
    "Balanced Finisher / MMA Generalist",
    "Durable Grinder",
    "Technical Boxer",
]


def run_matrix(archetype_name: str) -> list[dict[str, object]]:
    archetype = FIGHTER_ARCHETYPES[archetype_name]
    classes = list(FIGHTER_CLASSES.items())
    random_seed = 20301 + hash(archetype_name) % 10_000
    rng = random.Random(random_seed)
    results: list[dict[str, object]] = []

    for i, (class_a_name, class_a) in enumerate(classes):
        for j, (class_b_name, class_b) in enumerate(classes[i:], start=i):
            wins_a = wins_b = draws = 0
            for sim in range(SIMS_PER_PAIR):
                seed = rng.randint(0, 10_000_000)
                random.seed(seed)
                fighter_a = Fighter(class_a, archetype)
                fighter_b = Fighter(class_b, archetype)
                fight = Fight(fighter_a, fighter_b, NUM_ROUNDS)
                fight.simulate()
                result = fight.result
                if result.score_a > result.score_b:
                    wins_a += 1
                elif result.score_b > result.score_a:
                    wins_b += 1
                else:
                    draws += 1

            total = wins_a + wins_b + draws
            competitive = wins_a + wins_b or 1
            results.append(
                {
                    "class_a": class_a_name,
                    "class_b": class_b_name,
                    "wins_a": wins_a,
                    "wins_b": wins_b,
                    "draws": draws,
                    "total": total,
                    "win_rate_a": wins_a / competitive,
                    "win_rate_b": wins_b / competitive,
                    "draw_rate": draws / total if total else 0.0,
                }
            )
    return results


def print_matrix(archetype_name: str, rows: list[dict[str, object]]):
    col_width = 18
    print(f"\n=== Phong cách: {archetype_name} ===")
    header = (
        "Class A",
        "Class B",
        "Wins A",
        "Wins B",
        "Draws",
        "Total",
        "Win% A",
        "Win% B",
        "Draw%",
        "Diff (B-A)",
    )
    print(" | ".join(f"{title:>{col_width}}" for title in header))
    print("-" * ((col_width + 3) * len(header)))
    for entry in rows:
        diff = entry["win_rate_b"] - entry["win_rate_a"]
        print(
            f"{entry['class_a']:>{col_width}} | "
            f"{entry['class_b']:>{col_width}} | "
            f"{entry['wins_a']:>{col_width}d} | "
            f"{entry['wins_b']:>{col_width}d} | "
            f"{entry['draws']:>{col_width}d} | "
            f"{entry['total']:>{col_width}d} | "
            f"{entry['win_rate_a']*100:>{col_width - 1}.1f}% | "
            f"{entry['win_rate_b']*100:>{col_width - 1}.1f}% | "
            f"{entry['draw_rate']*100:>{col_width - 1}.1f}% | "
            f"{diff*100:>{col_width - 1}.1f}%"
        )


def main():
    for archetype_name in TARGET_ARCHETYPES:
        rows = run_matrix(archetype_name)
        print_matrix(archetype_name, rows)


if __name__ == "__main__":
    main()
