import random
from typing import List, Dict
from models import FighterClass

# Define base data for all fighter classes in the simulation
_ALL_FIGHTER_CLASSES: List[FighterClass] = [
    FighterClass(
        name="Tân binh (Rookie)",
        skill_range=(5, 40),
        description="Võ sĩ mới vào nghề, còn non kinh nghiệm nhưng đầy tiềm năng."
    ),
    FighterClass(
        name="Kỳ cựu (Veteran)",
        skill_range=(25, 55),
        description="Võ sĩ dày dạn kinh nghiệm, thi đấu ổn định và khó bị bắt bài."
    ),
    FighterClass(
        name="Ngôi sao (Contender)",
        skill_range=(45, 70),
        description="Võ sĩ thuộc top đầu, có khả năng tranh đai vô địch."
    ),
    FighterClass(
        name="Nhà vô địch (Champion)",
        skill_range=(55, 85),
        description="Đỉnh cao của giới đấu, sở hữu kỹ năng và bản lĩnh vượt trội."
    ),
    FighterClass(
        name="Huyền thoại (Legend)",
        skill_range=(55, 95),
        description="Một biểu tượng của môn thể thao, đã chứng tỏ đẳng cấp qua nhiều thế hệ."
    )
]

# Map for convenient lookups across the project
FIGHTER_CLASSES: Dict[str, FighterClass] = {fc.name: fc for fc in _ALL_FIGHTER_CLASSES}