from __future__ import annotations

import itertools
import random
import sys

from fighter_class import FIGHTER_CLASSES
from finish_method import FIGHTER_ARCHETYPES
from models import Fighter
from fight import Fight

SIMS_PER_PAIR = 200
NUM_ROUNDS = 3
CLASS_NAME = "Nhà vô địch (Champion)"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

target_class = FIGHTER_CLASSES[CLASS_NAME]
archetype_items = list(FIGHTER_ARCHETYPES.items())

records: dict[str, dict[str, float]] = {
    name: {"wins": 0, "losses": 0, "draws": 0} for name, _ in archetype_items
}

pairings = list(itertools.combinations(archetype_items, 2))

for pair_index, ((name_a, archetype_a), (name_b, archetype_b)) in enumerate(pairings):
    for sim_index in range(SIMS_PER_PAIR):
        seed_value = pair_index * SIMS_PER_PAIR + sim_index
        random.seed(seed_value)

        fighter_a = Fighter(fighter_class=target_class, archetype=archetype_a)
        fighter_b = Fighter(fighter_class=target_class, archetype=archetype_b)

        fight = Fight(fighter_a, fighter_b, num_rounds=NUM_ROUNDS)
        fight.simulate()
        result = fight.result

        if result.score_a > result.score_b:
            records[name_a]["wins"] += 1
            records[name_b]["losses"] += 1
        elif result.score_b > result.score_a:
            records[name_b]["wins"] += 1
            records[name_a]["losses"] += 1
        else:
            records[name_a]["draws"] += 1
            records[name_b]["draws"] += 1

rankings = []

for name, stats in records.items():
    wins = stats["wins"]
    losses = stats["losses"]
    draws = stats["draws"]
    total = wins + losses + draws
    competitive = wins + losses
    win_rate = wins / competitive if competitive else 0.0
    draw_rate = draws / total if total else 0.0
    rankings.append(
        {
            "name": name,
            "wins": int(wins),
            "losses": int(losses),
            "draws": int(draws),
            "total": int(total),
            "win_rate": win_rate,
            "draw_rate": draw_rate,
        }
    )

rankings.sort(key=lambda item: item["win_rate"], reverse=True)

col_width = 30

print(f"Hạng sử dụng: {CLASS_NAME}")
print(f"Số trận mỗi cặp archetype: {SIMS_PER_PAIR}")
print(f"Tổng archetype: {len(archetype_items)}\n")

header = ("Thứ hạng", "Phong cách", "Thắng", "Thua", "Hòa", "Tổng", "Win%", "Draw%")
print(
    f"{header[0]:>8} | {header[1]:>{col_width}} | {header[2]:>6} | {header[3]:>6} | "
    f"{header[4]:>6} | {header[5]:>6} | {header[6]:>7} | {header[7]:>7}"
)
print("-" * (8 + col_width + 6 * 7 + 7 * 3))

for idx, entry in enumerate(rankings, start=1):
    print(
        f"{idx:>8} | "
        f"{entry['name']:>{col_width}} | "
        f"{entry['wins']:>6} | "
        f"{entry['losses']:>6} | "
        f"{entry['draws']:>6} | "
        f"{entry['total']:>6} | "
        f"{entry['win_rate']*100:>6.1f}% | "
        f"{entry['draw_rate']*100:>6.1f}%"
    )
