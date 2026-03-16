import random
from typing import Iterable

import altair as alt
import pandas as pd
import streamlit as st

from mma_sim.finish_method import FIGHTER_ARCHETYPES
from mma_sim.fighter_class import FIGHTER_CLASSES
from mma_sim.history_manager import load_history, save_history
from mma_sim.models import Fighter, FightResult, HistoryEntry, TickEvent
from mma_sim.simulation_engine import run_simulation as core_run_simulation

MAX_HISTORY_SIZE = 50
TICK_PER_ROUND = 6
SECONDS_PER_ROUND = 5 * 60

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
    (float("inf"), "Outclass hoàn toàn", "Đẳng cấp cách biệt rõ rệt.", "error"),
]
ALERT_RENDERERS = {
    "info": st.info,
    "success": st.success,
    "warning": st.warning,
    "error": st.error,
}


def _force_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


def ensure_history_loaded():
    if "fight_history" not in st.session_state:
        st.session_state.fight_history = load_history()


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


def to_tick_event(raw) -> TickEvent | None:
    if isinstance(raw, TickEvent):
        return raw
    if isinstance(raw, dict):
        raw_dict = {
            "round_number": raw.get("round_number", 0),
            "tick_index": raw.get("tick_index", 0),
            "phase": raw.get("phase", "unknown"),
            "actor": raw.get("actor"),
            "description": raw.get("description", ""),
            "impact": float(raw.get("impact", 0.0)),
        }
        return TickEvent(**raw_dict)
    if isinstance(raw, str):
        return TickEvent(
            round_number=0,
            tick_index=0,
            phase="log",
            actor=None,
            description=raw,
            impact=0.0,
        )
    return None


def event_dataframe(events: Iterable[TickEvent], fighter_a_name: str, fighter_b_name: str) -> pd.DataFrame:
    rows = []
    for event in events:
        if event.tick_index and TICK_PER_ROUND > 0:
            tick_offset = (event.tick_index - 1) / TICK_PER_ROUND * SECONDS_PER_ROUND
        else:
            tick_offset = 0
        absolute_seconds = (event.round_number - 1) * SECONDS_PER_ROUND + tick_offset
        actor_code = event.actor or "-"
        if actor_code == "A":
            actor_display = fighter_a_name
        elif actor_code == "B":
            actor_display = fighter_b_name
        else:
            actor_display = "-"
        rows.append(
            {
                "round": event.round_number,
                "tick": event.tick_index,
                "phase": event.phase,
                "actor": actor_code,
                "actor_display": actor_display,
                "description": event.description,
                "impact": event.impact,
                "seconds": absolute_seconds,
                "minutes": absolute_seconds / 60.0,
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "round",
                "tick",
                "phase",
                "actor",
                "actor_display",
                "description",
                "impact",
                "minutes",
            ]
        )
    return pd.DataFrame(rows)


def render_event_timeline(df: pd.DataFrame, fighter_a_name: str, fighter_b_name: str):
    if df.empty:
        st.info("Chưa có log chi tiết cho trận đấu này.")
        return

    base = alt.Chart(df)
    scatter = (
        base.mark_circle(size=85)
        .encode(
            x=alt.X("minutes", title="Phút (ước lượng)", scale=alt.Scale(zero=False)),
            y=alt.Y(
                "actor_display:N",
                title="Võ sĩ",
                sort=[fighter_a_name, fighter_b_name, "-"],
            ),
            color=alt.Color("phase:N", title="Pha"),
            tooltip=[
                alt.Tooltip("round:N", title="Hiệp"),
                alt.Tooltip("tick:N", title="Pha"),
                alt.Tooltip("phase:N", title="Trạng thái"),
                alt.Tooltip("actor_display:N", title="Người ra đòn"),
                alt.Tooltip("description:N", title="Mô tả"),
                alt.Tooltip("impact:Q", title="Impact"),
            ],
        )
    )
    st.altair_chart(scatter.interactive(), use_container_width=True)

    st.markdown("#### Timeline sự kiện")
    for _, row in df.sort_values(["round", "tick"]).iterrows():
        impact_txt = f" (impact {row['impact']:.2f})" if row["impact"] else ""
        st.write(
            f"• Hiệp {int(row['round'])}, pha {int(row['tick'])} "
            f"[{row['phase']}] {row['actor_display']}: {row['description']}{impact_txt}"
        )


def display_fight_results(entry: HistoryEntry):
    result = entry.fight_result
    diff = abs(result.score_a - result.score_b)

    st.subheader("Tổng kết trận đấu – Thang điểm 0-100")
    st.write(
        f"**Trận đấu:** `{entry.fighter_a_display}` "
        f"({entry.class_a_name} • {entry.archetype_a_name}) vs "
        f"`{entry.fighter_b_display}` ({entry.class_b_name} • {entry.archetype_b_name})"
    )
    st.write(f"**Điểm số:** `{result.score_a}` – `{result.score_b}` *(chênh {diff})*")
    st.caption("Điểm = Kỹ năng ngày đấu + phong độ trận đấu (thang 0-100+).")

    diff_summary = describe_diff(diff)
    if diff_summary:
        title, detail, style = diff_summary
        ALERT_RENDERERS[style](f"{title} (Δ {diff}) – {detail}")

    upset = detect_upset(entry, result, diff)
    if upset:
        st.warning(upset)

    st.success(f"**Kết quả:** {result.result_description}")
    st.write(f"**Kiểu kết thúc:** {result.finish_info.method_type} – {result.finish_info.description}")
    if result.score_a > result.score_b:
        st.write(f"**Tên người thắng:** {entry.fighter_a_display}")
    elif result.score_b > result.score_a:
        st.write(f"**Tên người thắng:** {entry.fighter_b_display}")
    else:
        st.write("**Tên người thắng:** Trận đấu kết thúc với kết quả hòa")
    st.write(
        f"**Thời điểm:** Hiệp {result.time_info.round}/{result.time_info.num_rounds} – "
        f"{result.time_info.minute}:{str(result.time_info.second).zfill(2)}"
    )
    st.caption(result.time_info.note)

    if result.round_summaries:
        st.markdown("#### Điểm từng hiệp (thang 10-point)")
        round_rows = []
        textual_summary_lines = []
        for summary in result.round_summaries:
            round_rows.append(
                {
                    "Hiệp": summary.round_number,
                    entry.fighter_a_display: summary.score_a,
                    entry.fighter_b_display: summary.score_b,
                    "Ghi chú": summary.note,
                }
            )
            textual_summary_lines.append(
                f"Hiệp {summary.round_number}: "
                f"{entry.fighter_a_display} {summary.score_a} – "
                f"{entry.fighter_b_display} {summary.score_b}. {summary.note}"
            )

        st.table(round_rows)
        if textual_summary_lines:
            st.markdown("".join(f"- {line}\n" for line in textual_summary_lines))

        events = [to_tick_event(raw) for summary in result.round_summaries for raw in summary.events]
        events = [event for event in events if event]
        show_timeline = st.checkbox("Hiển thị timeline chi tiết", value=False, key=f"timeline_{entry.entry_id}")
        if show_timeline:
            df = event_dataframe(events, entry.fighter_a_display, entry.fighter_b_display)
            render_event_timeline(df, entry.fighter_a_display, entry.fighter_b_display)


def get_simulation_parameters(selected_class_a: str, selected_class_b: str, selected_archetype_a: str, selected_archetype_b: str):
    class_a_name = selected_class_a if selected_class_a != "Ngẫu nhiên" else random.choice(list(FIGHTER_CLASSES.keys()))
    class_b_name = selected_class_b if selected_class_b != "Ngẫu nhiên" else random.choice(list(FIGHTER_CLASSES.keys()))
    archetype_a_name = selected_archetype_a if selected_archetype_a != "Ngẫu nhiên" else random.choice(list(FIGHTER_ARCHETYPES.keys()))
    archetype_b_name = selected_archetype_b if selected_archetype_b != "Ngẫu nhiên" else random.choice(list(FIGHTER_ARCHETYPES.keys()))
    return class_a_name, class_b_name, archetype_a_name, archetype_b_name


def run_fight_simulation(class_a_name: str, class_b_name: str, archetype_a_name: str, archetype_b_name: str, num_rounds: int) -> FightResult:
    fighter_a = Fighter(fighter_class=FIGHTER_CLASSES[class_a_name], archetype=FIGHTER_ARCHETYPES[archetype_a_name])
    fighter_b = Fighter(fighter_class=FIGHTER_CLASSES[class_b_name], archetype=FIGHTER_ARCHETYPES[archetype_b_name])
    return core_run_simulation(fighter_a, fighter_b, num_rounds)


def update_history(
    fight_result: FightResult,
    class_a_name: str,
    class_b_name: str,
    archetype_a_name: str,
    archetype_b_name: str,
    fighter_a_display: str,
    fighter_b_display: str,
):
    history_entry = HistoryEntry(
        fight_result=fight_result,
        class_a_name=class_a_name,
        class_b_name=class_b_name,
        archetype_a_name=archetype_a_name,
        archetype_b_name=archetype_b_name,
        fighter_a_display=fighter_a_display,
        fighter_b_display=fighter_b_display,
    )
    st.session_state.fight_history.insert(0, history_entry)
    st.session_state.fight_history = st.session_state.fight_history[:MAX_HISTORY_SIZE]
    save_history(st.session_state.fight_history)


def main():
    ensure_history_loaded()

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
        selected_archetype_a = st.selectbox("Phong cách võ sĩ A:", archetype_options, key="archetype_a")
        if selected_archetype_a != "Ngẫu nhiên":
            st.caption(FIGHTER_ARCHETYPES[selected_archetype_a].description)

    with col4:
        selected_archetype_b = st.selectbox("Phong cách võ sĩ B:", archetype_options, key="archetype_b")
        if selected_archetype_b != "Ngẫu nhiên":
            st.caption(FIGHTER_ARCHETYPES[selected_archetype_b].description)

    name_col1, name_col2 = st.columns(2)
    with name_col1:
        fighter_name_a_input = st.text_input(
            "Tên hiển thị võ sĩ A",
            value=st.session_state.get("fighter_display_name_a", "Võ sĩ A"),
            key="fighter_display_name_a",
        )
    with name_col2:
        fighter_name_b_input = st.text_input(
            "Tên hiển thị võ sĩ B",
            value=st.session_state.get("fighter_display_name_b", "Võ sĩ B"),
            key="fighter_display_name_b",
        )

    if st.button("🚀 Mô phỏng trận đấu"):
        class_a_name, class_b_name, archetype_a_name, archetype_b_name = get_simulation_parameters(
            selected_class_a, selected_class_b, selected_archetype_a, selected_archetype_b
        )
        fight_result = run_fight_simulation(class_a_name, class_b_name, archetype_a_name, archetype_b_name, rounds)
        display_name_a = fighter_name_a_input.strip() or class_a_name
        display_name_b = fighter_name_b_input.strip() or class_b_name
        update_history(
            fight_result,
            class_a_name,
            class_b_name,
            archetype_a_name,
            archetype_b_name,
            display_name_a,
            display_name_b,
        )

    st.markdown("---")
    st.markdown("## 📜 Lịch sử mô phỏng")
    st.caption("Phân loại chênh lệch: ≤15 sát nút | 16-35 thuyết phục | 36-60 áp đảo | >60 outclass")

    if not st.session_state.fight_history:
        st.info("Chưa có trận đấu nào được mô phỏng. Bấm nút 'Mô phỏng trận đấu' để bắt đầu!")
        return

    with st.expander("Quản lý lịch sử"):
        total_entries = len(st.session_state.fight_history)

        def _history_label(idx: int) -> str:
            entry = st.session_state.fight_history[idx]
            return (
                f"#{total_entries - idx}: "
                f"{entry.fighter_a_display} vs {entry.fighter_b_display} "
                f"({entry.fight_result.score_a}-{entry.fight_result.score_b})"
            )

        selectable_indices = list(range(total_entries))
        selected_indices = st.multiselect(
            "Chọn các trận muốn xóa",
            options=selectable_indices,
            format_func=_history_label,
        )

        col_delete_selected, col_delete_all = st.columns(2)
        with col_delete_selected:
            if st.button("Xóa các trận đã chọn") and selected_indices:
                remaining_history = [
                    entry
                    for idx, entry in enumerate(st.session_state.fight_history)
                    if idx not in selected_indices
                ]
                st.session_state.fight_history = remaining_history
                save_history(remaining_history)
                _force_rerun()
        with col_delete_all:
            if st.button("Xóa toàn bộ lịch sử"):
                st.session_state.fight_history = []
                save_history([])
                _force_rerun()

    for i, entry in enumerate(st.session_state.fight_history):
        result = entry.fight_result
        diff = abs(result.score_a - result.score_b)
        summary = result.result_description.split("(")[0].strip()
        expander_title = (
            f"Trận #{len(st.session_state.fight_history) - i}: "
            f"{entry.class_a_name} vs {entry.class_b_name} | Δ {diff} – {summary}"
        )
        with st.expander(expander_title, expanded=(i == 0)):
            display_fight_results(entry)


if __name__ == "__main__":
    main()
