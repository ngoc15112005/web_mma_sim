import streamlit as st
import random
from finish_method import FIGHTER_ARCHETYPES
from fighter_class import FIGHTER_CLASSES
from models import FightResult, Fighter
from fight import Fight

def display_fight_results(result: FightResult, class_a: str, class_b: str):
    """Hàm này chỉ chịu trách nhiệm hiển thị kết quả lên giao diện Streamlit."""
    st.markdown("## Kết quả mô phỏng")
    st.write(f"**Trận đấu:** `{class_a}` (A) vs `{class_b}` (B)")
    st.write(f"**Điểm kỹ năng:** `{result.score_a}` vs `{result.score_b}`")
    st.success(f"**Kết quả:** {result.result_description}")
 
    st.error(f"**Kiểu kết liễu:** {result.finish_info.description}")
    st.write(f"Thời điểm: Hiệp {result.time_info.round}/{result.time_info.num_rounds} – {result.time_info.minute}:{str(result.time_info.second).zfill(2)}")
    st.write(f"Ghi chú: {result.time_info.note}")

# --- Giao diện ---
st.title("🔥 Mô Phỏng MMA Vĩ Đại 🔥")
rounds = st.radio("Chọn số hiệp:", [3, 5], index=0)

st.markdown("---")

# --- Lựa chọn Võ sĩ ---
st.markdown("### 1. Chọn Đẳng Cấp Võ Sĩ")
class_options = ["Ngẫu nhiên"] + list(FIGHTER_CLASSES.keys())
col1, col2 = st.columns(2)
with col1:
    selected_class_a = st.selectbox("Võ sĩ A:", class_options, key="class_a")
with col2:
    selected_class_b = st.selectbox("Võ sĩ B:", class_options, key="class_b")

# --- Lựa chọn Phong cách ---
st.markdown("### 2. Chọn Phong Cách Thi Đấu (của người thắng)")
archetype_options = ["Ngẫu nhiên"] + list(FIGHTER_ARCHETYPES.keys())
 
# Lấy mô tả và index dựa trên giá trị hiện tại của widget để duy trì trạng thái UI
description_for_help = "Di chuột vào đây sau khi chọn một phong cách để xem mô tả chi tiết."
default_index = 0
if 'archetype_selector' in st.session_state and st.session_state.archetype_selector != "Ngẫu nhiên":
    selected_value = st.session_state.archetype_selector
    # Truy cập thuộc tính .description của đối tượng Archetype
    description_for_help = FIGHTER_ARCHETYPES[selected_value].description
    # Tìm index của lựa chọn trước đó để đặt làm giá trị mặc định cho lần chạy này
    if selected_value in archetype_options:
        default_index = archetype_options.index(selected_value)
 
selected_archetype = st.selectbox(
    "Phong cách:",
    archetype_options,
    index=default_index, # Đặt giá trị mặc định để duy trì lựa chọn trên UI
    key="archetype_selector", # Key để truy cập giá trị trong session_state
    help=description_for_help
)

if st.button("🎮 Mô phỏng trận đấu"):
    # 1. Lấy tên đẳng cấp và phong cách từ UI, xử lý trường hợp "Ngẫu nhiên"
    class_a_name = selected_class_a if selected_class_a != "Ngẫu nhiên" else random.choice(list(FIGHTER_CLASSES.keys()))
    class_b_name = selected_class_b if selected_class_b != "Ngẫu nhiên" else random.choice(list(FIGHTER_CLASSES.keys()))
    archetype_name = selected_archetype if selected_archetype != "Ngẫu nhiên" else random.choice(list(FIGHTER_ARCHETYPES.keys()))

    # 2. Tạo các đối tượng Fighter
    # Giả định cả hai võ sĩ đều có cùng phong cách được chọn (hoặc ngẫu nhiên)
    # Đây là một điểm có thể mở rộng trong tương lai (mỗi võ sĩ có phong cách riêng)
    archetype_obj = FIGHTER_ARCHETYPES[archetype_name]
    fighter_a = Fighter(fighter_class=FIGHTER_CLASSES[class_a_name], archetype=archetype_obj)
    fighter_b = Fighter(fighter_class=FIGHTER_CLASSES[class_b_name], archetype=archetype_obj)
    
    # 3. Tạo và chạy mô phỏng thông qua đối tượng Fight
    fight = Fight(fighter_a, fighter_b, rounds)
    fight.simulate()
    fight_result = fight.result
    
    # 4. Hiển thị kết quả ra giao diện, sử dụng tên đẳng cấp thực tế đã được mô phỏng
    display_fight_results(fight_result, class_a_name, class_b_name)