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
    "Power Puncher / Brawler": {
        "weights": {"KO": 60, "TKO": 25, "SUB": 1, "DEC": 9},
        "description": "Dựa vào sức mạnh, luôn tìm kiếm một cú đấm 'trời giáng' để kết thúc trận đấu.",
        "preferred_kos": ["Đấm thẳng mặt", "Móc ngang", "Uppercut", "Counterpunch"],
        "preferred_tkos": ["Ground and Pound", "Combo đấm áp đảo", "Standing no defense"]
    },
    "Technical Boxer": {
        "weights": {"KO": 20, "TKO": 40, "SUB": 1, "DEC": 34},
        "description": "Bậc thầy về footwork và combo chính xác, thường thắng bằng TKO hoặc điểm số áp đảo.",
        "preferred_kos": ["Counterpunch", "Đấm thẳng mặt"],
        "preferred_tkos": ["Combo đấm áp đảo", "Standing no defense", "TKO (Bác sĩ dừng trận - Vết rách)"]
    },
    "Kickboxer / Muay Thai Specialist": {
        "weights": {"KO": 45, "TKO": 35, "SUB": 2, "DEC": 13},
        "description": "Sử dụng đa dạng các đòn chân, gối, chỏ tàn khốc, đặc biệt nguy hiểm khi áp sát.",
        "preferred_kos": ["Đá đầu", "Gối bay", "Elbow", "Body Shot"],
        "preferred_tkos": ["TKO (Bác sĩ dừng trận - Vết rách)", "TKO (Chấn thương/Injury)", "Combo đấm áp đảo"]
    },
    "Counter Striker": {
        "weights": {"KO": 50, "TKO": 20, "SUB": 2, "DEC": 23},
        "description": "Kiên nhẫn, dụ đối thủ tấn công để tung ra những đòn phản công chớp nhoáng và chính xác.",
        "preferred_kos": ["Counterpunch", "Đấm thẳng mặt", "Đá đầu"]
    },
    "Volume Striker": {
        "weights": {"KO": 10, "TKO": 45, "SUB": 2, "DEC": 38},
        "description": "Tấn công liên tục với số lượng lớn để áp đảo đối thủ, yêu cầu thể lực phi thường.",
        "preferred_tkos": ["Combo đấm áp đảo", "Standing no defense", "TKO (Góc ném khăn/Corner Stoppage)"]
    },
    "Movement-Based Striker / Point Fighter": {
        "weights": {"KO": 5, "TKO": 10, "SUB": 1, "DEC": 79},
        "description": "Sử dụng footwork linh hoạt và tốc độ để ra đòn từ bên ngoài, tích lũy điểm số và tránh giao tranh."
        # Finishes are rare, so we let them be generic from the main list
    },
    "Unorthodox Striker": {
        "weights": {"KO": 45, "TKO": 20, "SUB": 5, "DEC": 25},
        "description": "Sử dụng các kỹ thuật khó đoán (Karate, Capoeira), tạo ra những cú KO bất ngờ.",
        "preferred_kos": ["Đá xoay", "KO (Đòn xoay/Spinning Attack)", "Gối bay", "Elbow"]
    },
    # Grappling-focused
    "BJJ Specialist": {
        "weights": {"KO": 2, "TKO": 8, "SUB": 70, "DEC": 15},
        "description": "Bậc thầy địa chiến, mục tiêu chính là đưa trận đấu xuống sàn và tìm kiếm đòn khóa siết.",
        "preferred_submissions": {
            "common": ["Rear Naked Choke", "Guillotine Choke", "Armbar", "Triangle Choke"],
            "uncommon": ["Kimura", "D'Arce Choke", "Anaconda Choke"],
            "rare": ["Twister", "Peruvian Necktie", "Ezekiel Choke"]
        }
    },
    "Wrestler": {
        "weights": {"KO": 5, "TKO": 45, "SUB": 10, "DEC": 35},
        "description": "Kỹ năng vật và quật ngã thượng thừa, bào mòn thể lực đối thủ bằng Ground and Pound.",
        "preferred_tkos": ["Ground and Pound", "TKO (Đòn Slam)", "TKO (Bỏ cuộc giữa hiệp/Retirement)"],
        "preferred_submissions": ["Guillotine Choke", "Von Flue Choke", "Anaconda Choke"]
    },
    "Sambo Specialist": {
        "weights": {"KO": 5, "TKO": 20, "SUB": 55, "DEC": 15},
        "description": "Kết hợp các đòn quật ngã mạnh mẽ và các đòn khóa chân (leg locks) cực kỳ nguy hiểm.",
        "preferred_tkos": ["TKO (Đòn Slam)"],
        "preferred_submissions": {
            "common": ["Heel Hook", "Kneebar", "Armbar"],
            "uncommon": ["Suloev Stretch", "Americana"],
            "rare": ["Twister"]
        }
    },
    "Submission Wrestler (Catch Wrestler)": {
        "weights": {"KO": 5, "TKO": 30, "SUB": 50, "DEC": 10},
        "description": "Tập trung vào kiểm soát từ vị trí trên, dùng các kỹ thuật khóa siết gây đau đớn để buộc đối thủ đầu hàng.",
        "preferred_tkos": ["Ground and Pound", "TKO (Đầu hàng vì dính đòn/Submission to Strikes)"],
        "preferred_submissions": ["Kimura", "Guillotine Choke", "Kneebar", "Americana"]
    },
    # Hybrid/All-rounders
    "Balanced Finisher / MMA Generalist": {
        "weights": {"KO": 30, "TKO": 30, "SUB": 30, "DEC": 10},
        "description": (
            "Một võ sĩ toàn diện, có khả năng kết thúc trận đấu ở bất kỳ vị trí nào: "
            "knockout bằng striking, TKO bằng áp lực và ground-and-pound, hoặc khóa siết "
            "đối thủ trên sàn. Luôn mang lại cảm giác khó đoán cho đối thủ."
        ),
        "preferred_kos": ["Đấm thẳng mặt", "Counterpunch", "Đá đầu"],
        "preferred_tkos": ["Ground and Pound", "Combo đấm áp đảo", "TKO (Đầu hàng vì dính đòn/Submission to Strikes)"],
        "preferred_submissions": ["Rear Naked Choke", "Armbar", "Guillotine Choke", "Triangle Choke"]
    },
    "Wrestle-Boxer": {
        "weights": {"KO": 25, "TKO": 30, "SUB": 15, "DEC": 25},
        "description": "Lối đánh toàn diện, dùng boxing để thiết lập vật hoặc dùng vật để tạo cơ hội cho striking.",
        "preferred_kos": ["Đấm thẳng mặt", "Móc ngang"],
        "preferred_tkos": ["Ground and Pound", "Combo đấm áp đảo"],
        "preferred_submissions": ["Guillotine Choke", "Rear Naked Choke", "D'Arce Choke"]
    },
    "Pressure Fighter": {
        "weights": {"KO": 15, "TKO": 40, "SUB": 10, "DEC": 30},
        "description": "Luôn tiến về phía trước, dồn ép đối thủ vào lưới và bào mòn họ bằng cả striking và grappling.",
        "preferred_tkos": ["Ground and Pound", "Combo đấm áp đảo", "TKO (Góc ném khăn/Corner Stoppage)", "TKO (Đầu hàng vì dính đòn/Submission to Strikes)"]
    },
    "Clinch Fighter / Dirty Boxer": {
        "weights": {"KO": 10, "TKO": 45, "SUB": 5, "DEC": 35},
        "description": "Bậc thầy ép lưới, kiểm soát và bào mòn đối thủ bằng các đòn gối, chỏ và đấm tầm gần.",
        "preferred_kos": ["Elbow", "Body Shot"],
        "preferred_tkos": ["TKO (Bác sĩ dừng trận - Vết rách)", "Combo đấm áp đảo", "Ground and Pound"],
        "preferred_submissions": ["Guillotine Choke"]
    },
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
