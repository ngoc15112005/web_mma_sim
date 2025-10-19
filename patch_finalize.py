from pathlib import Path
path = Path("fight.py")
text = path.read_text(encoding="utf-8")
old = "            round_summary.note += \" K3- t li5. tr?n u ngay hi?p n?y.\"\n            if finish_time is None:\n                finish_time = TimeInfo(\n                    num_rounds=self.num_rounds,\n                    round=round_number,\n                    minute=4,\n                    second=59,\n                    note=f\"K3- t th4c  hib {round_number}, sau ti?ng chu?ng.\",\n                )\n"\

new = "            round_summary.note += \" K3- t li5. tr?n u ngay hi?p n?y.\"\n            if finish_time is None:\n                reference_tick = last_tick_index or tick_count\n                finish_time = self._make_time_info(\n                    round_number,\n                    reference_tick,\n                    near_end=True,\n                    note_template=\"K3- t th4c  hib {round}, sau ti?ng chu?ng.\"\n                )\n"\

if old not in text:
    raise SystemExit("final block not found")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
