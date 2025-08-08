import random

def analyze_battle_result_expanded(a, b):
    """
    Phân tích kết quả trận đấu với phạm vi điểm mở rộng (0-7).
    Cung cấp các mô tả chi tiết và đa dạng hơn.
    """
    # --- 1. XỬ LÝ HÒA ---
    if a == b:
        if a <= 1:
            return f"🤝 Hòa nhạt nhẽo ({a}-{b}) – một trận đấu thiếu điểm nhấn"
        elif a <= 4:
            return f"🤝 Hòa kịch tính ({a}-{b}) – một trận đấu cân tài cân sức"
        else: # a > 4
            return f"🤝 Hòa mãn nhãn ({a}-{b}) – cống hiến một cuộc đôi công đỉnh cao!"

    # --- 2. XÁC ĐỊNH THẮNG/THUA ---
    if a > b:
        diem_thang, diem_thua = a, b
        prefix_thang, prefix_thua = "✅", "❌"
        nguoi_thang = "Bạn"
    else:
        diem_thang, diem_thua = b, a
        prefix_thang, prefix_thua = "❌", "✅"
        nguoi_thang = "Đối thủ"

    diff = diem_thang - diem_thua
    
    # --- 3. MÔ TẢ DỰA TRÊN CHÊNH LỆCH ---
    # Trường hợp thắng/thua trắng
    if diem_thua == 0:
        if diem_thang <= 2:
            return f"{prefix_thang} Thắng/Thua tuyệt đối ({diem_thang}-{diem_thua}) – kiểm soát hoàn toàn thế trận"
        else:
            return f"{prefix_thang} Màn hủy diệt ({diem_thang}-{diem_thua}) – một buổi học miễn phí cho đối thủ"

    # Trường hợp thắng/thua sít sao
    if diff == 1:
        if diem_thang <= 4:
            return f"{prefix_thang} Thắng/Thua nghẹt thở ({diem_thang}-{diem_thua}) – vượt qua trong gang tấc"
        else:
            return f"{prefix_thang} Sống sót sau một cuộc chiến huyền thoại ({diem_thang}-{diem_thua}) – chiến thắng bằng ý chí!"
            
    # Trường hợp thắng/thua thuyết phục
    elif diff <= 3:
        return f"{prefix_thang} Thắng/Thua thuyết phục ({diem_thang}-{diem_thua}) – thể hiện sự vượt trội"
        
    # Trường hợp thắng/thua áp đảo
    elif diff <= 5:
        return f"{prefix_thang} Áp đảo ({diem_thang}-{diem_thua}) – hoàn toàn làm chủ trận đấu"
        
    # Trường hợp thắng/thua hủy diệt
    else: # diff > 5
        return f"{prefix_thang} Out trình hoàn toàn ({diem_thang}-{diem_thua}) – đối thủ chỉ biết chịu trận"
