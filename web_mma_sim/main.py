import random
from fighter_class import FIGHTER_CLASSES
from finish_method import FIGHTER_ARCHETYPES
from models import Fighter
from fight import Fight

def simulate_fight(num_rounds: int):
    # Tự động chọn ngẫu nhiên đẳng cấp cho hai võ sĩ
    class_a_name = random.choice(list(FIGHTER_CLASSES.keys()))
    class_b_name = random.choice(list(FIGHTER_CLASSES.keys()))

    # Chọn ngẫu nhiên một archetype cho mỗi võ sĩ
    archetype_a = random.choice(list(FIGHTER_ARCHETYPES.values()))
    archetype_b = random.choice(list(FIGHTER_ARCHETYPES.values()))

    # 1. Tạo các đối tượng Fighter
    fighter_a = Fighter(fighter_class=FIGHTER_CLASSES[class_a_name], archetype=archetype_a)
    fighter_b = Fighter(fighter_class=FIGHTER_CLASSES[class_b_name], archetype=archetype_b)

    # 2. Tạo và chạy mô phỏng thông qua đối tượng Fight
    fight = Fight(fighter_a, fighter_b, num_rounds)
    fight.simulate()
    result = fight.result

    # Truy cập thông tin từ đối tượng FightResult bằng thuộc tính (ví dụ: result.score_a)
    print("\n🎮 MÔ PHỎNG TRẬN ĐẤU MMA")
    print("═══════════════════════════")
    print(f"⚔️  Trận đấu: {class_a_name} (A) vs {class_b_name} (B)")
    print(f"🕒 Số hiệp: {num_rounds}")
    print(f"🎲 Điểm kỹ năng: {result.score_a} vs {result.score_b}")
    print(f"📊 {result.result_description}")
    print(f"💪 Phong cách thi đấu: {result.finish_info.archetype_name} ({result.finish_info.archetype_description})")
    print(f"🏁 Kiểu kết liễu: {result.finish_info.description}")
    print(f"⏱️ Thời điểm: Hiệp {result.time_info.round}/{result.time_info.num_rounds} – {result.time_info.minute}:{str(result.time_info.second).zfill(2)}")
    print(f"📝 Ghi chú: {result.time_info.note}")
    print("═══════════════════════════\n")

if __name__ == "__main__":
    while True:
        rounds = input("🔢 Chọn số hiệp (3 hoặc 5): ")
        if rounds in ['3', '5']:
            simulate_fight(int(rounds))
            break
        else:
            print("⚠️ Vui lòng nhập đúng 3 hoặc 5.")