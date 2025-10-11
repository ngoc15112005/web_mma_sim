import random

def analyze_battle_result_expanded(a, b):
    """
    Phân tích kết quả trận đấu với thang điểm mở rộng (0-100+).
    Trả về mô tả tiếng Việt tương ứng với mức độ chênh lệch.
    """
    # --- 1. Xử lý hòa ---
    if a == b:
        if a <= 20:
            return f"Hòa thăm dò ({a}-{b}) trong thế trận chậm rãi"
        elif a <= 60:
            return f"Hòa kịch tính ({a}-{b}) – hai bên ăn miếng trả miếng"
        else:
            return f"Hòa mãn nhãn ({a}-{b}) sau một màn đôi công dữ dội!"

    # --- 2. Xác định điểm thắng/thua ---
    if a > b:
        diem_thang, diem_thua = a, b
    else:
        diem_thang, diem_thua = b, a

    diff = diem_thang - diem_thua

    # --- 3. Mô tả dựa trên chênh lệch ---
    if diem_thua == 0:
        if diem_thang <= 40:
            return f"Chặn đứng hoàn toàn ({diem_thang}-{diem_thua}) – đối thủ không kịp nhập cuộc"
        else:
            return f"Hủy diệt tuyệt đối ({diem_thang}-{diem_thua}) – một chiều từ đầu tới cuối"

    if diff <= 15:
        return f"Thắng sát nút ({diem_thang}-{diem_thua}) – phân định bởi những khoảnh khắc nhỏ"
    elif diff <= 35:
        return f"Thắng thuyết phục ({diem_thang}-{diem_thua}) – kiểm soát phần lớn thời lượng"
    elif diff <= 60:
        return f"Áp đảo toàn diện ({diem_thang}-{diem_thua}) – áp lực liên tục dồn lên đối thủ"
    else:
        return f"Outclass hoàn toàn ({diem_thang}-{diem_thua}) – đẳng cấp cách biệt rõ rệt"