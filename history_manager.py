import json
import os
from dataclasses import asdict
from typing import List

from models import HistoryEntry, FightResult, FinishInfo, TimeInfo

# Hằng số cho tên file, để dễ dàng thay đổi nếu cần
HISTORY_FILE_PATH = "fight_history.json"

def save_history(history: List[HistoryEntry]):
    """
    Chuyển đổi danh sách các đối tượng HistoryEntry thành JSON và lưu vào file.
    Sử dụng dataclasses.asdict để chuyển đổi object thành dictionary một cách tự động.
    """
    try:
        # Chuyển đổi toàn bộ danh sách các đối tượng dataclass thành danh sách các dictionary
        history_as_dicts = [asdict(entry) for entry in history]
        with open(HISTORY_FILE_PATH, 'w', encoding='utf-8') as f:
            # Ghi vào file JSON với định dạng đẹp (indent=4) và hỗ trợ ký tự Unicode
            json.dump(history_as_dicts, f, ensure_ascii=False, indent=4)
    except IOError as e:
        # Trong một ứng dụng thực tế, bạn có thể muốn ghi log lỗi này
        print(f"Lỗi khi lưu lịch sử: {e}")

def load_history() -> List[HistoryEntry]:
    """
    Tải lịch sử từ file JSON và chuyển đổi ngược lại thành danh sách các đối tượng HistoryEntry.
    Xử lý các trường hợp file không tồn tại hoặc bị lỗi.
    """
    # Nếu file không tồn tại, trả về danh sách rỗng, không gây lỗi
    if not os.path.exists(HISTORY_FILE_PATH):
        return []

    try:
        with open(HISTORY_FILE_PATH, 'r', encoding='utf-8') as f:
            # Đọc dữ liệu từ file JSON
            history_as_dicts = json.load(f)

        # Tái cấu trúc lại các đối tượng dataclass từ dictionary
        reconstructed_history = []
        for entry_dict in history_as_dicts:
            # Tái cấu trúc các đối tượng lồng nhau trước
            fr_dict = entry_dict['fight_result']
            finish_info = FinishInfo(**fr_dict['finish_info'])
            time_info = TimeInfo(**fr_dict['time_info'])
            
            # Tạo lại đối tượng FightResult
            fight_result = FightResult(**{k: v for k, v in fr_dict.items() if k not in ['finish_info', 'time_info']}, finish_info=finish_info, time_info=time_info)
            
            # Tạo lại đối tượng HistoryEntry cấp cao nhất
            # Tách dữ liệu cho HistoryEntry và cung cấp giá trị mặc định cho các trường mới
            # để đảm bảo tương thích ngược với các file lịch sử cũ.
            history_entry_data = {k: v for k, v in entry_dict.items() if k != 'fight_result'}
            history_entry_data['fight_result'] = fight_result
            history_entry_data.setdefault('archetype_a_name', 'Không rõ')
            history_entry_data.setdefault('archetype_b_name', 'Không rõ')

            history_entry = HistoryEntry(**history_entry_data)
            reconstructed_history.append(history_entry)
        
        return reconstructed_history
    except (IOError, json.JSONDecodeError, KeyError, TypeError) as e:
        # Nếu file bị lỗi (sai định dạng, thiếu key...), trả về danh sách rỗng để ứng dụng không bị crash
        print(f"Lỗi khi tải lịch sử (file có thể bị hỏng), bắt đầu với lịch sử trống: {e}")
        return []