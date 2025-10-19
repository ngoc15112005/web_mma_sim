from __future__ import annotations

import itertools
import random
import sys

from fighter_class import FIGHTER_CLASSES
from finish_method import FIGHTER_ARCHETYPES
from models import Fighter
from fight import Fight

SIMS_PER_PAIR = 2000
NUM_ROUNDS = 3
ARCHETYPE_NAME = "Balanced Finisher / MMA Generalist"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

archetype = FIGHTER_ARCHETYPES[ARCHETYPE_NAME]
pairs = list(itertools.combinations_with_replacement(list(FIGHTER_CLASSES.items()), 2))

rows: list[dict[str, object]] = []

for pair_index, ((name_a, class_a), (name_b, class_b)) in enumerate(pairs):
    wins_a = wins_b = draws = 0

    for sim_index in range(SIMS_PER_PAIR):
        seed_value = pair_index * SIMS_PER_PAIR + sim_index
        random.seed(seed_value)

        fighter_a = Fighter(fighter_class=class_a, archetype=archetype)
        fighter_b = Fighter(fighter_class=class_b, archetype=archetype)

        fight = Fight(fighter_a, fighter_b, num_rounds=NUM_ROUNDS)
        fight.simulate()
        result = fight.result

        if result.score_a > result.score_b:
            wins_a += 1
        elif result.score_b > result.score_a:
            wins_b += 1
        else:
            draws += 1

    total = wins_a + wins_b + draws
    competitive = wins_a + wins_b
    win_rate_a = wins_a / competitive if competitive else 0.0
    win_rate_b = wins_b / competitive if competitive else 0.0
    draw_rate = draws / total if total else 0.0
    diff = win_rate_b - win_rate_a

    rows.append(
        {
            "class_a": name_a,
            "class_b": name_b,
            "wins_a": wins_a,
            "wins_b": wins_b,
            "draws": draws,
            "total": total,
            "win_rate_a": win_rate_a,
            "win_rate_b": win_rate_b,
            "draw_rate": draw_rate,
            "diff": diff,
        }
    )

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

col_width = 18

print(f"Archetype: {ARCHETYPE_NAME}")
print(" | ".join(f"{title:>{col_width}}" for title in header))
print("-" * ((col_width + 3) * len(header)))

for entry in rows:
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
        f"{entry['diff']*100:>{col_width - 1}.1f}%"
    )
