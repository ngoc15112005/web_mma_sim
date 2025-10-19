import itertools
import random
import sys

from fighter_class import FIGHTER_CLASSES
from finish_method import FIGHTER_ARCHETYPES
from models import Fighter
from fight import Fight

SIMS_PER_ARCHETYPE = 200
NUM_ROUNDS = 3

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

class_pairs = list(itertools.combinations(list(FIGHTER_CLASSES.items()), 2))
archetypes = list(FIGHTER_ARCHETYPES.items())

results = []

seed_base = 1337
seed_step = SIMS_PER_ARCHETYPE * len(archetypes)

for pair_index, ((class_a_name, class_a), (class_b_name, class_b)) in enumerate(class_pairs):
    wins_a = 0
    wins_b = 0
    draws = 0

    for arch_index, (arch_name, archetype) in enumerate(archetypes):
        for sim_index in range(SIMS_PER_ARCHETYPE):
            seed_value = seed_base + pair_index * seed_step + arch_index * SIMS_PER_ARCHETYPE + sim_index
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
    competitive_total = wins_a + wins_b

    win_rate_a = wins_a / competitive_total if competitive_total else 0.0
    win_rate_b = wins_b / competitive_total if competitive_total else 0.0
    draw_rate = draws / total if total else 0.0
    diff = win_rate_b - win_rate_a  # positive means class B advantage

    results.append(
        {
            "pair": f"{class_a_name} vs {class_b_name}",
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

for entry in results:
    print(
        f"{entry['pair']}: "
        f"A win {entry['win_rate_a']*100:5.1f}% | "
        f"B win {entry['win_rate_b']*100:5.1f}% | "
        f"draw {entry['draw_rate']*100:4.1f}% | "
        f"diff (B-A) {entry['diff']*100:5.1f} pts"
    )
