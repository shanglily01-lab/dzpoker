"""
AI决策引擎 - 为AI玩家做出智能决策

根据玩家类型、手牌强度、位置、底池赔率等因素
自动决定弃牌、过牌、跟注、加注或All-in
"""

import random
from typing import Dict, List, Optional, Tuple
from ..core.poker import Card


class AIDecisionMaker:
    """AI决策制定者"""

    def __init__(self):
        pass

    def evaluate_hand_strength(
        self,
        hole_cards: List[Card],
        community_cards: List[Card]
    ) -> float:
        """
        评估手牌强度 (0.0 - 1.0)

        简化版评估：
        - 基于高牌、对子、顺子听牌、同花听牌等
        """
        if not hole_cards or len(hole_cards) != 2:
            return 0.0

        score = 0.0
        card1, card2 = hole_cards

        # 使用 value (2-14) 进行统一比较
        val1, val2 = card1.value, card2.value

        # 1. 底牌对子
        if val1 == val2:
            if val1 >= 11:  # JJ, QQ, KK, AA (11-14)
                score += 0.8
            elif val1 >= 7:  # 77-TT (7-10)
                score += 0.6
            else:  # 22-66 (2-6)
                score += 0.4

        # 2. 高牌
        max_val = max(val1, val2)
        if max_val == 14:  # A
            score += 0.3
        elif max_val >= 12:  # K, Q
            score += 0.2
        elif max_val >= 10:  # J, T
            score += 0.1

        # 3. 同花
        if card1.suit == card2.suit:
            score += 0.2

        # 4. 连牌 (顺子听牌)
        if abs(val1 - val2) <= 4:
            score += 0.1

        # 5. 如果有公共牌，评估改进
        if community_cards:
            all_cards = hole_cards + community_cards

            # 检查对子
            values = [c.value for c in all_cards]
            if len(set(values)) < len(values):  # 有重复
                score += 0.3

            # 检查同花听牌
            suits = [c.suit for c in all_cards]
            for suit in set(suits):
                if suits.count(suit) >= 4:
                    score += 0.2
                    break

        return min(score, 1.0)

    def calculate_pot_odds(
        self,
        pot: int,
        call_amount: int
    ) -> float:
        """
        计算底池赔率

        Returns:
            赔率 (如果需要跟注100，底池有300，返回3.0)
        """
        if call_amount <= 0:
            return float('inf')
        return pot / call_amount

    def make_decision(
        self,
        player_id: int,
        player_type: str,
        hole_cards: List[Card],
        community_cards: List[Card],
        current_bet: int,
        player_bet: int,
        player_chips: int,
        pot: int,
        game_state: str,
        position: str = "MP"
    ) -> Tuple[str, Optional[int]]:
        """
        为AI玩家做出决策

        Args:
            player_id: 玩家ID
            player_type: 玩家类型 (TAG/LAG/PASSIVE/FISH/REGULAR)
            hole_cards: 底牌
            community_cards: 公共牌
            current_bet: 当前下注额
            player_bet: 玩家已下注额
            player_chips: 玩家剩余筹码
            pot: 底池
            game_state: 游戏阶段 (preflop/flop/turn/river)
            position: 位置 (BTN/SB/BB/UTG/MP/CO)

        Returns:
            (action, amount) - 动作和金额
        """
        call_amount = current_bet - player_bet

        # 如果无需跟注
        if call_amount == 0:
            return self._decide_with_no_bet(
                player_type, hole_cards, community_cards,
                current_bet, player_chips, pot, game_state
            )

        # 需要跟注
        return self._decide_with_bet(
            player_type, hole_cards, community_cards,
            current_bet, call_amount, player_chips, pot, game_state
        )

    def _decide_with_no_bet(
        self,
        player_type: str,
        hole_cards: List[Card],
        community_cards: List[Card],
        current_bet: int,
        chips: int,
        pot: int,
        game_state: str
    ) -> Tuple[str, Optional[int]]:
        """当无需跟注时的决策

        注意: chips 是玩家剩余筹码，current_bet 是当前全局最大下注
        玩家已经下注了 current_bet (因为 call_amount == 0)
        """
        hand_strength = self.evaluate_hand_strength(hole_cards, community_cards)

        # 最小加注额（至少是大盲注，或当前下注的2倍）
        # 如果是preflop且current_bet是盲注，则至少加注到2BB
        # 否则至少加注到current_bet的2倍
        min_raise = max(current_bet * 2, current_bet + max(pot // 10, 2))
        if min_raise > chips + current_bet:
            # 如果最小加注超过筹码，则不能加注，只能过牌或all-in
            min_raise = current_bet + 1  # 设置一个无法达到的值，将导致选择check

        # 根据玩家类型和手牌强度决策
        if player_type == "TAG":  # 紧凶型
            if hand_strength >= 0.7:
                # 强牌：加注
                raise_size = max(int(pot * 0.75), min_raise - current_bet)
                raise_amount = min(raise_size, chips)
                if current_bet + raise_amount > current_bet:  # 确保有效加注
                    return ("raise", current_bet + raise_amount)
                return ("check", None)
            elif hand_strength >= 0.4:
                # 中等牌：有时加注，有时过牌
                if random.random() < 0.3:
                    raise_size = max(int(pot * 0.5), min_raise - current_bet)
                    raise_amount = min(raise_size, chips)
                    if current_bet + raise_amount > current_bet:
                        return ("raise", current_bet + raise_amount)
                return ("check", None)
            else:
                # 弱牌：过牌
                return ("check", None)

        elif player_type == "LAG":  # 松凶型
            if hand_strength >= 0.5:
                # 中等以上牌：加注
                raise_size = max(int(pot * random.uniform(0.5, 1.5)), min_raise - current_bet)
                raise_amount = min(raise_size, chips)
                if current_bet + raise_amount > current_bet:
                    return ("raise", current_bet + raise_amount)
                return ("check", None)
            elif random.random() < 0.4:
                # 弱牌也有40%概率加注（诈唬）
                raise_size = max(int(pot * 0.6), min_raise - current_bet)
                raise_amount = min(raise_size, chips)
                if current_bet + raise_amount > current_bet:
                    return ("raise", current_bet + raise_amount)
            return ("check", None)

        elif player_type == "PASSIVE":  # 被动型
            if hand_strength >= 0.8:
                # 非常强的牌才加注
                raise_size = max(int(pot * 0.4), min_raise - current_bet)
                raise_amount = min(raise_size, chips)
                if current_bet + raise_amount > current_bet:
                    return ("raise", current_bet + raise_amount)
            return ("check", None)

        elif player_type == "FISH":  # 鱼
            # 随机决策，经常看牌
            if random.random() < 0.2 and hand_strength >= 0.3:
                raise_size = max(int(pot * random.uniform(0.3, 1.0)), min_raise - current_bet)
                raise_amount = min(raise_size, chips)
                if current_bet + raise_amount > current_bet:
                    return ("raise", current_bet + raise_amount)
            return ("check", None)

        else:  # REGULAR - 常规型
            if hand_strength >= 0.6:
                raise_size = max(int(pot * 0.6), min_raise - current_bet)
                raise_amount = min(raise_size, chips)
                if current_bet + raise_amount > current_bet:
                    return ("raise", current_bet + raise_amount)
                return ("check", None)
            elif hand_strength >= 0.4:
                if random.random() < 0.2:
                    raise_size = max(int(pot * 0.5), min_raise - current_bet)
                    raise_amount = min(raise_size, chips)
                    if current_bet + raise_amount > current_bet:
                        return ("raise", current_bet + raise_amount)
                return ("check", None)
            return ("check", None)

    def _decide_with_bet(
        self,
        player_type: str,
        hole_cards: List[Card],
        community_cards: List[Card],
        current_bet: int,
        call_amount: int,
        chips: int,
        pot: int,
        game_state: str
    ) -> Tuple[str, Optional[int]]:
        """当需要跟注时的决策

        注意: chips 是玩家剩余筹码，call_amount 是需要跟注的金额
        如果筹码不足，根据手牌强度决定是 all-in 还是弃牌
        """
        hand_strength = self.evaluate_hand_strength(hole_cards, community_cards)
        pot_odds = self.calculate_pot_odds(pot, call_amount)

        # 最小加注额（当前下注的2倍，或current_bet + 最小加注）
        min_raise_total = max(current_bet * 2, current_bet + max(call_amount, 2))

        # 如果筹码连跟注都不够，只能 all-in 或弃牌
        if chips <= call_amount:
            # 根据手牌强度和玩家类型决定是否 all-in
            all_in_threshold = {
                "TAG": 0.5,
                "LAG": 0.4,
                "PASSIVE": 0.6,
                "FISH": 0.3,
                "REGULAR": 0.5
            }
            if hand_strength >= all_in_threshold.get(player_type, 0.5):
                return ("all_in", None)
            return ("fold", None)

        # 根据玩家类型决策
        if player_type == "TAG":  # 紧凶型
            if hand_strength >= 0.7:
                # 超强牌：加注或 all-in
                raise_size = max(int(pot * 0.8), min_raise_total - current_bet)
                total_raise = current_bet + raise_size
                if raise_size <= chips - call_amount and total_raise > current_bet:
                    return ("raise", total_raise)
                return ("all_in", None)
            elif hand_strength >= 0.4:
                return ("call", None)
            elif hand_strength >= 0.25 and pot_odds >= 2.5:
                return ("call", None)
            else:
                return ("fold", None)

        elif player_type == "LAG":  # 松凶型
            if hand_strength >= 0.5:
                # 较强牌：加注或 all-in
                raise_size = max(int(pot * random.uniform(0.8, 1.5)), min_raise_total - current_bet)
                total_raise = current_bet + raise_size
                if raise_size <= chips - call_amount and total_raise > current_bet:
                    return ("raise", total_raise)
                return ("all_in", None)
            elif hand_strength >= 0.25:
                return ("call", None)
            elif random.random() < 0.4:
                if random.random() < 0.6:
                    return ("call", None)
                else:
                    raise_size = max(int(pot * 0.7), min_raise_total - current_bet)
                    total_raise = current_bet + raise_size
                    if raise_size <= chips - call_amount and total_raise > current_bet:
                        return ("raise", total_raise)
                    return ("all_in", None)
            return ("fold", None)

        elif player_type == "PASSIVE":  # 被动型
            if hand_strength >= 0.6:
                if random.random() < 0.2:
                    raise_size = max(int(pot * 0.5), min_raise_total - current_bet)
                    total_raise = current_bet + raise_size
                    if raise_size <= chips - call_amount and total_raise > current_bet:
                        return ("raise", total_raise)
                    return ("all_in", None)
                return ("call", None)
            elif hand_strength >= 0.3:
                return ("call", None)
            elif hand_strength >= 0.2 and pot_odds >= 3.0:
                return ("call", None)
            return ("fold", None)

        elif player_type == "FISH":  # 鱼
            if hand_strength >= 0.2 or random.random() < 0.6:
                if random.random() < 0.1:
                    raise_size = max(int(pot * random.uniform(0.5, 1.2)), min_raise_total - current_bet)
                    total_raise = current_bet + raise_size
                    if raise_size <= chips - call_amount and total_raise > current_bet:
                        return ("raise", total_raise)
                    return ("all_in", None)
                return ("call", None)
            return ("fold", None)

        else:  # REGULAR - 常规型
            if hand_strength >= 0.6:
                raise_size = max(int(pot * 0.7), min_raise_total - current_bet)
                total_raise = current_bet + raise_size
                if raise_size <= chips - call_amount and total_raise > current_bet:
                    return ("raise", total_raise)
                return ("all_in", None)
            elif hand_strength >= 0.35:
                return ("call", None)
            elif hand_strength >= 0.2 and pot_odds >= 2.5:
                return ("call", None)
            return ("fold", None)

    def assign_player_type(self, player_id: int) -> str:
        """
        为玩家分配类型

        可以根据player_id或随机分配
        """
        types = ["TAG", "LAG", "PASSIVE", "FISH", "REGULAR"]
        weights = [0.2, 0.15, 0.2, 0.25, 0.2]  # 各类型概率

        return random.choices(types, weights=weights)[0]


# 全局单例
ai_decision_maker = AIDecisionMaker()
