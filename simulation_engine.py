from models import Fighter, FightResult
from fight import Fight

def run_simulation(fighter_a: Fighter, fighter_b: Fighter, num_rounds: int) -> FightResult:
    """
    Hàm điều phối chính, tạo một trận đấu và chạy mô phỏng.
    Đây là điểm kết nối giữa giao diện người dùng và logic cốt lõi.
    """
    # 1. Tạo một đối tượng Fight, đóng gói tất cả logic của một trận đấu
    fight = Fight(fighter_a, fighter_b, num_rounds)
    
    # 2. Thực hiện toàn bộ quá trình mô phỏng
    fight.simulate()
    
    # 3. Trả về kết quả cuối cùng
    # Sau khi .simulate() chạy, fight.result sẽ chứa đối tượng FightResult
    if fight.result is None:
        raise ValueError("Mô phỏng không tạo ra kết quả.")
        
    return fight.result