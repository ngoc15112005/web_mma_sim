import random
import sys

from mma_sim.finish_method import FIGHTER_ARCHETYPES
from mma_sim.fighter_class import FIGHTER_CLASSES
from mma_sim.models import Fighter
from mma_sim.simulation_engine import run_simulation

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def simulate_fight(num_rounds: int):
    """Chạy một trận ngẫu nhiên và in kết quả ra console."""
    class_a_name = random.choice(list(FIGHTER_CLASSES.keys()))
    class_b_name = random.choice(list(FIGHTER_CLASSES.keys()))
    archetype_a = random.choice(list(FIGHTER_ARCHETYPES.values()))
    archetype_b = random.choice(list(FIGHTER_ARCHETYPES.values()))

    fighter_a = Fighter(fighter_class=FIGHTER_CLASSES[class_a_name], archetype=archetype_a)
    fighter_b = Fighter(fighter_class=FIGHTER_CLASSES[class_b_name], archetype=archetype_b)

    result = run_simulation(fighter_a, fighter_b, num_rounds)

    print("\n🎮 MÔ PHỎNG TRẬN ĐẤU MMA")
    print("───────────────────────────────")
    print(f"⚔️  Trận đấu: {class_a_name} (A) vs {class_b_name} (B)")
    print(f"🕒 Số hiệp: {num_rounds}")
    print(f"🎲 Điểm kỹ năng: {result.score_a} vs {result.score_b}")
    print(f"📊 {result.result_description}")
    print(f"💪 Phong cách thi đấu: {result.finish_info.archetype_name} ({result.finish_info.archetype_description})")
    print(f"🏁 Kiểu kết liễu: {result.finish_info.description}")
    print(
        f"⏱️ Thời điểm: Hiệp {result.time_info.round}/{result.time_info.num_rounds} – "
        f"{result.time_info.minute}:{str(result.time_info.second).zfill(2)}"
    )
    print(f"📝 Ghi chú: {result.time_info.note}")
    print("───────────────────────────────\n")


def main():
    while True:
        rounds = input("🔧 Chọn số hiệp (3 hoặc 5): ")
        if rounds in {"3", "5"}:
            simulate_fight(int(rounds))
            break
        print("⚠️  Vui lòng nhập đúng 3 hoặc 5.")


if __name__ == "__main__":
    main()
