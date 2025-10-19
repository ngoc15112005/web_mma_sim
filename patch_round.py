from pathlib import Path
path = Path("fight.py")
text = path.read_text(encoding="utf-8")
old = "            if tick_result[\"finish\"]:\n                finish_trigger = True\n                winner_side = tick_result[\"winner\"]\n                finish_hint = tick_result[\"finish_hint\"]\n                finish_bonus_points = 4\n                minute = min(4, (tick_index - 1) // 2)\n                second = random.randint(0, 59)\n                finish_time = TimeInfo(\n                    num_rounds=self.num_rounds,\n                    round=round_number,\n                    minute=minute,\n                    second=second,\n                    note=f\"Kt th1c  hib {round_number}, pht {minute}:{str(second).zfill(2)}.\",\n                )\n                break\n"\

new = "            if tick_result[\"finish\"]:\n                finish_trigger = True\n                winner_side = tick_result[\"winner\"]\n                finish_hint = tick_result[\"finish_hint\"]\n                finish_bonus_points = 4\n                finish_time = self._make_time_info(round_number, tick_index)\n                break\n"\

if old not in text:
    raise SystemExit("finish block not found")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
