import random
from typing import List, Dict

from models import Archetype, FinishInfo
import config

# Tạo một danh sách các đối tượng Archetype từ dữ liệu trong file config
ALL_ARCHETYPES: List[Archetype] = [Archetype(name=name, **data) for name, data in config.FIGHTER_ARCHETYPES_DATA.items()]

# Tạo một dictionary (map) để dễ dàng tra cứu bằng tên, giữ nguyên khả năng tương thích với các file khác.
FIGHTER_ARCHETYPES: Dict[str, Archetype] = {arch.name: arch for arch in ALL_ARCHETYPES}

def get_dynamic_finish_method(archetype_name=None, score_diff=None) -> FinishInfo:
    # Nếu không có phong cách nào được chỉ định hoặc tên không hợp lệ, chọn ngẫu nhiên.
    if archetype_name is None or archetype_name not in FIGHTER_ARCHETYPES:
        archetype_name = random.choice(list(FIGHTER_ARCHETYPES.keys()))

    # `archetype` bây giờ là một đối tượng Archetype, không phải là dictionary
    archetype = FIGHTER_ARCHETYPES[archetype_name]

    # Lấy trọng số cơ bản từ phong cách (đã được dọn dẹp)
    base_weights = archetype.weights.copy()

    # --- Bước 1.3: Thêm Logic "Động" điều chỉnh trọng số ---
    if score_diff is not None:
        # Sử dụng hằng số từ config.py
        if score_diff >= config.FINISH_SCORE_DIFF_OUTCLASS_THRESHOLD: # Out trình
            for method, multiplier in config.FINISH_OUTCLASS_MULTIPLIERS.items():
                base_weights[method] = base_weights.get(method, 0) * multiplier
        elif score_diff <= config.FINISH_SCORE_DIFF_CLOSE_THRESHOLD: # Thắng nghẹt thở
            for method, multiplier in config.FINISH_CLOSE_MULTIPLIERS.items():
                base_weights[method] = base_weights.get(method, 0) * multiplier

    # --- Bước 1.4: Hoàn thiện và tích hợp lại các kết quả tình huống ---
    final_weights = base_weights
    final_weights.update(config.FINISH_STATIC_WEIGHTS)

    method_types = list(final_weights.keys())
    weights = list(final_weights.values())

    # Đảm bảo không có lỗi nếu tất cả trọng số bằng 0 (ví dụ: One-Round Monster chỉ có DEC=0)
    if not any(w > 0 for w in weights):
        # Fallback: nếu không có trọng số, chọn ngẫu nhiên từ các loại có thể
        chosen_method_type = random.choice(method_types)
    else:
        # Đảm bảo không có trọng số âm hoặc bằng không để tránh lỗi
        positive_weights = [max(0.01, w) for w in weights]
        chosen_method_type = random.choices(method_types, weights=positive_weights, k=1)[0]

    # Chọn một diễn giải chi tiết từ loại kết liễu
    specific_finishes = config.FINISH_METHODS[chosen_method_type]
    specific_finish = random.choice(specific_finishes)

    # Tạo mô tả đầy đủ
    # Đối với DEC, mô tả đã đủ chi tiết
    full_description = specific_finish if chosen_method_type in ["DEC", "DQ", "NC", "DRAW"] else f"{chosen_method_type} – {specific_finish}"

    # Trả về một đối tượng FinishInfo có cấu trúc
    return FinishInfo(
        archetype_name=archetype.name, # Truy cập thuộc tính .name
        archetype_description=archetype.description, # Truy cập thuộc tính .description
        description=full_description,
        method_type=chosen_method_type
    )
