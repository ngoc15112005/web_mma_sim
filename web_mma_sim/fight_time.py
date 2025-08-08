import random
from models import TimeInfo
import config

def generate_dynamic_fight_time(method_type, num_rounds, archetype_name=None, score_diff=None) -> TimeInfo:
    """
    Tạo ra thời điểm kết thúc trận đấu một cách "động",
    dựa trên kiểu kết liễu, phong cách và mức độ chênh lệch.
    """
    # Các trận đấu hết giờ sẽ luôn kết thúc ở 5:00 của hiệp cuối.
    if method_type in ["DEC", "DRAW"]:
        return TimeInfo(
            num_rounds=num_rounds,
            round=num_rounds,
            minute=5,
            second=0,
            note="Kết thúc bằng điểm số sau hiệp cuối cùng"
        )

    # --- Logic xác định hiệp kết thúc ---
    # Bắt đầu với trọng số cơ bản cho mỗi hiệp
    round_weights = [10.0] * num_rounds

    # 1. Điều chỉnh trọng số dựa trên Phong cách (Archetype) từ config
    if archetype_name and archetype_name in config.TIME_ARCHETYPE_MODIFIERS:
        modifiers = config.TIME_ARCHETYPE_MODIFIERS[archetype_name]
        if "round_1_multiplier" in modifiers:
            round_weights[0] *= modifiers["round_1_multiplier"]
        if "other_rounds_multiplier" in modifiers and num_rounds > 1:
            for i in range(1, num_rounds):
                round_weights[i] *= modifiers["other_rounds_multiplier"]
        if "final_round_multiplier" in modifiers and num_rounds > 1:
            # Sửa lỗi: Áp dụng hệ số cho hiệp cuối cùng
            round_weights[-1] *= modifiers["final_round_multiplier"]

    # 2. Điều chỉnh trọng số dựa trên Mức độ chênh lệch (Score Diff)
    if score_diff is not None:
        # Sử dụng hằng số từ config.py để code dễ đọc và dễ cân bằng hơn
        if score_diff >= config.TIME_SCORE_DIFF_OUTCLASS_THRESHOLD: # Out trình
            for round_num, multiplier in config.TIME_OUTCLASS_ROUND_MULTIPLIERS.items():
                # Đảm bảo không truy cập index ngoài phạm vi
                if round_num - 1 < len(round_weights):
                    round_weights[round_num - 1] *= multiplier
        elif score_diff <= config.TIME_SCORE_DIFF_CLOSE_THRESHOLD: # Cân bằng hoặc nghẹt thở
            if num_rounds > 1:
                # Tăng nhẹ khả năng kéo dài đến hiệp cuối
                round_weights[-1] *= config.TIME_CLOSE_ROUND_MULTIPLIER

    # Chọn hiệp kết thúc dựa trên trọng số đã điều chỉnh
    possible_rounds = list(range(1, num_rounds + 1))
    round_end = random.choices(possible_rounds, weights=round_weights, k=1)[0]

    minute = random.randint(0, 4)
    second = random.randint(0, 59)

    return TimeInfo(
        num_rounds=num_rounds,
        round=round_end,
        minute=minute,
        second=second,
        note=f"Kết thúc bằng {method_type} tại hiệp {round_end}, phút {minute}:{str(second).zfill(2)}"
    )