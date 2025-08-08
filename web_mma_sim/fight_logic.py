import random
from models import Fighter
import config

def simulate_fight_scores(fighter_a: Fighter, fighter_b: Fighter) -> tuple[int, int]:
    """
    Mô phỏng điểm số trận đấu bằng cách kết hợp kỹ năng cơ bản với "Yếu tố Phong độ".
    Điều này cho phép các kết quả bất ngờ (upset) và làm cho mô phỏng trở nên năng động hơn.
    Hàm này giờ nhận vào hai đối tượng Fighter.
    """
    # 1. Gọi phương thức generate_skill_point() từ chính đối tượng Fighter
    skill_a = fighter_a.generate_skill_point()
    skill_b = fighter_b.generate_skill_point()

    # 2. Tạo ra một "Yếu tố Phong độ" ngẫu nhiên cho mỗi võ sĩ trong trận đấu này
    # Tượng trưng cho việc họ có một ngày thi đấu tốt hay tệ.
    # Phạm vi rộng hơn cho phép các cuộc lật đổ kịch tính hơn.
    performance_a = random.randint(*config.PERFORMANCE_FACTOR_RANGE)
    performance_b = random.randint(*config.PERFORMANCE_FACTOR_RANGE)

    # 3. Tính điểm số cuối cùng
    final_score_a = skill_a + performance_a
    final_score_b = skill_b + performance_b

    # Đảm bảo điểm số không xuống dưới 0 để logic mô tả kết quả được đơn giản
    final_score_a = max(0, final_score_a)
    final_score_b = max(0, final_score_b)

    return final_score_a, final_score_b