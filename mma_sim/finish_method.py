import random
from typing import Dict, List

from . import config
from .models import Archetype, FinishInfo

# Tạo một danh sách các đối tượng Archetype từ dữ liệu trong file config
ALL_ARCHETYPES: List[Archetype] = [Archetype(name=name, **data) for name, data in config.FIGHTER_ARCHETYPES_DATA.items()]

# Tạo một dictionary (map) để dễ dàng tra cứu bằng tên, giữ nguyên khả năng tương thích với các file khác.
FIGHTER_ARCHETYPES: Dict[str, Archetype] = {arch.name: arch for arch in ALL_ARCHETYPES}

def _get_specific_finish(archetype: Archetype, method_type: str) -> str:
    """
    Chọn một đòn kết liễu chi tiết.
    Ưu tiên các đòn sở trường của archetype, nếu không có sẽ fallback về danh sách chung.
    """
    # 1. Ưu tiên chọn đòn SUB sở trường
    if method_type == "SUB" and archetype.preferred_submissions:
        subs = archetype.preferred_submissions
        if isinstance(subs, dict):
            # Logic chọn theo độ hiếm (common, uncommon, rare)
            rarity_choices = ["common", "uncommon", "rare"]
            rarity_weights = [75, 20, 5] # Trọng số có thể được cấu hình sau
            
            valid_rarities = [r for r in rarity_choices if subs.get(r)]
            if valid_rarities:
                valid_weights = [rarity_weights[rarity_choices.index(r)] for r in valid_rarities]
                chosen_rarity = random.choices(valid_rarities, weights=valid_weights, k=1)[0]
                return random.choice(subs[chosen_rarity])
        
        elif isinstance(subs, list) and subs:
            return random.choice(subs)

    # 2. Ưu tiên chọn đòn KO sở trường
    if method_type == "KO" and archetype.preferred_kos:
        return random.choice(archetype.preferred_kos)

    # 3. Ưu tiên chọn đòn TKO sở trường
    if method_type == "TKO" and archetype.preferred_tkos:
        return random.choice(archetype.preferred_tkos)

    # 4. Fallback: Nếu không có đòn sở trường hoặc loại kết liễu khác (DEC, DQ...)
    # Lấy từ danh sách chung trong config
    specific_finishes = config.FINISH_METHODS.get(method_type, ["Không xác định"])
    return random.choice(specific_finishes)

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

    # --- Giai đoạn 2: Chọn đòn kết liễu chi tiết dựa trên archetype ---
    specific_finish = _get_specific_finish(archetype, chosen_method_type)

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
