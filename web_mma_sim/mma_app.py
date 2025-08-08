import streamlit as st
import random
from finish_method import FIGHTER_ARCHETYPES
from fighter_class import FIGHTER_CLASSES
from fight import Fight
from models import Fighter, HistoryEntry, FightResult
import history_manager 

# Hằng số để giới hạn số lượng kết quả trong lịch sử
MAX_HISTORY_SIZE = 50

# Khởi tạo session state để lưu lịch sử nếu chưa có
if 'fight_history' not in st.session_state:
    st.session_state.fight_history = history_manager.load_history()

def display_fight_results(entry: HistoryEntry):
    """Hàm này chỉ chịu trách nhiệm hiển thị kết quả lên giao diện Streamlit."""
    result = entry.fight_result
    class_a = entry.class_a_name
    class_b = entry.class_b_name
    arch_a = entry.archetype_a_name
    arch_b = entry.archetype_b_name
    st.write(f"**Trận đấu:** `{class_a}` (`{arch_a}`) vs `{class_b}` (`{arch_b}`)")
    st.write(f"**Điểm kỹ năng:** `{result.score_a}` vs `{result.score_b}`")
    st.success(f"**Kết quả:** {result.result_description}")
 
    st.error(f"**Kiểu kết liễu:** {result.finish_info.description}")
    st.write(f"Thời điểm: Hiệp {result.time_info.round}/{result.time_info.num_rounds} – {result.time_info.minute}:{str(result.time_info.second).zfill(2)}")
    st.write(f"Ghi chú: {result.time_info.note}")

def get_simulation_parameters(
    selected_class_a: str, 
    selected_class_b: str, 
    selected_archetype_a: str, 
    selected_archetype_b: str
) -> tuple[str, str, str, str]:
    """Giai đoạn 1: Lấy và xử lý các tham số đầu vào từ UI, bao gồm cả lựa chọn 'Ngẫu nhiên'."""
    class_a_name = selected_class_a if selected_class_a != "Ngẫu nhiên" else random.choice(list(FIGHTER_CLASSES.keys()))
    class_b_name = selected_class_b if selected_class_b != "Ngẫu nhiên" else random.choice(list(FIGHTER_CLASSES.keys()))
    
    archetype_a_name = selected_archetype_a if selected_archetype_a != "Ngẫu nhiên" else random.choice(list(FIGHTER_ARCHETYPES.keys()))
    archetype_b_name = selected_archetype_b if selected_archetype_b != "Ngẫu nhiên" else random.choice(list(FIGHTER_ARCHETYPES.keys()))
    
    return class_a_name, class_b_name, archetype_a_name, archetype_b_name

def run_fight_simulation(
    class_a_name: str, 
    class_b_name: str, 
    archetype_a_name: str, 
    archetype_b_name: str, 
    num_rounds: int
) -> FightResult:
    """Giai đoạn 2: Tạo đối tượng, chạy mô phỏng trận đấu và trả về kết quả."""
    archetype_a_obj = FIGHTER_ARCHETYPES[archetype_a_name]
    archetype_b_obj = FIGHTER_ARCHETYPES[archetype_b_name]
    
    fighter_a = Fighter(fighter_class=FIGHTER_CLASSES[class_a_name], archetype=archetype_a_obj)
    fighter_b = Fighter(fighter_class=FIGHTER_CLASSES[class_b_name], archetype=archetype_b_obj)
    
    fight = Fight(fighter_a, fighter_b, num_rounds)
    fight.simulate()
    return fight.result

def update_history(
    fight_result: FightResult, 
    class_a_name: str, 
    class_b_name: str, 
    archetype_a_name: str, 
    archetype_b_name: str
):
    """Giai đoạn 3: Tạo entry mới, cập nhật và lưu lịch sử trận đấu."""
    history_entry = HistoryEntry(
        fight_result=fight_result,
        class_a_name=class_a_name,
        class_b_name=class_b_name,
        archetype_a_name=archetype_a_name,
        archetype_b_name=archetype_b_name
    )
    st.session_state.fight_history.insert(0, history_entry)
    # Giới hạn số lượng history, ghi đè cái cũ nhất
    st.session_state.fight_history = st.session_state.fight_history[:MAX_HISTORY_SIZE]
    # Lưu lịch sử cập nhật vào file
    history_manager.save_history(st.session_state.fight_history)

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
st.markdown("### 2. Chọn Phong Cách Thi Đấu")
archetype_options = ["Ngẫu nhiên"] + list(FIGHTER_ARCHETYPES.keys())
col3, col4 = st.columns(2)
with col3:
    selected_archetype_a = st.selectbox(
        "Phong cách Võ sĩ A:",
        archetype_options,
        key="archetype_a"
    )
    if selected_archetype_a != "Ngẫu nhiên":
        st.caption(FIGHTER_ARCHETYPES[selected_archetype_a].description)

with col4:
    selected_archetype_b = st.selectbox(
        "Phong cách Võ sĩ B:",
        archetype_options,
        key="archetype_b"
    )
    if selected_archetype_b != "Ngẫu nhiên":
        st.caption(FIGHTER_ARCHETYPES[selected_archetype_b].description)

if st.button("🎮 Mô phỏng trận đấu"):
    # Giai đoạn 1: Lấy và xử lý tham số
    class_a_name, class_b_name, archetype_a_name, archetype_b_name = get_simulation_parameters(
        selected_class_a, selected_class_b, selected_archetype_a, selected_archetype_b
    )

    # Giai đoạn 2: Chạy mô phỏng
    fight_result = run_fight_simulation(
        class_a_name, class_b_name, archetype_a_name, archetype_b_name, rounds
    )

    # Giai đoạn 3: Cập nhật và lưu lịch sử
    update_history(
        fight_result, class_a_name, class_b_name, archetype_a_name, archetype_b_name
    )

# --- Hiển thị Lịch sử ---
st.markdown("---")
st.markdown("## 📜 Lịch sử kết quả")

if not st.session_state.fight_history:
    st.info("Chưa có trận đấu nào được mô phỏng. Bấm nút 'Mô phỏng' để bắt đầu!")
else:
    # Thêm nút để xóa toàn bộ lịch sử
    if st.button("🗑️ Xóa lịch sử"):
        st.session_state.fight_history = []
        history_manager.save_history([]) # Xóa cả trong file
        st.rerun() # Chạy lại app để cập nhật giao diện ngay lập tức

    # Hiển thị từng kết quả trong lịch sử bằng st.expander
    for i, entry in enumerate(st.session_state.fight_history):
        result = entry.fight_result

        # Tạo tiêu đề tóm tắt cho expander
        summary = result.result_description.split('(')[0].strip().replace("✅ ", "").replace("❌ ", "")
        expander_title = f"Trận #{len(st.session_state.fight_history) - i}: {entry.class_a_name} vs {entry.class_b_name}  |  {summary}"

        # Mở sẵn expander của kết quả gần nhất (i=0)
        with st.expander(expander_title, expanded=(i == 0)):
            display_fight_results(entry)