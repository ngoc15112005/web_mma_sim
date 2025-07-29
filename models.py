import random
from dataclasses import dataclass
from typing import Tuple, Dict, Optional

@dataclass
class FighterClass:
    """Đại diện cho một đẳng cấp võ sĩ."""
    name: str
    description: str
    skill_range: Tuple[int, int]

@dataclass
class Archetype:
    """Đại diện cho một phong cách thi đấu."""
    name: str
    description: str
    weights: Dict[str, int]

@dataclass
class Fighter:
    """
    Đại diện cho một võ sĩ cụ thể trong một trận đấu.
    Lớp này đóng gói đẳng cấp và các hành vi liên quan.
    """
    fighter_class: FighterClass
    archetype: Archetype

    def generate_skill_point(self) -> int:
        """Tạo điểm kỹ năng dựa trên đẳng cấp của chính võ sĩ này."""
        min_skill, max_skill = self.fighter_class.skill_range
        return random.randint(min_skill, max_skill)


@dataclass
class TimeInfo:
    """Lưu trữ thông tin về thời điểm kết thúc trận đấu."""
    num_rounds: int
    round: int
    minute: int
    second: int
    note: str

@dataclass
class FinishInfo:
    """Lưu trữ thông tin về kiểu kết liễu."""
    archetype_name: str
    archetype_description: str
    description: str
    method_type: str

@dataclass
class FightResult:
    """Đối tượng kết quả cuối cùng, chứa tất cả thông tin của một trận đấu."""
    score_a: int
    score_b: int
    result_description: str
    finish_info: 'FinishInfo'
    time_info: 'TimeInfo'