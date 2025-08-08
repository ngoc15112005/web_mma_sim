import random
from typing import List, Dict
from models import FighterClass

# Định nghĩa dữ liệu gốc dưới dạng một danh sách các đối tượng FighterClass
_ALL_FIGHTER_CLASSES: List[FighterClass] = [
    FighterClass(
        name="Tân binh (Rookie)",
        skill_range=(0, 2),
        description="Võ sĩ mới vào nghề, còn non kinh nghiệm nhưng đầy tiềm năng."
    ),
    FighterClass(
        name="Kỳ cựu (Veteran)",
        skill_range=(2, 4),
        description="Võ sĩ dày dạn kinh nghiệm, thi đấu ổn định và khó bị bắt bài."
    ),
    FighterClass(
        name="Ngôi sao (Contender)",
        skill_range=(4, 6),
        description="Võ sĩ thuộc top đầu, có khả năng tranh đai vô địch."
    ),
    FighterClass(
        name="Nhà vô địch (Champion)",
        skill_range=(5, 7),
        description="Đỉnh cao của giải đấu, sở hữu kỹ năng và bản lĩnh vượt trội."
    ),
    FighterClass(
        name="Huyền thoại (Legend)",
        skill_range=(6, 7),
        description="Một biểu tượng của môn thể thao, đã chứng tỏ đẳng cấp qua nhiều thế hệ."
    )
]

# Tạo một dictionary (map) để các file khác có thể truy cập dễ dàng bằng tên.
# Tên biến `FIGHTER_CLASSES` được giữ nguyên để đảm bảo tương thích, không làm hỏng code ở các file khác.
FIGHTER_CLASSES: Dict[str, FighterClass] = {fc.name: fc for fc in _ALL_FIGHTER_CLASSES}