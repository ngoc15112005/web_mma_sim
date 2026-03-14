import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from .models import FinishInfo, FightResult, HistoryEntry, RoundSummary, TickEvent, TimeInfo

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE_PATH = DATA_DIR / "fight_history.json"


def save_history(history: List[HistoryEntry]):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        history_as_dicts = [asdict(entry) for entry in history]
        HISTORY_FILE_PATH.write_text(
            json.dumps(history_as_dicts, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )
    except IOError as e:
        print(f"Lỗi khi lưu lịch sử: {e}")


def load_history() -> List[HistoryEntry]:
    if not HISTORY_FILE_PATH.exists():
        return []

    try:
        history_as_dicts = json.loads(HISTORY_FILE_PATH.read_text(encoding="utf-8"))

        reconstructed_history = []
        for entry_dict in history_as_dicts:
            fr_dict = entry_dict["fight_result"]
            finish_info = FinishInfo(**fr_dict["finish_info"])
            time_info = TimeInfo(**fr_dict["time_info"])
            round_summaries_data = fr_dict.get("round_summaries", [])
            round_summaries = []
            for summary in round_summaries_data:
                tick_events = summary.get("events", [])
                parsed_events = []
                for event in tick_events:
                    if isinstance(event, dict) and all(
                        key in event for key in ["round_number", "tick_index", "phase", "description"]
                    ):
                        parsed_events.append(TickEvent(**event))
                    elif isinstance(event, str):
                        parsed_events.append(
                            TickEvent(
                                round_number=summary.get("round_number", 0),
                                tick_index=0,
                                phase="standup",
                                actor=None,
                                description=event,
                                impact=0.0,
                            )
                        )
                summary_payload = {k: v for k, v in summary.items() if k != "events"}
                round_summaries.append(RoundSummary(events=parsed_events, **summary_payload))

            fight_result_payload = {k: v for k, v in fr_dict.items() if k not in {"finish_info", "time_info", "round_summaries"}}
            fight_result = FightResult(finish_info=finish_info, time_info=time_info, round_summaries=round_summaries, **fight_result_payload)

            history_entry_data = {k: v for k, v in entry_dict.items() if k != "fight_result"}
            history_entry_data["fight_result"] = fight_result
            history_entry_data.setdefault("archetype_a_name", "Không rõ")
            history_entry_data.setdefault("archetype_b_name", "Không rõ")
            history_entry_data.setdefault("fighter_a_display", history_entry_data.get("class_a_name", "Võ sĩ A"))
            history_entry_data.setdefault("fighter_b_display", history_entry_data.get("class_b_name", "Võ sĩ B"))

            history_entry = HistoryEntry(**history_entry_data)
            reconstructed_history.append(history_entry)

        return reconstructed_history
    except (IOError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Lỗi khi tải lịch sử (file có thể hỏng), bắt đầu với lịch sử trống: {e}")
        return []
