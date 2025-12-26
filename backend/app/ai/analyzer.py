"""玩家分析器 - AI模块"""
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
import numpy as np


class PlayerType(Enum):
    """玩家类型"""
    TAG = "紧凶型"       # Tight Aggressive - 只玩强牌,下注激进
    LAG = "松凶型"       # Loose Aggressive - 玩牌范围广,下注激进
    PASSIVE = "被动型"   # Tight Passive - 保守打法
    FISH = "鱼"         # Loose Passive - 随机打法
    UNKNOWN = "未知"


@dataclass
class PlayerProfile:
    """玩家画像"""
    player_id: int
    player_type: PlayerType
    skill_level: int  # 0-100
    vpip: float       # 入池率
    pfr: float        # 翻前加注率
    af: float         # 激进因子
    three_bet: float  # 3-bet率
    wtsd: float       # 摊牌率
    total_hands: int


class PlayerAnalyzer:
    """玩家分析器"""

    def __init__(self):
        pass

    def calculate_stats(self, actions: List[Dict]) -> Dict:
        """
        计算玩家统计数据

        Args:
            actions: 玩家动作列表, 每个动作包含:
                - street: 阶段 (preflop/flop/turn/river)
                - action_type: 动作类型 (fold/call/raise/check/all_in)
                - amount: 金额
        """
        if not actions:
            return {
                "vpip": 0.0,
                "pfr": 0.0,
                "af": 0.0,
                "three_bet": 0.0,
                "wtsd": 0.0,
                "total_hands": 0
            }

        # 按手牌分组
        hands = {}
        for action in actions:
            hand_id = action.get("hand_id", 0)
            if hand_id not in hands:
                hands[hand_id] = []
            hands[hand_id].append(action)

        total_hands = len(hands)

        # 计算VPIP (自愿入池率)
        vpip_count = 0
        for hand_actions in hands.values():
            preflop_actions = [a for a in hand_actions if a.get("street") == "preflop"]
            for action in preflop_actions:
                if action.get("action_type") in ["call", "raise", "all_in"]:
                    vpip_count += 1
                    break

        vpip = (vpip_count / total_hands * 100) if total_hands > 0 else 0

        # 计算PFR (翻牌前加注率)
        pfr_count = 0
        for hand_actions in hands.values():
            preflop_actions = [a for a in hand_actions if a.get("street") == "preflop"]
            for action in preflop_actions:
                if action.get("action_type") in ["raise", "all_in"]:
                    pfr_count += 1
                    break

        pfr = (pfr_count / total_hands * 100) if total_hands > 0 else 0

        # 计算AF (激进因子) = (raise + bet) / call
        raise_count = sum(1 for a in actions if a.get("action_type") in ["raise", "all_in"])
        call_count = sum(1 for a in actions if a.get("action_type") == "call")
        af = raise_count / call_count if call_count > 0 else raise_count

        # 计算3-bet率 (面对加注时再加注)
        three_bet = pfr * 0.3  # 简化计算

        # 计算WTSD (摊牌率) - 需要更多数据,这里简化
        wtsd = 25.0  # 默认值

        return {
            "vpip": round(vpip, 1),
            "pfr": round(pfr, 1),
            "af": round(af, 2),
            "three_bet": round(three_bet, 1),
            "wtsd": round(wtsd, 1),
            "total_hands": total_hands
        }

    def classify_player(self, stats: Dict) -> PlayerType:
        """
        分类玩家类型

        基于VPIP和PFR的经典分类:
        - 紧凶 (TAG): VPIP < 25, PFR > 15
        - 松凶 (LAG): VPIP > 25, PFR > 20
        - 被动型: PFR < 10
        - 鱼: VPIP > 35, PFR < 15
        """
        vpip = stats.get("vpip", 0)
        pfr = stats.get("pfr", 0)
        total_hands = stats.get("total_hands", 0)

        if total_hands < 20:
            return PlayerType.UNKNOWN

        # 紧凶型
        if vpip < 25 and pfr > 15:
            return PlayerType.TAG

        # 松凶型
        if vpip > 25 and pfr > 20:
            return PlayerType.LAG

        # 鱼
        if vpip > 35 and pfr < 15:
            return PlayerType.FISH

        # 被动型
        if pfr < 10:
            return PlayerType.PASSIVE

        return PlayerType.UNKNOWN

    def evaluate_skill(self, stats: Dict) -> int:
        """
        评估技术水平 (0-100分)

        评分维度:
        - VPIP合理性 (理想范围: 18-25)
        - PFR合理性 (理想范围: 12-18)
        - PFR/VPIP比例 (理想 > 0.65)
        - 激进因子 (理想范围: 1.5-3.0)
        """
        score = 50  # 基础分

        vpip = stats.get("vpip", 0)
        pfr = stats.get("pfr", 0)
        af = stats.get("af", 0)
        total_hands = stats.get("total_hands", 0)

        # 样本量不足
        if total_hands < 50:
            return score

        # VPIP评分 (最高20分)
        if 18 <= vpip <= 25:
            score += 20
        elif 15 <= vpip <= 28:
            score += 12
        elif 12 <= vpip <= 32:
            score += 6

        # PFR评分 (最高20分)
        if 12 <= pfr <= 18:
            score += 20
        elif 8 <= pfr <= 22:
            score += 12
        elif 5 <= pfr <= 25:
            score += 6

        # PFR/VPIP比例评分 (最高15分)
        if vpip > 0:
            ratio = pfr / vpip
            if ratio >= 0.70:
                score += 15
            elif ratio >= 0.60:
                score += 10
            elif ratio >= 0.50:
                score += 5

        # 激进因子评分 (最高15分)
        if 1.5 <= af <= 3.0:
            score += 15
        elif 1.0 <= af <= 4.0:
            score += 8
        elif 0.5 <= af <= 5.0:
            score += 4

        return min(score, 100)

    def get_player_profile(self, player_id: int, actions: List[Dict]) -> PlayerProfile:
        """获取完整玩家画像"""
        stats = self.calculate_stats(actions)
        player_type = self.classify_player(stats)
        skill_level = self.evaluate_skill(stats)

        return PlayerProfile(
            player_id=player_id,
            player_type=player_type,
            skill_level=skill_level,
            vpip=stats["vpip"],
            pfr=stats["pfr"],
            af=stats["af"],
            three_bet=stats["three_bet"],
            wtsd=stats["wtsd"],
            total_hands=stats["total_hands"]
        )

    def get_recommendations(self, profile: PlayerProfile) -> List[str]:
        """根据玩家画像给出建议"""
        recommendations = []

        if profile.vpip > 30:
            recommendations.append("建议收紧起手牌范围,减少入池率")

        if profile.pfr < 10:
            recommendations.append("建议增加翻前加注频率,打法更激进")

        if profile.vpip > 0 and profile.pfr / profile.vpip < 0.5:
            recommendations.append("跟注过多,建议要么加注要么弃牌")

        if profile.af < 1.0:
            recommendations.append("打法过于被动,建议增加下注和加注")

        if profile.af > 4.0:
            recommendations.append("打法过于激进,建议适当控制")

        if not recommendations:
            recommendations.append("数据良好,继续保持!")

        return recommendations


# 单例分析器
player_analyzer = PlayerAnalyzer()
