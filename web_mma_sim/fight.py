import random
from typing import Optional

from models import Fighter, FightResult, FinishInfo
from fight_logic import simulate_fight_scores
from battle_result import analyze_battle_result_expanded
from finish_method import get_dynamic_finish_method
from fight_time import generate_dynamic_fight_time
import config

class Fight:
    """
    Đại diện cho một trận đấu, đóng gói toàn bộ logic mô phỏng.
    Đây là "bộ não" chính của ứng dụng.
    """
    def __init__(self, fighter_a: Fighter, fighter_b: Fighter, num_rounds: int):
        self.fighter_a = fighter_a
        self.fighter_b = fighter_b
        self.num_rounds = num_rounds
        self.result: Optional[FightResult] = None # Kết quả sẽ được lưu ở đây sau khi mô phỏng

    def simulate(self):
        """
        Thực hiện toàn bộ quá trình mô phỏng trận đấu.
        """
        # 1. Mô phỏng điểm số
        score_a, score_b = simulate_fight_scores(self.fighter_a, self.fighter_b)

        # 2. Phân tích kết quả
        result_description = analyze_battle_result_expanded(score_a, score_b)
        score_diff = abs(score_a - score_b)

        # 3. Xử lý logic kết liễu
        if score_a == score_b: # Trường hợp Hòa
            finish = FinishInfo(
                archetype_name="Không có",
                archetype_description="Trận đấu kết thúc với tỷ số hòa.",
                description=random.choice(config.FINISH_METHODS["DRAW"]),
                method_type="DRAW"
            )
            time_info = generate_dynamic_fight_time("DRAW", self.num_rounds)
        else: # Trường hợp có người thắng
            # Xác định người thắng và lấy archetype từ chính đối tượng Fighter đó
            winner = self.fighter_a if score_a > score_b else self.fighter_b
            winner_archetype_name = winner.archetype.name

            # Truyền archetype của người thắng vào các hàm logic
            finish = get_dynamic_finish_method(winner_archetype_name, score_diff)
            time_info = generate_dynamic_fight_time(finish.method_type, self.num_rounds, winner_archetype_name, score_diff)

        # 4. Gán kết quả cuối cùng vào thuộc tính `result` của lớp
        self.result = FightResult(
            score_a=score_a,
            score_b=score_b,
            result_description=result_description,
            finish_info=finish,
            time_info=time_info
        )