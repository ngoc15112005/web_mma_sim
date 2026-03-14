"""Batch-run simulations to check class balance across many matchups.

Usage examples:
    python scripts/balance_tester.py --runs-per-pair 300 --rounds 3
    python scripts/balance_tester.py --runs-per-pair 500 --rounds 5 --seed 42 --csv-out data/balance.csv
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Tuple

from _bootstrap import add_project_root

add_project_root()

from mma_sim.fighter_class import FIGHTER_CLASSES
from mma_sim.finish_method import FIGHTER_ARCHETYPES
from mma_sim.models import Fighter
from mma_sim.simulation_engine import run_simulation


PairKey = Tuple[str, str]
PairStat = Dict[str, float]


def simulate_pairs(runs_per_pair: int, rounds: int, *, seed: int | None) -> Dict[PairKey, PairStat]:
    if seed is not None:
        random.seed(seed)

    classes = list(FIGHTER_CLASSES.values())
    archetypes = list(FIGHTER_ARCHETYPES.values())

    stats: Dict[PairKey, PairStat] = defaultdict(lambda: defaultdict(float))

    for class_a in classes:
        for class_b in classes:
            if class_a.name == class_b.name:
                continue
            wins_a = wins_b = draws = 0
            score_diffs: list[int] = []
            for _ in range(runs_per_pair):
                arch_a = random.choice(archetypes)
                arch_b = random.choice(archetypes)
                fighter_a = Fighter(class_a, arch_a)
                fighter_b = Fighter(class_b, arch_b)
                result = run_simulation(fighter_a, fighter_b, rounds)

                if result.score_a > result.score_b:
                    wins_a += 1
                elif result.score_b > result.score_a:
                    wins_b += 1
                else:
                    draws += 1
                score_diffs.append(result.score_a - result.score_b)

            total = wins_a + wins_b + draws
            competitive = max(1, wins_a + wins_b)
            stats[(class_a.name, class_b.name)] = {
                "win_a": wins_a / competitive,
                "win_b": wins_b / competitive,
                "draw": draws / total if total else 0.0,
                "avg_diff": sum(score_diffs) / total if total else 0.0,
                "games": total,
            }
    return stats


def to_rows(stats: Dict[PairKey, PairStat]) -> list[dict]:
    rows: list[dict] = []
    for (class_a, class_b), s in stats.items():
        rows.append(
            {
                "class_a": class_a,
                "class_b": class_b,
                "win_rate_a": s["win_a"],
                "win_rate_b": s["win_b"],
                "draw_rate": s["draw"],
                "avg_score_diff": s["avg_diff"],
                "games": s["games"],
                "imbalance": s["win_b"] - s["win_a"],
            }
        )
    rows.sort(key=lambda r: abs(r["imbalance"]), reverse=True)
    return rows


def print_table(rows: Iterable[dict]):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    header = f"{'Class A':<25}{'Class B':<25}{'Win A':>8}{'Win B':>8}{'Draw':>8}{'Δscore':>8}{'Games':>8}"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row['class_a']:<25}{row['class_b']:<25}"
            f"{row['win_rate_a']*100:7.1f}%"
            f"{row['win_rate_b']*100:7.1f}%"
            f"{row['draw_rate']*100:7.1f}%"
            f"{row['avg_score_diff']:7.2f}"
            f"{int(row['games']):8d}"
        )


def write_csv(rows: Iterable[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "class_a",
        "class_b",
        "win_rate_a",
        "win_rate_b",
        "draw_rate",
        "avg_score_diff",
        "games",
        "imbalance",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-per-pair", type=int, default=200, help="Số trận mô phỏng cho mỗi cặp class.")
    parser.add_argument("--rounds", type=int, default=3, help="Số hiệp mỗi trận.")
    parser.add_argument("--seed", type=int, default=None, help="Seed ngẫu nhiên (tùy chọn).")
    parser.add_argument("--csv-out", type=Path, default=None, help="Lưu kết quả ra CSV (tùy chọn).")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    stats = simulate_pairs(args.runs_per_pair, args.rounds, seed=args.seed)
    rows = to_rows(stats)
    print_table(rows)
    if args.csv_out:
        write_csv(rows, args.csv_out)
        print(f"\nĐã lưu CSV vào {args.csv_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
