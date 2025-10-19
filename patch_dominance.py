from pathlib import Path
path = Path("fight.py")
text = path.read_text(encoding="utf-8")
old = "                            finish_bonus_points = 4\n                            dominance_finish_note = \" Tr3- n d?u b d?ng do Ap 3- o r? r?t.\"\n                            if finish_time is None:\n                                finish_time = TimeInfo(\n                                    num_rounds=self.num_rounds,\n                                    round=round_number,\n                                    minute=4,\n                                    second=59,\n                                    note=f\"K?t thc Ap 3- o  hi?p {round_number}, tr?ng t?i d?ng tr?n sau ti?ng chu?ng.\",\n                                )\n"\

new = "                            finish_bonus_points = 4\n                            dominance_finish_note = \" Tr3- n d?u b d?ng do Ap 3- o r? r?t.\"\n                            if finish_time is None:\n                                reference_tick = last_tick_index or tick_count\n                                finish_time = self._make_time_info(\n                                    round_number,\n                                    reference_tick,\n                                    near_end=True,\n                                    note_template=\"Kt th4p ?o  hib {round}, tr?ng t?i d?ng tr?n l?c {minute}:{second}.\"\n                                )\n"\

if old not in text:
    raise SystemExit("dominance block not found")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
