import random
from collections import defaultdict

from fighter_class import FIGHTER_CLASSES
from finish_method import FIGHTER_ARCHETYPES
from models import Fighter
from simulation_engine import run_simulation


def archetype_win_rates(class_name: str = "Nhà vô địch (Champion)", runs: int = 2000, rounds: int = 5):
    archetypes = list(FIGHTER_ARCHETYPES.keys())
    wins = defaultdict(int)
    losses = defaultdict(int)
    random.seed(42)

    for _ in range(runs):
        a_name, b_name = random.sample(archetypes, 2)
        fighter_a = Fighter(
            fighter_class=FIGHTER_CLASSES[class_name],
            archetype=FIGHTER_ARCHETYPES[a_name],
        )
        fighter_b = Fighter(
            fighter_class=FIGHTER_CLASSES[class_name],
            archetype=FIGHTER_ARCHETYPES[b_name],
        )
        result = run_simulation(fighter_a, fighter_b, rounds)
        if result.score_a > result.score_b:
            wins[a_name] += 1
            losses[b_name] += 1
        elif result.score_b > result.score_a:
            wins[b_name] += 1
            losses[a_name] += 1

    records = []
    for name in archetypes:
        total = wins[name] + losses[name]
        if total:
            records.append((name, wins[name], losses[name], wins[name] / total))

    records.sort(key=lambda x: x[3])
    print("Bottom 5 archetypes by win rate:")
    for name, w, l, rate in records[:5]:
        print(f"{name:35} {w:4d}-{l:4d} win={rate:.2f}")

    records.sort(key=lambda x: x[3], reverse=True)
    print("\nTop 5 archetypes by win rate:")
    for name, w, l, rate in records[:5]:
        print(f"{name:35} {w:4d}-{l:4d} win={rate:.2f}")


if __name__ == "__main__":
    archetype_win_rates(runs=10000)
