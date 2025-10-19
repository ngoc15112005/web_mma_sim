from __future__ import annotations

import random
import sys
from collections import Counter
from typing import Tuple

from fighter_class import FIGHTER_CLASSES
from finish_method import FIGHTER_ARCHETYPES
from models import Fighter
from fight import Fight

NUM_SCENARIOS = 3
SIMULATIONS_PER_SCENARIO = 500
NUM_ROUNDS = 3
RANDOM_SEED = 202511

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def pick_scenarios(num: int) -> list[Tuple[str, str, str, str]]:
    class_names = list(FIGHTER_CLASSES.keys())
    archetype_names = list(FIGHTER_ARCHETYPES.keys())
    scenarios = []
    picked = set()
    rng = random.Random(RANDOM_SEED)

    while len(scenarios) < num:
        class_a = rng.choice(class_names)
        class_b = rng.choice(class_names)
        archetype_a = rng.choice(archetype_names)
        archetype_b = rng.choice(archetype_names)
        key = (class_a, archetype_a, class_b, archetype_b)
        if key not in picked:
            picked.add(key)
            scenarios.append(key)
    return scenarios


def categorise_finish(method_type: str) -> str:
    if method_type in {"KO", "TKO"}:
        return "KO/TKO"
    if method_type == "SUB":
        return "SUB"
    if method_type == "DEC":
        return "Điểm"
    if method_type == "DRAW":
        return "Hòa"
    return "Khác"


def run_scenario(scenario: Tuple[str, str, str, str], sims: int, seed_offset: int) -> Counter:
    class_a_name, archetype_a_name, class_b_name, archetype_b_name = scenario
    counter: Counter = Counter()
    rng = random.Random(RANDOM_SEED + seed_offset)

    for _ in range(sims):
        fighter_a = Fighter(
            fighter_class=FIGHTER_CLASSES[class_a_name],
            archetype=FIGHTER_ARCHETYPES[archetype_a_name],
        )
        fighter_b = Fighter(
            fighter_class=FIGHTER_CLASSES[class_b_name],
            archetype=FIGHTER_ARCHETYPES[archetype_b_name],
        )

        random.seed(rng.randint(0, 10_000_000))
        fight = Fight(fighter_a, fighter_b, num_rounds=NUM_ROUNDS)
        fight.simulate()

        method = fight.result.finish_info.method_type
        counter[categorise_finish(method)] += 1

    counter["Tổng"] = sims
    return counter


def format_percentage(value: int, total: int) -> float:
    return (value / total * 100) if total else 0.0


def main():
    scenarios = pick_scenarios(NUM_SCENARIOS)

    for index, scenario in enumerate(scenarios, start=1):
        class_a, arch_a, class_b, arch_b = scenario
        counts = run_scenario(scenario, SIMULATIONS_PER_SCENARIO, seed_offset=index)
        total = counts["Tổng"]

        print(f"Scenario {index}:")
        print(f"  Võ sĩ A: {class_a} / {arch_a}")
        print(f"  Võ sĩ B: {class_b} / {arch_b}")
        print(f"  Số trận: {total}")

        for key in ["Điểm", "SUB", "KO/TKO", "Hòa", "Khác"]:
            count = counts.get(key, 0)
            print(f"    {key:7s}: {count:4d} ({format_percentage(count, total):5.1f}%)")
        print()


if __name__ == "__main__":
    main()
