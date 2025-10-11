import random
import streamlit as st

from finish_method import FIGHTER_ARCHETYPES
from fighter_class import FIGHTER_CLASSES
from models import Fighter, HistoryEntry, FightResult
import history_manager
from simulation_engine import run_simulation as core_run_simulation

MAX_HISTORY_SIZE = 50

CLASS_POWER_ORDER = [
    "Tân binh (Rookie)",
    "Kỳ cựu (Veteran)",
    "Ngôi sao (Contender)",
    "Nhà vô địch (Champion)",
    "Huyền thoại (Legend)",
]
CLASS_POWER_INDEX = {name: idx for idx, name in enumerate(CLASS_POWER_ORDER)}

DIFF_BUCKETS = [
    (15, "Thắng sát nút", "Trận đấu có thể đổi chiều chỉ bằng một pha ra đòn.", "info"),
    (35, "Thắng thuyết phục", "Áp lực đều đặn qua từng hiệp.", "success"),
    (60, "Áp đảo toàn diện", "Đối thủ liên tục ở thế chống đỡ.", "warning"),
    (float("inf"), "Outclass hoàn toàn", "Đẳng cấp khác biệt rõ rệt.", "error"),
]
ALERT_RENDERERS = {
    "info": st.info,
    "success": st.success,
    "warning": st.warning,
    "error": st.error,
}


if "fight_history" not in st.session_state:
    st.session_state.fight_history = history_manager.load_history()


def class_rank(name: str) -> int:
    return CLASS_POWER_INDEX.get(name, len(CLASS_POWER_ORDER))


def describe_diff(diff: int):
    if diff == 0:
        return None
    for threshold, title, detail, style in DIFF_BUCKETS:
        if diff <= threshold:
            return title, detail, style
    return None


def detect_upset(entry: HistoryEntry, result: FightResult, diff: int) -> str | None:
    if diff == 0:
        return None
    if result.score_a > result.score_b:
        winner_class = entry.class_a_name
        loser_class = entry.class_b_name
    else:
        winner_class = entry.class_b_name
        loser_class = entry.class_a_name
    winner_rank = class_rank(winner_class)
    loser_rank = class_rank(loser_class)
    if winner_rank < loser_rank and diff >= 40:
        return f"UPSET! {winner_class} tạo địa chấn trước {loser_class}."
    return None


def display_fight_results(entry: HistoryEntry):
    result = entry.fight_result
    class_a = entry.class_a_name
    class_b = entry.class_b_name
    arch_a = entry.archetype_a_name
    arch_b = entry.archetype_b_name
    diff = abs(result.score_a - result.score_b)

    st.subheader("Tổng kết trận đấu – Thang điểm 0-100")
    st.write(f"**Trận đấu:** `{class_a}` (`{arch_a}`) vs `{class_b}` (`{arch_b}`)")
    st.write(
        f"**Điểm số:** `{result.score_a}` – `{result.score_b}`  *(chênh {diff})*"
    )
    st.caption("Điểm = Kỹ năng ngày đấu + phong độ trận đấu (thang 0-100+).")

    diff_summary = describe_diff(diff)
    if diff_summary:
        title, detail, style = diff_summary
        ALERT_RENDERERS[style](f"{title} (Δ {diff}) – {detail}")

    upset = detect_upset(entry, result, diff)
    if upset:
        st.warning(upset)

    st.success(f"**Kết quả:** {result.result_description}")
    st.write(
        f"**Kiểu kết thúc:** {result.finish_info.method_type} – {result.finish_info.description}"
    )
    st.write(
        f"**Phong cách người thắng:** {result.finish_info.archetype_name}"
    )
    st.write(
        f"**Thời điểm:** Hiệp {result.time_info.round}/{result.time_info.num_rounds} – "
        f"{result.time_info.minute}:{str(result.time_info.second).zfill(2)}"
    )
    st.caption(result.time_info.note)


def get_simulation_parameters(
    selected_class_a: str,
    selected_class_b: str,
    selected_archetype_a: str,
    selected_archetype_b: str,
) -> tuple[str, str, str, str]:
    class_a_name = (
        selected_class_a
        if selected_class_a != "Ngẫu nhiên"
        else random.choice(list(FIGHTER_CLASSES.keys()))
    )
    class_b_name = (
        selected_class_b
        if selected_class_b != "Ngẫu nhiên"
        else random.choice(list(FIGHTER_CLASSES.keys()))
    )

    archetype_a_name = (
        selected_archetype_a
        if selected_archetype_a != "Ngẫu nhiên"
        else random.choice(list(FIGHTER_ARCHETYPES.keys()))
    )
    archetype_b_name = (
        selected_archetype_b
        if selected_archetype_b != "Ngẫu nhiên"
        else random.choice(list(FIGHTER_ARCHETYPES.keys()))
    )

    return class_a_name, class_b_name, archetype_a_name, archetype_b_name


def run_fight_simulation(
    class_a_name: str,
    class_b_name: str,
    archetype_a_name: str,
    archetype_b_name: str,
    num_rounds: int,
) -> FightResult:
    archetype_a_obj = FIGHTER_ARCHETYPES[archetype_a_name]
    archetype_b_obj = FIGHTER_ARCHETYPES[archetype_b_name]

    fighter_a = Fighter(
        fighter_class=FIGHTER_CLASSES[class_a_name],
        archetype=archetype_a_obj,
    )
    fighter_b = Fighter(
        fighter_class=FIGHTER_CLASSES[class_b_name],
        archetype=archetype_b_obj,
    )
    return core_run_simulation(fighter_a, fighter_b, num_rounds)


def update_history(
    fight_result: FightResult,
    class_a_name: str,
    class_b_name: str,
    archetype_a_name: str,
    archetype_b_name: str,
):
    history_entry = HistoryEntry(
        fight_result=fight_result,
        class_a_name=class_a_name,
        class_b_name=class_b_name,
        archetype_a_name=archetype_a_name,
        archetype_b_name=archetype_b_name,
    )
    st.session_state.fight_history.insert(0, history_entry)
    st.session_state.fight_history = st.session_state.fight_history[:MAX_HISTORY_SIZE]
    history_manager.save_history(st.session_state.fight_history)


st.title("🔥 Mô phỏng MMA – Thang điểm 0-100")
rounds = st.radio("Chọn số hiệp:", [3, 5], index=0)

st.markdown("---")

st.markdown("### 1. Chọn hạng đấu")
class_options = ["Ngẫu nhiên"] + list(FIGHTER_CLASSES.keys())
col1, col2 = st.columns(2)
with col1:
    selected_class_a = st.selectbox("Võ sĩ A:", class_options, key="class_a")
with col2:
    selected_class_b = st.selectbox("Võ sĩ B:", class_options, key="class_b")

st.markdown("### 2. Chọn phong cách thi đấu")
archetype_options = ["Ngẫu nhiên"] + list(FIGHTER_ARCHETYPES.keys())
col3, col4 = st.columns(2)
with col3:
    selected_archetype_a = st.selectbox(
        "Phong cách võ sĩ A:", archetype_options, key="archetype_a"
    )
    if selected_archetype_a != "Ngẫu nhiên":
        st.caption(FIGHTER_ARCHETYPES[selected_archetype_a].description)

with col4:
    selected_archetype_b = st.selectbox(
        "Phong cách võ sĩ B:", archetype_options, key="archetype_b"
    )
    if selected_archetype_b != "Ngẫu nhiên":
        st.caption(FIGHTER_ARCHETYPES[selected_archetype_b].description)

if st.button("🚀 Mô phỏng trận đấu"):
    class_a_name, class_b_name, archetype_a_name, archetype_b_name = (
        get_simulation_parameters(
            selected_class_a,
            selected_class_b,
            selected_archetype_a,
            selected_archetype_b,
        )
    )

    fight_result = run_fight_simulation(
        class_a_name, class_b_name, archetype_a_name, archetype_b_name, rounds
    )

    update_history(
        fight_result, class_a_name, class_b_name, archetype_a_name, archetype_b_name
    )

st.markdown("---")
st.markdown("## 📜 Lịch sử mô phỏng")
st.caption("Phân loại chênh lệch: ≤15 sát nút | 16-35 thuyết phục | 36-60 áp đảo | >60 outclass")

if not st.session_state.fight_history:
    st.info("Chưa có trận đấu nào được mô phỏng. Bấm nút 'Mô phỏng trận đấu' để bắt đầu!")
else:
    if st.button("🧹 Xóa lịch sử"):
        st.session_state.fight_history = []
        history_manager.save_history([])
        st.rerun()

    for i, entry in enumerate(st.session_state.fight_history):
        result = entry.fight_result
        diff = abs(result.score_a - result.score_b)
        summary = result.result_description.split("(")[0].strip()
        expander_title = (
            f"Trận #{len(st.session_state.fight_history) - i}: "
            f"{entry.class_a_name} vs {entry.class_b_name} | Δ {diff}"
        )
        with st.expander(expander_title, expanded=(i == 0)):
            display_fight_results(entry)