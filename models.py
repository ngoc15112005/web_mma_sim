import random
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class FighterClass:
    """Đại diện cho một hạng đấu và mô tả thang kỹ năng cơ bản."""

    name: str
    description: str
    skill_range: Tuple[int, int]


@dataclass
class Archetype:
    """Mô tả phong cách thi đấu của võ sĩ."""

    name: str
    description: str
    weights: Dict[str, int]
    preferred_kos: Optional[List[str]] = None
    preferred_tkos: Optional[List[str]] = None
    preferred_submissions: Optional[List[str] | Dict[str, List[str]]] = None


@dataclass
class Fighter:
    """Đối tượng võ sĩ được sử dụng trong mô phỏng."""

    fighter_class: FighterClass
    archetype: Archetype

    def generate_skill_point(self) -> int:
        min_skill, max_skill = self.fighter_class.skill_range
        return random.randint(min_skill, max_skill)


@dataclass
class TimeInfo:
    """Thời điểm kết thúc trận đấu."""

    num_rounds: int
    round: int
    minute: int
    second: int
    note: str


@dataclass
class FinishInfo:
    """Thông tin về kiểu kết thúc trận đấu."""

    archetype_name: str
    archetype_description: str
    description: str
    method_type: str


@dataclass
class RoundSummary:
    """Tóm tắt điểm số và ghi chú của từng hiệp."""

    round_number: int
    score_a: int
    score_b: int
    note: str = ""
    events: List[str] = field(default_factory=list)


@dataclass
class TickEvent:
    """Chi tiết một pha giao tranh trong hiệp (dùng cho log nâng cao)."""

    round_number: int
    tick_index: int
    phase: str
    actor: Optional[str]
    description: str
    impact: float


@dataclass
class FighterAttributes:
    """Các chỉ số chi tiết dùng cho mô phỏng theo pha."""

    striking: int
    clinch: int
    grappling: int
    submission: int
    cardio: int
    durability: int
    fight_iq: int


@dataclass
class FightResult:
    """Kết quả cuối cùng của trận đấu."""

    score_a: int
    score_b: int
    result_description: str
    finish_info: FinishInfo
    time_info: TimeInfo
    round_summaries: List[RoundSummary] = field(default_factory=list)


@dataclass
class HistoryEntry:
    """Bản ghi lịch sử của một lần mô phỏng."""

    fight_result: FightResult
    class_a_name: str
    class_b_name: str
    archetype_a_name: str
    archetype_b_name: str
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))