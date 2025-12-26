"""智能发牌器 - AI控制发牌策略"""
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from ..core.poker import Card, Deck, RANK_SYMBOLS


@dataclass
class DealingConfig:
    """发牌配置"""
    # 公平性约束 - 最大调整幅度
    max_adjustment: float = 0.15  # 15%

    # 娱乐性权重
    entertainment_weight: float = 0.3

    # 是否启用智能发牌
    smart_dealing_enabled: bool = True

    # 连续输牌补偿阈值
    loss_streak_threshold: int = 5


class SmartDealer:
    """
    智能发牌器

    核心目标:
    1. 在公平性约束内提升娱乐性
    2. 对不活跃玩家适度提升手牌强度
    3. 对连续输牌玩家给予补偿
    4. 增加戏剧性牌面出现概率
    """

    def __init__(self, config: Optional[DealingConfig] = None):
        self.config = config or DealingConfig()
        self.deck = Deck()

    def deal_with_strategy(
        self,
        num_players: int,
        player_states: List[Dict]
    ) -> Tuple[List[List[Card]], List[Card]]:
        """
        策略性发牌

        Args:
            num_players: 玩家数量
            player_states: 玩家状态列表, 包含:
                - player_id: 玩家ID
                - activity_score: 活跃度 (0-1)
                - loss_streak: 连续输牌次数
                - skill_level: 技术水平

        Returns:
            (hole_cards, remaining_deck)
        """
        if not self.config.smart_dealing_enabled:
            return self._standard_deal(num_players)

        # 计算每个玩家的权重
        weights = self._calculate_weights(player_states)

        # 按权重发牌
        return self._weighted_deal(num_players, weights)

    def _standard_deal(self, num_players: int) -> Tuple[List[List[Card]], List[Card]]:
        """标准随机发牌"""
        self.deck.reset()
        self.deck.shuffle()

        hole_cards = []
        for _ in range(num_players):
            cards = self.deck.deal(2)
            hole_cards.append(cards)

        return hole_cards, self.deck.cards

    def _calculate_weights(self, player_states: List[Dict]) -> List[float]:
        """计算每个玩家的发牌权重"""
        weights = []

        for state in player_states:
            weight = 1.0

            # 活跃度调整 - 不活跃玩家稍微提升
            activity = state.get("activity_score", 1.0)
            if activity < 0.3:
                weight *= 1.1

            # 连续输牌补偿
            loss_streak = state.get("loss_streak", 0)
            if loss_streak >= self.config.loss_streak_threshold:
                compensation = min(loss_streak * 0.02, self.config.max_adjustment)
                weight *= (1 + compensation)

            # 确保在公平性约束内
            weight = min(weight, 1 + self.config.max_adjustment)
            weight = max(weight, 1 - self.config.max_adjustment)

            weights.append(weight)

        return weights

    def _weighted_deal(
        self,
        num_players: int,
        weights: List[float]
    ) -> Tuple[List[List[Card]], List[Card]]:
        """
        加权发牌

        原理: 对权重较高的玩家,增加获得较强手牌的概率
        """
        self.deck.reset()
        self.deck.shuffle()

        # 生成所有可能的两张牌组合并评估强度
        all_cards = self.deck.cards.copy()

        # 按权重从高到低排序玩家
        player_indices = list(range(num_players))
        if len(weights) >= num_players:
            player_indices = sorted(
                range(num_players),
                key=lambda i: weights[i] if i < len(weights) else 1.0,
                reverse=True
            )

        hole_cards = [None] * num_players
        used_cards = set()

        for player_idx in player_indices:
            weight = weights[player_idx] if player_idx < len(weights) else 1.0

            # 从剩余牌中选择
            available_cards = [c for i, c in enumerate(all_cards) if i not in used_cards]

            if len(available_cards) < 2:
                break

            # 根据权重选择手牌
            if weight > 1.05:
                # 权重高 - 倾向选择较强的牌
                hand = self._select_stronger_hand(available_cards)
            elif weight < 0.95:
                # 权重低 - 倾向选择较弱的牌
                hand = self._select_weaker_hand(available_cards)
            else:
                # 正常随机
                random.shuffle(available_cards)
                hand = available_cards[:2]

            hole_cards[player_idx] = hand

            # 标记已使用的牌
            for card in hand:
                for i, c in enumerate(all_cards):
                    if i not in used_cards and c.suit == card.suit and c.rank == card.rank:
                        used_cards.add(i)
                        break

        # 更新剩余牌堆
        remaining = [c for i, c in enumerate(all_cards) if i not in used_cards]
        self.deck.cards = remaining

        return hole_cards, remaining

    def _select_stronger_hand(self, cards: List[Card]) -> List[Card]:
        """选择较强的手牌"""
        if len(cards) < 2:
            return cards

        # 生成所有可能的组合并评分
        best_hand = None
        best_score = -1

        # 为了效率,只考虑前20张牌的组合
        sample_cards = cards[:min(20, len(cards))]

        for i, card1 in enumerate(sample_cards):
            for card2 in sample_cards[i + 1:]:
                score = self._evaluate_hand_strength([card1, card2])
                if score > best_score:
                    best_score = score
                    best_hand = [card1, card2]

        # 加入随机性,不总是选最强的
        if random.random() < 0.3 and len(cards) >= 4:
            # 30%概率选择次优
            random.shuffle(cards)
            return cards[:2]

        return best_hand or cards[:2]

    def _select_weaker_hand(self, cards: List[Card]) -> List[Card]:
        """选择较弱的手牌"""
        if len(cards) < 2:
            return cards

        # 简单实现: 随机选择中等偏下的牌
        random.shuffle(cards)
        return cards[:2]

    def _evaluate_hand_strength(self, cards: List[Card]) -> float:
        """
        评估两张底牌的强度 (0-1)

        考虑因素:
        - 高牌价值
        - 是否对子
        - 是否同花
        - 是否连张
        """
        if len(cards) != 2:
            return 0

        card1, card2 = cards
        score = 0.0

        # 高牌加分 (每张牌最高0.3分)
        score += (card1.rank / 12) * 0.3
        score += (card2.rank / 12) * 0.3

        # 对子加分 (0.25分)
        if card1.rank == card2.rank:
            score += 0.25
            # 高对子额外加分
            score += (card1.rank / 12) * 0.1

        # 同花加分 (0.1分)
        if card1.suit == card2.suit:
            score += 0.1

        # 连张加分 (0.05分)
        gap = abs(card1.rank - card2.rank)
        if gap == 1:
            score += 0.05
        elif gap == 2:
            score += 0.02

        return min(score, 1.0)

    def get_hand_description(self, cards: List[Card]) -> str:
        """获取手牌描述"""
        if len(cards) != 2:
            return "无效手牌"

        card1, card2 = sorted(cards, key=lambda c: c.rank, reverse=True)

        rank1 = RANK_SYMBOLS[card1.rank]
        rank2 = RANK_SYMBOLS[card2.rank]
        suited = "s" if card1.suit == card2.suit else "o"

        if card1.rank == card2.rank:
            return f"{rank1}{rank2}"  # 对子
        else:
            return f"{rank1}{rank2}{suited}"


# 全局智能发牌器
smart_dealer = SmartDealer()
