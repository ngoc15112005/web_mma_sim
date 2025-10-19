from __future__ import annotations

import random
from typing import Dict, Tuple

from fight import Fight
from fighter_class import FIGHTER_CLASSES
from finish_method import FIGHTER_ARCHETYPES
from models import Fighter

CLASS_NAME = "Nhà vô địch (Champion)"
NUM_ROUNDS = 3
SIMS_PER_ARCHETYPE = 400
RANDOM_SEED = 20260


def main():
    rng = random.Random(RANDOM_SEED)
    fighter_class = FIGHTER_CLASSES[CLASS_NAME]

    print(f"Hạng kiểm tra: {CLASS_NAME}")
    print(f"Số trận mỗi phong cách: {SIMS_PER_ARCHETYPE}")
    print(f"Rounds mỗi trận: {NUM_ROUNDS}\n")

    for name, archetype in FIGHTER_ARCHETYPES.items():
        counts: Dict[str, int] = {
            "DEC": 0,
            "KO": 0,
            "TKO": 0,
            "SUB": 0,
            "DRAW": 0,
            "OTHER": 0,
        }

        for _ in range(SIMS_PER_ARCHETYPE):
            rng.seed(rng.randint(0, 10_000_000))
            fighter_a = Fighter(fighter_class=fighter_class, archetype=archetype)
            fighter_b = Fighter(fighter_class=fighter_class, archetype=archetype)
            fight = Fight(fighter_a, fighter_b, NUM_ROUNDS)
            fight.simulate()

            method = fight.result.finish_info.method_type
            if method in counts:
                counts[method] += 1
            else:
                counts["OTHER"] += 1

        total = sum(counts.values())
        print(f"{name}:")
        for key in ["DEC", "KO", "TKO", "SUB", "DRAW", "OTHER"]:
            count = counts[key]
            pct = count / total * 100 if total else 0.0
            print(f"  {key:>4}: {count:4d} ({pct:5.1f}%)")
        print()


if __name__ == "__main__":
    main()
