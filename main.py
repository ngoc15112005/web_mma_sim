import random
from fighter_class import FIGHTER_CLASSES, generate_skill_point
from simulation_engine import run_simulation

def simulate_fight(num_rounds):
    # Tự động chọn ngẫu nhiên đẳng cấp cho hai võ sĩ
    class_a_name = random.choice(list(FIGHTER_CLASSES.keys()))
    class_b_name = random.choice(list(FIGHTER_CLASSES.keys()))

    # Gọi Lõi mô phỏng. Ở đây ta không chọn archetype, để Lõi tự chọn ngẫu nhiên.
    result = run_simulation(num_rounds, class_a_name, class_b_name, "Ngẫu nhiên")

    # Lấy thông tin từ kết quả trả về để hiển thị
    finish = result["finish_info"]
    time_info = result["time_info"]
    
    print("\n🎮 MÔ PHỎNG TRẬN ĐẤU MMA")
    print("═══════════════════════════")
    print(f"⚔️  Trận đấu: {class_a_name} (A) vs {class_b_name} (B)")
    print(f"🕒 Số hiệp: {num_rounds}")
    print(f"🎲 Điểm kỹ năng: {result['score_a']} vs {result['score_b']}")
    print(f"📊 {result['result_description']}")
    print(f"💪 Phong cách thi đấu: {finish['archetype_name']} ({finish['archetype_description']})")
    print(f"🏁 Kiểu kết liễu: {finish['description']}")
    print(f"⏱️ Thời điểm: Hiệp {time_info['round']}/{time_info['num_rounds']} – {time_info['minute']}:{str(time_info['second']).zfill(2)}")
    print(f"📝 Ghi chú: {time_info['note']}")
    print("═══════════════════════════\n")

if __name__ == "__main__":
    while True:
        rounds = input("🔢 Chọn số hiệp (3 hoặc 5): ")
        if rounds in ['3', '5']:
            simulate_fight(int(rounds))
            break
        else:
            print("⚠️ Vui lòng nhập đúng 3 hoặc 5.")