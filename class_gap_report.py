"""Báo cáo tỷ lệ thắng giữa các đẳng cấp võ sĩ.

Script mô phỏng mọi cặp đẳng cấp với cùng phong cách (archetype) để kiểm tra
độ chênh lệch sau mỗi lần tinh chỉnh cân bằng. Có thể chọn ngôn ngữ đầu ra để
phục vụ việc báo cáo.

Ví dụ chạy:

    python class_gap_report.py --runs 200 --rounds 3 --seed 321 --language vi

"""

from __future__ import annotations

import argparse
import random
from collections import defaultdict
from typing import Dict, Iterable, Tuple

from fighter_class import FIGHTER_CLASSES
from finish_method import FIGHTER_ARCHETYPES
from models import Fighter
from simulation_engine import run_simulation


ResultKey = Tuple[str, str]
ResultValue = Tuple[int, int, int]


LANGUAGE_PACKS = {
    "vi": {
        "class_a": "Đẳng cấp A",
        "class_b": "Đẳng cấp B",
        "win_a": "Thắng A",
        "win_b": "Thắng B",
        "draw": "Hòa",
        "total": "Tổng",
    },
    "en": {
        "class_a": "Class A",
        "class_b": "Class B",
        "win_a": "Win A",
        "win_b": "Win B",
        "draw": "Draw",
        "total": "Total",
    },
}


def simulate_pairings(
    runs_per_archetype: int,
    rounds: int,
    *,
    seed: int | None,
) -> Dict[ResultKey, ResultValue]:
    """Run the requested number of simulations for every class pairing."""

    if seed is not None:
        random.seed(seed)

    classes = list(FIGHTER_CLASSES.values())
    archetypes = list(FIGHTER_ARCHETYPES.values())

    stats: Dict[ResultKey, ResultValue] = defaultdict(lambda: (0, 0, 0))

    for class_a in classes:
        for class_b in classes:
            wins_a = wins_b = draws = 0
            for archetype in archetypes:
                for _ in range(runs_per_archetype):
                    fighter_a = Fighter(class_a, archetype)
                    fighter_b = Fighter(class_b, archetype)
                    result = run_simulation(fighter_a, fighter_b, rounds)

                    if result.score_a > result.score_b:
                        wins_a += 1
                    elif result.score_b > result.score_a:
                        wins_b += 1
                    else:
                        draws += 1

            stats[(class_a.name, class_b.name)] = (wins_a, wins_b, draws)

    return stats


def format_table(stats: Dict[ResultKey, ResultValue], language: str) -> str:
    """Render the aggregated pairing statistics into a text table."""

    labels = LANGUAGE_PACKS[language]
    class_names = sorted({name for pair in stats for name in pair})

    name_width = max(
        max(len(name) for name in class_names),
        len(labels["class_a"]),
        len(labels["class_b"]),
    ) + 2
    percent_width = max(
        len("100.00%"),
        len(labels["win_a"]),
        len(labels["win_b"]),
        len(labels["draw"]),
    ) + 2
    max_total = max((sum(stats[pair]) for pair in stats), default=0)
    total_width = max(len(str(max_total)), len(labels["total"])) + 2

    header = (
        f"{labels['class_a']:<{name_width}}{labels['class_b']:<{name_width}}"
        f"{labels['win_a']:>{percent_width}}{labels['win_b']:>{percent_width}}"
        f"{labels['draw']:>{percent_width}}{labels['total']:>{total_width}}"
    )
    lines = [header, "-" * len(header)]

    for class_a in class_names:
        for class_b in class_names:
            wins_a, wins_b, draws = stats[(class_a, class_b)]
            total = wins_a + wins_b + draws
            if total == 0:
                win_rate_a = win_rate_b = draw_rate = 0.0
            else:
                win_rate_a = wins_a / total
                win_rate_b = wins_b / total
                draw_rate = draws / total

            win_a_str = f"{win_rate_a:.2%}"
            win_b_str = f"{win_rate_b:.2%}"
            draw_str = f"{draw_rate:.2%}"

            lines.append(
                f"{class_a:<{name_width}}{class_b:<{name_width}}"
                f"{win_a_str:>{percent_width}}{win_b_str:>{percent_width}}"
                f"{draw_str:>{percent_width}}{total:>{total_width}}"
            )

    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs",
        type=int,
        default=200,
        help="Số trận mô phỏng cho mỗi phong cách trong từng cặp đẳng cấp.",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=3,
        help="Số hiệp mỗi trận mô phỏng.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=321,
        help="Seed ngẫu nhiên để tái lập kết quả.",
    )
    parser.add_argument(
        "--language",
        "-l",
        choices=sorted(LANGUAGE_PACKS.keys()),
        default="vi",
        help="Ngôn ngữ hiển thị bảng (vi hoặc en).",
    )

    args = parser.parse_args(argv)

    stats = simulate_pairings(
        runs_per_archetype=args.runs, rounds=args.rounds, seed=args.seed
    )
    print(format_table(stats, language=args.language))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
