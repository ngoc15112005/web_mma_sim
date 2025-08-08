"""
Tập trung tất cả các hằng số, trọng số và các giá trị cấu hình
để dễ dàng cân bằng và tinh chỉnh game.
"""

# --- Cấu hình Logic Trận đấu (fight_logic.py) ---
PERFORMANCE_FACTOR_RANGE = (-2, 4) # (min, max) của yếu tố phong độ

# --- Cấu hình Phương thức Kết liễu (finish_method.py) ---
FINISH_METHODS = {
    "KO": [
        "Đấm thẳng mặt", "Móc ngang", "Uppercut", "Counterpunch",
        "Gối bay", "Đá đầu", "Đá xoay", "Elbow", "Body Shot",
        "KO (Đòn Slam)", "KO (Đòn xoay/Spinning Attack)"
    ],
    "TKO": [
        "Ground and Pound", "Standing no defense", "Combo đấm áp đảo",
        "TKO (Bác sĩ dừng trận - Vết rách)", "TKO (Góc ném khăn/Corner Stoppage)",
        "TKO (Chấn thương/Injury)", "TKO (Bỏ cuộc giữa hiệp/Retirement)",
        "TKO (Đầu hàng vì dính đòn/Submission to Strikes)"
    ],
    "SUB": [
        "Rear Naked Choke", "Armbar", "Triangle Choke", "Guillotine Choke",
        "Kimura", "Americana", "Twister", "Von Flue Choke", "Suloev Stretch",
        "Ezekiel Choke", "Peruvian Necktie", "Banana Split",
        "Heel Hook", "Kneebar", "Anaconda Choke", "D'Arce Choke"
    ],
    "DEC": [
        "Thắng điểm đồng thuận (Unanimous Decision)",
        "Thắng điểm chia (Split Decision)",
        "Thắng điểm đa số (Majority Decision)"
    ],
    "DQ": [
        "Thắng do đối thủ phạm luật (Đòn chỏ 12-6)",
        "Thắng do đối thủ phạm luật (Lên gối vào đầu đối thủ đang nằm)",
        "Thắng do đối thủ phạm luật (Giữ lồng/quần liên tục)",
        "Bị loại vì phạm luật (Ra đòn sau tiếng chuông)"
    ],
    "NC": ["No Contest (Vô hiệu)"],
    "DRAW": ["Hòa điểm đồng thuận (Draw)", "Hòa điểm đa số (Majority Draw)"]
}

FIGHTER_ARCHETYPES_DATA = {
    # Striking-focused
    "Power Puncher / Brawler": {"weights": {"KO": 60, "TKO": 25, "SUB": 1, "DEC": 9}, "description": "Dựa vào sức mạnh, luôn tìm kiếm một cú đấm 'trời giáng' để kết thúc trận đấu."},
    "Technical Boxer": {"weights": {"KO": 20, "TKO": 40, "SUB": 1, "DEC": 34}, "description": "Bậc thầy về footwork và combo chính xác, thường thắng bằng TKO hoặc điểm số áp đảo."},
    "Kickboxer / Muay Thai Specialist": {"weights": {"KO": 45, "TKO": 35, "SUB": 2, "DEC": 13}, "description": "Sử dụng đa dạng các đòn chân, gối, chỏ tàn khốc, đặc biệt nguy hiểm khi áp sát."},
    "Counter Striker": {"weights": {"KO": 50, "TKO": 20, "SUB": 2, "DEC": 23}, "description": "Kiên nhẫn, dụ đối thủ tấn công để tung ra những đòn phản công chớp nhoáng và chính xác."},
    "Volume Striker": {"weights": {"KO": 10, "TKO": 45, "SUB": 2, "DEC": 38}, "description": "Tấn công liên tục với số lượng lớn để áp đảo đối thủ, yêu cầu thể lực phi thường."},
    "Movement-Based Striker / Point Fighter": {"weights": {"KO": 5, "TKO": 10, "SUB": 1, "DEC": 79}, "description": "Sử dụng footwork linh hoạt và tốc độ để ra đòn từ bên ngoài, tích lũy điểm số và tránh giao tranh."},
    "Unorthodox Striker": {"weights": {"KO": 45, "TKO": 20, "SUB": 5, "DEC": 25}, "description": "Sử dụng các kỹ thuật khó đoán (Karate, Capoeira), tạo ra những cú KO bất ngờ."},
    # Grappling-focused
    "BJJ Specialist": {"weights": {"KO": 2, "TKO": 8, "SUB": 70, "DEC": 15}, "description": "Bậc thầy địa chiến, mục tiêu chính là đưa trận đấu xuống sàn và tìm kiếm đòn khóa siết."},
    "Wrestler": {"weights": {"KO": 5, "TKO": 45, "SUB": 10, "DEC": 35}, "description": "Kỹ năng vật và quật ngã thượng thừa, bào mòn thể lực đối thủ bằng Ground and Pound."},
    "Sambo Specialist": {"weights": {"KO": 5, "TKO": 20, "SUB": 55, "DEC": 15}, "description": "Kết hợp các đòn quật ngã mạnh mẽ và các đòn khóa chân (leg locks) cực kỳ nguy hiểm."},
    "Submission Wrestler (Catch Wrestler)": {"weights": {"KO": 5, "TKO": 30, "SUB": 50, "DEC": 10}, "description": "Tập trung vào kiểm soát từ vị trí trên, dùng các kỹ thuật khóa siết gây đau đớn để buộc đối thủ đầu hàng."},
    # Hybrid/All-rounders
    "Wrestle-Boxer": {"weights": {"KO": 25, "TKO": 30, "SUB": 15, "DEC": 25}, "description": "Lối đánh toàn diện, dùng boxing để thiết lập vật hoặc dùng vật để tạo cơ hội cho striking."},
    "Pressure Fighter": {"weights": {"KO": 15, "TKO": 40, "SUB": 10, "DEC": 30}, "description": "Luôn tiến về phía trước, dồn ép đối thủ vào lưới và bào mòn họ bằng cả striking và grappling."},
    "Violent Virtuoso / Nghệ Sĩ Bạo Lực": {
        "weights": {"KO": 28, "TKO": 35, "SUB": 35, "DEC": 2},
        "description": "Đây là hình mẫu võ sĩ hoàn hảo của kỷ nguyên mới. Sở hữu bộ kỹ năng toàn diện đến đáng sợ, họ có thể knockout đối thủ bằng một đòn duy nhất, áp đảo bằng Ground and Pound (TKO), hoặc siết ngạt trên sàn đấu (Submission). Phong cách của họ là sự tổng hòa của áp lực và bản năng 'sát thủ', luôn tìm kiếm cơ hội kết liễu và hiếm khi để trận đấu kéo dài đến quyết định của giám định."
    },
    "Clinch Fighter / Dirty Boxer": {"weights": {"KO": 10, "TKO": 45, "SUB": 5, "DEC": 35}, "description": "Bậc thầy ép lưới, kiểm soát và bào mòn đối thủ bằng các đòn gối, chỏ và đấm tầm gần."},
    # Specialists/Unique Styles
    "One-Round Monster": {"weights": {"KO": 50, "TKO": 30, "SUB": 15, "DEC": 0}, "description": "Cực kỳ bùng nổ và nguy hiểm trong hiệp 1, nhưng thể lực giảm sút nhanh chóng."},
    "Durable Grinder": {"weights": {"KO": 5, "TKO": 10, "SUB": 5, "DEC": 75}, "description": "Sở hữu 'cằm sắt' và sức bền phi thường, thường kéo đối thủ vào cuộc chiến thể lực."},
    "Glass Cannon": {"weights": {"KO": 65, "TKO": 25, "SUB": 2, "DEC": 3}, "description": "Sức tấn công cực kỳ khủng khiếp nhưng khả năng chịu đòn rất kém. 'Được ăn cả, ngã về không'."}
}

FINISH_SCORE_DIFF_OUTCLASS_THRESHOLD = 6
FINISH_SCORE_DIFF_CLOSE_THRESHOLD = 1
FINISH_OUTCLASS_MULTIPLIERS = {"KO": 2.0, "TKO": 1.5, "SUB": 1.5, "DEC": 0.1}
FINISH_CLOSE_MULTIPLIERS = {"DEC": 2.0}
FINISH_STATIC_WEIGHTS = {"DQ": 2, "NC": 1}

# --- Cấu hình Thời gian Trận đấu (fight_time.py) ---
TIME_SCORE_DIFF_OUTCLASS_THRESHOLD = 6
TIME_SCORE_DIFF_CLOSE_THRESHOLD = 2
TIME_OUTCLASS_ROUND_MULTIPLIERS = {1: 2.0, 2: 1.5} # Hệ số cho hiệp 1, hiệp 2
TIME_CLOSE_ROUND_MULTIPLIER = 1.2 # Hệ số cho hiệp cuối

TIME_ARCHETYPE_MODIFIERS = {
    "One-Round Monster": {"round_1_multiplier": 5.0, "other_rounds_multiplier": 0.2},
    "Durable Grinder": {"round_1_multiplier": 0.5, "final_round_multiplier": 2.0},
    "Glass Cannon": {"round_1_multiplier": 3.0}
}
