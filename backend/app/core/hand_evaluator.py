"""
德州扑克牌型评估器
实现完整的德州扑克牌型判断和大小比较
"""

from typing import List, Tuple, Dict
from collections import Counter
from enum import IntEnum
from .poker import Card


class HandRank(IntEnum):
    """牌型等级（数字越大越强）"""
    HIGH_CARD = 1       # 高牌
    ONE_PAIR = 2        # 一对
    TWO_PAIR = 3        # 两对
    THREE_OF_KIND = 4   # 三条
    STRAIGHT = 5        # 顺子
    FLUSH = 6           # 同花
    FULL_HOUSE = 7      # 葫芦（三带二）
    FOUR_OF_KIND = 8    # 四条
    STRAIGHT_FLUSH = 9  # 同花顺
    ROYAL_FLUSH = 10    # 皇家同花顺


class HandEvaluator:
    """德州扑克手牌评估器"""

    # 点数映射（用于比较大小）
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }

    @staticmethod
    def evaluate_hand(hole_cards: List[Card], community_cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """
        评估最佳手牌

        Args:
            hole_cards: 玩家底牌（2张）
            community_cards: 公共牌（3-5张）

        Returns:
            (牌型等级, 决定性点数列表)
            例如: (HandRank.TWO_PAIR, [13, 13, 8, 8, 7]) 表示KK88带7
        """
        # 合并所有可用的牌
        all_cards = hole_cards + community_cards

        if len(all_cards) < 5:
            raise ValueError("至少需要5张牌才能评估手牌")

        # 从所有牌中找出最佳的5张牌组合
        best_rank = HandRank.HIGH_CARD
        best_values = []

        # 如果是7张牌，需要遍历所有C(7,5)=21种组合
        # 简化处理：直接评估所有7张牌中最强的组合
        from itertools import combinations

        for five_cards in combinations(all_cards, 5):
            rank, values = HandEvaluator._evaluate_five_cards(list(five_cards))

            # 比较并保留最佳组合
            if rank > best_rank or (rank == best_rank and values > best_values):
                best_rank = rank
                best_values = values

        return best_rank, best_values

    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """评估固定5张牌的牌型"""

        # 获取点数和花色
        ranks = [card.value for card in cards]  # card.value 返回 2-14
        suits = [card.suit for card in cards]

        # 排序（从大到小）
        ranks_sorted = sorted(ranks, reverse=True)

        # 统计每个点数出现的次数
        rank_counts = Counter(ranks)
        count_values = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

        # 检查是否同花
        is_flush = len(set(suits)) == 1

        # 检查是否顺子
        is_straight, straight_high = HandEvaluator._check_straight(ranks_sorted)

        # 判断牌型

        # 皇家同花顺 (Royal Flush)
        if is_flush and is_straight and straight_high == 14:
            return HandRank.ROYAL_FLUSH, [14, 13, 12, 11, 10]

        # 同花顺 (Straight Flush)
        if is_flush and is_straight:
            if straight_high == 5:  # A-2-3-4-5 的特殊情况
                return HandRank.STRAIGHT_FLUSH, [5, 4, 3, 2, 1]
            return HandRank.STRAIGHT_FLUSH, [straight_high, straight_high-1, straight_high-2, straight_high-3, straight_high-4]

        # 四条 (Four of a Kind)
        if count_values[0][1] == 4:
            four_rank = count_values[0][0]
            kicker = count_values[1][0]
            return HandRank.FOUR_OF_KIND, [four_rank] * 4 + [kicker]

        # 葫芦 (Full House)
        if count_values[0][1] == 3 and count_values[1][1] == 2:
            three_rank = count_values[0][0]
            pair_rank = count_values[1][0]
            return HandRank.FULL_HOUSE, [three_rank] * 3 + [pair_rank] * 2

        # 同花 (Flush)
        if is_flush:
            return HandRank.FLUSH, ranks_sorted

        # 顺子 (Straight)
        if is_straight:
            if straight_high == 5:  # A-2-3-4-5
                return HandRank.STRAIGHT, [5, 4, 3, 2, 1]
            return HandRank.STRAIGHT, [straight_high, straight_high-1, straight_high-2, straight_high-3, straight_high-4]

        # 三条 (Three of a Kind)
        if count_values[0][1] == 3:
            three_rank = count_values[0][0]
            kickers = sorted([count_values[1][0], count_values[2][0]], reverse=True)
            return HandRank.THREE_OF_KIND, [three_rank] * 3 + kickers

        # 两对 (Two Pair)
        if count_values[0][1] == 2 and count_values[1][1] == 2:
            pair1 = max(count_values[0][0], count_values[1][0])
            pair2 = min(count_values[0][0], count_values[1][0])
            kicker = count_values[2][0]
            return HandRank.TWO_PAIR, [pair1, pair1, pair2, pair2, kicker]

        # 一对 (One Pair)
        if count_values[0][1] == 2:
            pair_rank = count_values[0][0]
            kickers = sorted([count_values[1][0], count_values[2][0], count_values[3][0]], reverse=True)
            return HandRank.ONE_PAIR, [pair_rank, pair_rank] + kickers

        # 高牌 (High Card)
        return HandRank.HIGH_CARD, ranks_sorted

    @staticmethod
    def _check_straight(ranks: List[int]) -> Tuple[bool, int]:
        """
        检查是否是顺子

        Returns:
            (是否顺子, 顺子最高点)
        """
        sorted_ranks = sorted(set(ranks), reverse=True)

        # 常规顺子检查
        if len(sorted_ranks) == 5:
            if sorted_ranks[0] - sorted_ranks[4] == 4:
                return True, sorted_ranks[0]

        # 特殊情况：A-2-3-4-5 (轮子/自行车)
        if sorted_ranks == [14, 5, 4, 3, 2]:
            return True, 5  # A在这里作为1，所以最高点是5

        return False, 0

    @staticmethod
    def compare_hands(hand1: Tuple[HandRank, List[int]],
                     hand2: Tuple[HandRank, List[int]]) -> int:
        """
        比较两手牌的大小

        Returns:
            1: hand1 > hand2
            0: hand1 == hand2 (平局)
            -1: hand1 < hand2
        """
        rank1, values1 = hand1
        rank2, values2 = hand2

        # 先比较牌型等级
        if rank1 > rank2:
            return 1
        elif rank1 < rank2:
            return -1

        # 牌型相同，比较决定性点数
        for v1, v2 in zip(values1, values2):
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1

        # 完全相同
        return 0

    @staticmethod
    def hand_to_string(rank: HandRank, values: List[int]) -> str:
        """将牌型转换为可读字符串"""

        rank_names = {
            '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
            '7': '7', '8': '8', '9': '9', 'T': '10',
            'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'
        }

        # 反向映射
        value_to_rank = {v: k for k, v in HandEvaluator.RANK_VALUES.items()}

        if rank == HandRank.ROYAL_FLUSH:
            return "皇家同花顺"
        elif rank == HandRank.STRAIGHT_FLUSH:
            high = value_to_rank[values[0]]
            return f"同花顺 ({rank_names[high]}高)"
        elif rank == HandRank.FOUR_OF_KIND:
            four = value_to_rank[values[0]]
            return f"四条{rank_names[four]}"
        elif rank == HandRank.FULL_HOUSE:
            three = value_to_rank[values[0]]
            pair = value_to_rank[values[3]]
            return f"葫芦 ({rank_names[three]}带{rank_names[pair]})"
        elif rank == HandRank.FLUSH:
            high = value_to_rank[values[0]]
            return f"同花 ({rank_names[high]}高)"
        elif rank == HandRank.STRAIGHT:
            high = value_to_rank[values[0]]
            return f"顺子 ({rank_names[high]}高)"
        elif rank == HandRank.THREE_OF_KIND:
            three = value_to_rank[values[0]]
            return f"三条{rank_names[three]}"
        elif rank == HandRank.TWO_PAIR:
            high_pair = value_to_rank[values[0]]
            low_pair = value_to_rank[values[2]]
            return f"两对 ({rank_names[high_pair]}和{rank_names[low_pair]})"
        elif rank == HandRank.ONE_PAIR:
            pair = value_to_rank[values[0]]
            return f"一对{rank_names[pair]}"
        else:
            high = value_to_rank[values[0]]
            return f"高牌{rank_names[high]}"
