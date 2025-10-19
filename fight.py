import random
from typing import Literal, Optional

from battle_result import analyze_battle_result_expanded
from finish_method import get_dynamic_finish_method
from fight_time import generate_dynamic_fight_time
import config
from models import (
    Fighter,
    FightResult,
    FinishInfo,
    RoundSummary,
    TimeInfo,
    FighterAttributes,
    TickEvent,
)


class Fight:
    """Đại diện cho một trận đấu MMA và bao bọc toàn bộ logic mô phỏng."""

    def __init__(self, fighter_a: Fighter, fighter_b: Fighter, num_rounds: int):
        self.fighter_a = fighter_a
        self.fighter_b = fighter_b
        self.num_rounds = num_rounds
        self.result: Optional[FightResult] = None
        self.attributes_a = self._build_attributes(self.fighter_a)
        self.attributes_b = self._build_attributes(self.fighter_b)
        self.class_skill_a = self.fighter_a.generate_skill_point()
        self.class_skill_b = self.fighter_b.generate_skill_point()
        perf_min, perf_max = config.PERFORMANCE_FACTOR_RANGE
        self.performance_a = random.randint(perf_min, perf_max)
        self.performance_b = random.randint(perf_min, perf_max)
        total_ticks = max(1, self.num_rounds * 6)
        skill_weight = getattr(config, "CLASS_SKILL_ADVANTAGE_WEIGHT", 0.0)
        performance_weight = getattr(config, "PERFORMANCE_ADVANTAGE_WEIGHT", 0.0)
        self._class_skill_bonus = (
            (self.class_skill_a - self.class_skill_b) * skill_weight / total_ticks
        )
        self._performance_bonus = (
            (self.performance_a - self.performance_b) * performance_weight / total_ticks
        )

    def simulate(self):
        round_summaries, score_a, score_b, forced_finish, forced_time = self._simulate_rounds()

        score_diff = abs(score_a - score_b)

        if forced_finish:
            finish = forced_finish
            time_info = forced_time
        elif score_a == score_b:
            if getattr(config, "ALLOW_TIE_BREAK_DECISION", False):
                bias_scale = getattr(config, "TIE_BREAK_DECISION_BIAS", 0.0)
                score_delta = getattr(config, "TIE_BREAK_DECISION_SCORE_DELTA", 1)
                advantage = (self.class_skill_a - self.class_skill_b) + (self.performance_a - self.performance_b)
                prob_a = 0.5 + advantage * bias_scale
                prob_a = max(0.05, min(0.95, prob_a))
                winner_side = "A" if random.random() < prob_a else "B"
                if winner_side == "A":
                    score_a = min(100, score_a + score_delta)
                    winner = self.fighter_a
                else:
                    score_b = min(100, score_b + score_delta)
                    winner = self.fighter_b
                score_diff = abs(score_a - score_b)
                finish = get_dynamic_finish_method(winner.archetype.name, max(1, score_diff))
                finish = self._normalize_scorecard_finish(finish, score_diff, winner)
                time_info = TimeInfo(
                    num_rounds=self.num_rounds,
                    round=self.num_rounds,
                    minute=5,
                    second=0,
                    note="Giám khảo ra quyết định tách sau khi điểm số bằng nhau.",
                )
            else:
                finish = FinishInfo(
                    archetype_name="Không có",
                    archetype_description="Trận đấu kết thúc với tỉ số hòa.",
                    description=random.choice(config.FINISH_METHODS["DRAW"]),
                    method_type="DRAW",
                )
                time_info = generate_dynamic_fight_time("DRAW", self.num_rounds)
        else:
            winner = self.fighter_a if score_a > score_b else self.fighter_b
            winner_archetype_name = winner.archetype.name
            finish = get_dynamic_finish_method(winner_archetype_name, score_diff)
            finish = self._normalize_scorecard_finish(finish, score_diff, winner)
            time_info = TimeInfo(
                num_rounds=self.num_rounds,
                round=self.num_rounds,
                minute=5,
                second=0,
                note="Kết thúc bằng quyết định của giám khảo sau đủ số hiệp.",
            )

        result_description = analyze_battle_result_expanded(score_a, score_b)

        self.result = FightResult(
            score_a=score_a,
            score_b=score_b,
            result_description=result_description,
            finish_info=finish,
            time_info=time_info,
            round_summaries=round_summaries,
        )

    def _normalize_scorecard_finish(self, finish: FinishInfo, score_diff: int, winner: Fighter) -> FinishInfo:
        """Ensure scorecard-based outcomes map to reasonable finish types."""
        allowed_types = {"KO", "TKO", "SUB"}
        if finish.method_type not in allowed_types:
            return finish

        allow_stoppage = getattr(config, "ALLOW_SCORECARD_STOPPAGES", False)
        diff_threshold = getattr(config, "SCORECARD_STOPPAGE_DIFF_THRESHOLD", None)
        if allow_stoppage and diff_threshold is not None and score_diff >= diff_threshold:
            return finish

        base_prob = getattr(config, "SCORECARD_STOPPAGE_BASE_PROB", 0.0)
        per_point = getattr(config, "SCORECARD_STOPPAGE_PER_POINT", 0.0)
        if allow_stoppage and (base_prob > 0.0 or per_point > 0.0):
            probability = base_prob + max(0.0, score_diff) * per_point
            probability *= self._finish_probability_scale(winner.archetype)
            probability = max(0.0, min(1.0, probability))
            if random.random() < probability:
                return finish

        description = random.choice(config.FINISH_METHODS["DEC"])
        return FinishInfo(
            archetype_name=finish.archetype_name,
            archetype_description=finish.archetype_description,
            description=description,
            method_type="DEC",
        )

    def _finish_probability_scale(self, archetype) -> float:
        weights = getattr(archetype, "weights", {}) or {}
        total = sum(weights.values()) or 1.0
        decision_share = weights.get("DEC", 0) / total
        influence = getattr(config, "FINISH_DECISION_WEIGHT_INFLUENCE", 0.0)
        min_scale = getattr(config, "FINISH_MIN_PROB_SCALE", 0.0)
        max_scale = getattr(config, "FINISH_MAX_PROB_SCALE", None)
        scale = 1.0 + decision_share * influence
        if max_scale is not None:
            scale = min(max_scale, scale)
        if min_scale:
            scale = max(min_scale, scale)
        return max(0.0, scale)

    def _pick_dominance_finish_hint(self, winner: Fighter, last_phase: Optional[str]) -> str:
        """Select a finish hint for dominance-based stoppages."""
        weights = getattr(winner.archetype, "weights", {}) or {}
        method_weights = {
            "KO": weights.get("KO", 0),
            "TKO": weights.get("TKO", 0),
            "SUB": weights.get("SUB", 0),
        }

        if last_phase == "ground" and method_weights.get("SUB", 0) > 0:
            return "SUB"
        if last_phase == "standup":
            if method_weights.get("KO", 0) >= method_weights.get("TKO", 0):
                return "KO"
            if method_weights.get("TKO", 0) > 0:
                return "TKO"
        if last_phase == "clinch" and method_weights.get("TKO", 0) > 0:
            return "TKO"

        preferred = max(method_weights, key=lambda key: method_weights[key], default="TKO")
        return preferred if method_weights.get(preferred, 0) else "TKO"

    # ------------------------------------------------------------------
    # Thuộc tính & tiện ích
    # ------------------------------------------------------------------
    def _build_attributes(self, fighter: Fighter) -> FighterAttributes:
        baseline = config.ATTRIBUTE_BASELINES.get(
            fighter.fighter_class.name,
            config.ATTRIBUTE_BASELINES["Kỳ cựu (Veteran)"],
        ).copy()

        modifier = config.ATTRIBUTE_ARCHETYPE_MODIFIERS.get(fighter.archetype.name)
        if modifier is None:
            modifier = {}
            for key, value in config.ATTRIBUTE_ARCHETYPE_MODIFIERS.items():
                if key in fighter.archetype.name:
                    modifier = value
                    break

        base_values = baseline.copy()
        modifier_scale = getattr(config, "ATTRIBUTE_MODIFIER_SCALE", 1.0)
        for stat, delta in modifier.items():
            if stat in baseline:
                baseline[stat] += delta * modifier_scale

        for stat in baseline:
            baseline[stat] += random.randint(*config.ATTRIBUTE_NOISE_RANGE)
            baseline[stat] = max(
                config.ATTRIBUTE_MIN,
                min(config.ATTRIBUTE_MAX, baseline[stat]),
            )

        delta_clamp = getattr(config, "ATTRIBUTE_DELTA_CLAMP", None)
        if delta_clamp is not None:
            for stat in baseline:
                delta = baseline[stat] - base_values[stat]
                if delta > delta_clamp:
                    baseline[stat] = base_values[stat] + delta_clamp
                elif delta < -delta_clamp:
                    baseline[stat] = base_values[stat] - delta_clamp

        blend_weight = getattr(config, "ATTRIBUTE_BASELINE_BLEND", 0.0)
        if blend_weight:
            for stat in baseline:
                baseline[stat] = (
                    base_values[stat] * blend_weight
                    + baseline[stat] * (1 - blend_weight)
                )

        for stat in baseline:
            baseline[stat] = int(round(baseline[stat]))

        return FighterAttributes(**baseline)

    def _offensive_rating(self, attrs: FighterAttributes) -> float:
        standup = attrs.striking * 0.6 + attrs.clinch * 0.2 + attrs.fight_iq * 0.2
        ground = attrs.grappling * 0.45 + attrs.submission * 0.35 + attrs.fight_iq * 0.2
        return standup * 0.6 + ground * 0.4

    def _resilience_rating(self, attrs: FighterAttributes) -> float:
        return attrs.durability * 0.55 + attrs.cardio * 0.3 + attrs.fight_iq * 0.15

    def _stamina_cost(self, attrs: FighterAttributes, base_cost: float) -> float:
        modifier = max(0.0, (110 - attrs.cardio) / 160)
        return base_cost * (1 + modifier)

    # ------------------------------------------------------------------
    # Mô phỏng trận đấu
    # ------------------------------------------------------------------
    def _simulate_rounds(
        self,
    ) -> tuple[list[RoundSummary], int, int, Optional[FinishInfo], Optional[TimeInfo]]:
        total_points_a = 0
        total_points_b = 0
        round_summaries: list[RoundSummary] = []
        finish_override: Optional[FinishInfo] = None
        finish_time_override: Optional[TimeInfo] = None

        stamina_a = 1.0
        stamina_b = 1.0
        health_a = 100.0
        health_b = 100.0

        for round_number in range(1, self.num_rounds + 1):
            outcome = self._simulate_single_round(
                round_number=round_number,
                attrs_a=self.attributes_a,
                attrs_b=self.attributes_b,
                stamina_a=stamina_a,
                stamina_b=stamina_b,
                health_a=health_a,
                health_b=health_b,
                cumulative_points_a=total_points_a,
                cumulative_points_b=total_points_b,
            )

            summary = outcome["summary"]
            round_summaries.append(summary)
            total_points_a += summary.score_a
            total_points_b += summary.score_b

            stamina_a = outcome["stamina_a"]
            stamina_b = outcome["stamina_b"]
            health_a = outcome["health_a"]
            health_b = outcome["health_b"]

            if outcome["finish"]:
                winner_side: Literal["A", "B"] = outcome["winner"]
                bonus_points = outcome["finish_bonus_points"]
                if winner_side == "A":
                    total_points_a += bonus_points
                    round_summaries[-1].score_a += bonus_points
                else:
                    total_points_b += bonus_points
                    round_summaries[-1].score_b += bonus_points

                finish_override = outcome["finish_info"]
                finish_time_override = outcome["finish_time"]
                break

        completed_rounds = max(1, len(round_summaries))
        max_points = completed_rounds * 10
        score_a = int(round(min(1.0, total_points_a / max_points) * 100))
        score_b = int(round(min(1.0, total_points_b / max_points) * 100))

        return round_summaries, score_a, score_b, finish_override, finish_time_override

    def _simulate_single_round(
        self,
        round_number: int,
        attrs_a: FighterAttributes,
        attrs_b: FighterAttributes,
        stamina_a: float,
        stamina_b: float,
        health_a: float,
        health_b: float,
        cumulative_points_a: int,
        cumulative_points_b: int,
    ) -> dict:
        resilience_a = self._resilience_rating(attrs_a)
        resilience_b = self._resilience_rating(attrs_b)

        tick_count = 6
        tick_points_a = 0
        tick_points_b = 0
        control_a = 0.0
        control_b = 0.0
        stamina_current_a = stamina_a
        stamina_current_b = stamina_b
        health_current_a = health_a
        health_current_b = health_b
        finish_trigger = False
        finish_info = None
        finish_time = None
        finish_bonus_points = 0
        winner_side: Optional[Literal["A", "B"]] = None
        finish_hint: Optional[str] = None
        tick_events: list[TickEvent] = []
        last_phase: Optional[str] = None
        dominance_finish_note: Optional[str] = None

        for tick_index in range(1, tick_count + 1):
            phase = self._choose_phase(attrs_a, attrs_b, last_phase)
            tick_result = self._simulate_tick(
                round_number=round_number,
                tick_index=tick_index,
                phase=phase,
                attrs_a=attrs_a,
                attrs_b=attrs_b,
                stamina_a=stamina_current_a,
                stamina_b=stamina_current_b,
                health_a=health_current_a,
                health_b=health_current_b,
            )

            tick_points_a += tick_result["points_a"]
            tick_points_b += tick_result["points_b"]
            control_a += tick_result["control_a"]
            control_b += tick_result["control_b"]
            health_current_a = max(0.0, health_current_a - tick_result["damage_a"])
            health_current_b = max(0.0, health_current_b - tick_result["damage_b"])
            tick_events.extend(tick_result["events"])

            stamina_current_a = max(
                0.2,
                stamina_current_a - self._stamina_cost(attrs_a, tick_result["stamina_cost_a"]),
            )
            stamina_current_b = max(
                0.2,
                stamina_current_b - self._stamina_cost(attrs_b, tick_result["stamina_cost_b"]),
            )

            if tick_result["finish"]:
                finish_trigger = True
                winner_side = tick_result["winner"]
                finish_hint = tick_result["finish_hint"]
                finish_bonus_points = 4
                minute = min(4, (tick_index - 1) // 2)
                second = random.randint(0, 59)
                finish_time = TimeInfo(
                    num_rounds=self.num_rounds,
                    round=round_number,
                    minute=minute,
                    second=second,
                    note=f"Kết thúc ở hiệp {round_number}, phút {minute}:{str(second).zfill(2)}.",
                )
                break

            last_phase = phase

        dominance = tick_points_a - tick_points_b + (control_a - control_b) * 0.6

        if not finish_trigger:
            dominance_threshold = getattr(config, "DOMINANCE_FINISH_THRESHOLD", None)
            if dominance_threshold:
                dominance_margin = abs(dominance)
                if dominance_margin >= dominance_threshold:
                    base_prob = getattr(config, "DOMINANCE_FINISH_BASE_PROB", 0.0)
                    per_point_prob = getattr(config, "DOMINANCE_FINISH_PER_POINT", 0.0)
                    max_prob = getattr(config, "DOMINANCE_FINISH_MAX_PROB", 1.0)
                    finish_prob = base_prob + max(0.0, dominance_margin - dominance_threshold) * per_point_prob

                    if finish_prob > 0.0:
                        candidate_side = "A" if dominance > 0 else "B"
                        candidate_fighter = self.fighter_a if candidate_side == "A" else self.fighter_b
                        if last_phase == "ground":
                            sub_bonus = getattr(config, "DOMINANCE_SUB_FINISH_BONUS", 0.0)
                            if sub_bonus:
                                submission_weight = candidate_fighter.archetype.weights.get("SUB", 0)
                                finish_prob += sub_bonus * max(0, submission_weight) / 100.0

                        finish_prob *= self._finish_probability_scale(candidate_fighter.archetype)
                        finish_prob = min(max_prob, max(0.0, finish_prob))

                        if random.random() < finish_prob:
                            finish_trigger = True
                            winner_side = candidate_side
                            finish_hint = self._pick_dominance_finish_hint(candidate_fighter, last_phase)
                            finish_bonus_points = 4
                            dominance_finish_note = " Trận đấu bị dừng do áp đảo rõ rệt."
                            if finish_time is None:
                                finish_time = TimeInfo(
                                    num_rounds=self.num_rounds,
                                    round=round_number,
                                    minute=4,
                                    second=59,
                                    note=f"Kết thúc áp đảo ở hiệp {round_number}, trọng tài dừng trận sau tiếng chuông.",
                                )

        if dominance >= 6:
            points_a, points_b = 10, 8
            winner_side = winner_side or "A"
            note = "Võ sĩ A áp đảo hoàn toàn và gây sát thương lớn."
        elif dominance <= -6:
            points_a, points_b = 8, 10
            winner_side = winner_side or "B"
            note = "Võ sĩ B áp đảo hoàn toàn và gây sát thương lớn."
        elif dominance >= 2:
            points_a, points_b = 10, 9
            winner_side = winner_side or "A"
            note = "Võ sĩ A nhỉnh hơn trong các pha tranh chấp."
        elif dominance <= -2:
            points_a, points_b = 9, 10
            winner_side = winner_side or "B"
            note = "Võ sĩ B nhỉnh hơn trong các pha tranh chấp."
        else:
            points_a, points_b = 10, 10
            note = "Hiệp đấu cân bằng, hai bên trả đòn qua lại."

        if dominance_finish_note:
            note += dominance_finish_note

        round_summary = RoundSummary(
            round_number=round_number,
            score_a=points_a,
            score_b=points_b,
            note=note,
            events=tick_events,
        )

        if not finish_trigger:
            if health_current_a <= 0 and health_current_b > health_current_a + 3:
                finish_trigger = True
                winner_side = "B"
                finish_hint = "TKO"
                finish_bonus_points = 4
            elif health_current_b <= 0 and health_current_a > health_current_b + 3:
                finish_trigger = True
                winner_side = "A"
                finish_hint = "TKO"
                finish_bonus_points = 4

        if finish_trigger and winner_side:
            winner_fighter = self.fighter_a if winner_side == "A" else self.fighter_b
            projected_a = cumulative_points_a + points_a + (finish_bonus_points if winner_side == "A" else 0)
            projected_b = cumulative_points_b + points_b + (finish_bonus_points if winner_side == "B" else 0)
            projected_score_diff = max(1, abs(projected_a - projected_b) * 2)
            finish_info = get_dynamic_finish_method(
                winner_fighter.archetype.name,
                projected_score_diff,
            )
            if finish_hint:
                specific_finish = random.choice(config.FINISH_METHODS.get(finish_hint, ["Finish"]))
                description = (
                    specific_finish
                    if finish_hint in {"DEC", "DQ", "NC", "DRAW"}
                    else f"{finish_hint} – {specific_finish}"
                )
                finish_info = FinishInfo(
                    archetype_name=winner_fighter.archetype.name,
                    archetype_description=winner_fighter.archetype.description,
                    description=description,
                    method_type=finish_hint,
                )
            round_summary.note += " Kết liễu trận đấu ngay hiệp này."
            if finish_time is None:
                finish_time = TimeInfo(
                    num_rounds=self.num_rounds,
                    round=round_number,
                    minute=4,
                    second=59,
                    note=f"Kết thúc ở hiệp {round_number}, sau tiếng chuông.",
                )

        return {
            "summary": round_summary,
            "finish": finish_trigger,
            "winner": winner_side,
            "finish_info": finish_info,
            "finish_time": finish_time,
            "finish_bonus_points": finish_bonus_points,
            "stamina_a": stamina_current_a,
            "stamina_b": stamina_current_b,
            "health_a": health_current_a,
            "health_b": health_current_b,
        }

    def _choose_phase(
        self,
        attrs_a: FighterAttributes,
        attrs_b: FighterAttributes,
        last_phase: Optional[str],
    ) -> str:
        weights = {
            "standup": attrs_a.striking + attrs_b.striking,
            "clinch": attrs_a.clinch + attrs_b.clinch,
            "ground": attrs_a.grappling + attrs_b.grappling,
        }
        if last_phase == "ground":
            weights["ground"] *= 0.85
        total = sum(weights.values())
        choices = list(weights.keys())
        probs = [weights[key] / total for key in choices]
        return random.choices(choices, weights=probs, k=1)[0]

    def _simulate_tick(
        self,
        round_number: int,
        tick_index: int,
        phase: str,
        attrs_a: FighterAttributes,
        attrs_b: FighterAttributes,
        stamina_a: float,
        stamina_b: float,
        health_a: float,
        health_b: float,
    ) -> dict:
        events: list[TickEvent] = []
        points_a = points_b = 0
        control_a = control_b = 0.0
        damage_a = damage_b = 0.0
        stamina_cost_a = stamina_cost_b = 0.05
        winner_side: Optional[Literal["A", "B"]] = None
        finish = False
        finish_hint: Optional[str] = None

        if phase == "standup":
            attack_a = attrs_a.striking * stamina_a
            attack_b = attrs_b.striking * stamina_b
            defense_a = attrs_a.durability * 0.45 + attrs_a.fight_iq * 0.25
            defense_b = attrs_b.durability * 0.45 + attrs_b.fight_iq * 0.25
            damage_multiplier = 0.15
            finish_hint = "KO"
        elif phase == "clinch":
            attack_a = (attrs_a.clinch * 0.7 + attrs_a.striking * 0.3) * stamina_a
            attack_b = (attrs_b.clinch * 0.7 + attrs_b.striking * 0.3) * stamina_b
            defense_a = attrs_a.durability * 0.5 + attrs_a.fight_iq * 0.2
            defense_b = attrs_b.durability * 0.5 + attrs_b.fight_iq * 0.2
            damage_multiplier = 0.15
            finish_hint = "TKO"
        else:  # ground
            attack_a = (attrs_a.grappling * 0.6 + attrs_a.submission * 0.4) * stamina_a
            attack_b = (attrs_b.grappling * 0.6 + attrs_b.submission * 0.4) * stamina_b
            defense_a = attrs_a.grappling * 0.45 + attrs_a.durability * 0.25 + attrs_a.fight_iq * 0.2
            defense_b = attrs_b.grappling * 0.45 + attrs_b.durability * 0.25 + attrs_b.fight_iq * 0.2
            damage_multiplier = 0.15
            finish_hint = "SUB"

        noise = random.uniform(-5, 5)
        advantage = (attack_a - defense_b) - (attack_b - defense_a) + noise
        advantage += self._class_skill_bonus + self._performance_bonus

        if advantage >= 8:
            points_a += 2
            control_a += 1.1
            dmg = max(0.0, advantage - 6) * damage_multiplier
            damage_b += dmg
            events.append(
                TickEvent(
                    round_number=round_number,
                    tick_index=tick_index,
                    phase=phase,
                    actor="A",
                    description="Võ sĩ A tung chuỗi đòn uy lực khiến đối thủ lảo đảo.",
                    impact=dmg,
                )
            )
            winner_side = "A"
            stamina_cost_a += 0.02
        elif advantage <= -8:
            points_b += 2
            control_b += 1.1
            dmg = max(0.0, -advantage - 6) * damage_multiplier
            damage_a += dmg
            events.append(
                TickEvent(
                    round_number=round_number,
                    tick_index=tick_index,
                    phase=phase,
                    actor="B",
                    description="Võ sĩ B áp đảo và gây sát thương nặng.",
                    impact=dmg,
                )
            )
            winner_side = "B"
            stamina_cost_b += 0.02
        elif advantage >= 3:
            points_a += 1
            control_a += 0.7
            dmg = max(0.0, advantage - 2) * damage_multiplier * 0.6
            damage_b += dmg
            events.append(
                TickEvent(
                    round_number=round_number,
                    tick_index=tick_index,
                    phase=phase,
                    actor="A",
                    description="Võ sĩ A ghi điểm với đòn đánh chính xác.",
                    impact=dmg,
                )
            )
            winner_side = "A"
        elif advantage <= -3:
            points_b += 1
            control_b += 0.7
            dmg = max(0.0, -advantage - 2) * damage_multiplier * 0.6
            damage_a += dmg
            events.append(
                TickEvent(
                    round_number=round_number,
                    tick_index=tick_index,
                    phase=phase,
                    actor="B",
                    description="Võ sĩ B ghi điểm với đòn phản công chuẩn xác.",
                    impact=dmg,
                )
            )
            winner_side = "B"
        else:
            control_a += 0.3
            control_b += 0.3
            events.append(
                TickEvent(
                    round_number=round_number,
                    tick_index=tick_index,
                    phase=phase,
                    actor=None,
                    description="Hai bên giằng co, chưa bên nào tạo được lợi thế rõ rệt.",
                    impact=0.0,
                )
            )

        finish_attempted = False
        if winner_side == "A":
            target_health = health_b
            stamina_cost_a += 0.01
            margin = max(0.0, advantage)
            health_ratio = target_health / 100
            if margin >= 24 and health_ratio < 0.08:
                finish_attempted = True
                margin_factor = margin / 130
                damage_factor = damage_b / 600
                fatigue_factor = max(0.0, 1 - stamina_b) * 0.07
                health_factor = max(0.0, (0.06 - health_ratio)) * 0.25
                finish_chance = 0.00002 + margin_factor + damage_factor + fatigue_factor + health_factor
                if health_ratio < 0.03:
                    finish_chance += 0.0015
                finish_chance = min(0.0025, finish_chance)
                if random.random() < finish_chance:
                    finish = True
                    finish_hint = finish_hint or "TKO"
        elif winner_side == "B":
            target_health = health_a
            stamina_cost_b += 0.01
            margin = max(0.0, -advantage)
            health_ratio = target_health / 100
            if margin >= 24 and health_ratio < 0.08:
                finish_attempted = True
                margin_factor = margin / 130
                damage_factor = damage_a / 600
                fatigue_factor = max(0.0, 1 - stamina_a) * 0.07
                health_factor = max(0.0, (0.06 - health_ratio)) * 0.25
                finish_chance = 0.00002 + margin_factor + damage_factor + fatigue_factor + health_factor
                if health_ratio < 0.03:
                    finish_chance += 0.0015
                finish_chance = min(0.0025, finish_chance)
                if random.random() < finish_chance:
                    finish = True
                    finish_hint = finish_hint or "TKO"

        # Submission-specific bonus
        if finish_attempted and phase == "ground" and winner_side == "A" and attrs_a.submission > attrs_a.striking:
            finish_hint = "SUB"
        elif finish_attempted and phase == "ground" and winner_side == "B" and attrs_b.submission > attrs_b.striking:
            finish_hint = "SUB"

        return {
            "points_a": points_a,
            "points_b": points_b,
            "control_a": control_a,
            "control_b": control_b,
            "damage_a": damage_a,
            "damage_b": damage_b,
            "stamina_cost_a": stamina_cost_a,
            "stamina_cost_b": stamina_cost_b,
            "events": events,
            "finish": finish,
            "winner": winner_side,
            "finish_hint": finish_hint,
        }
