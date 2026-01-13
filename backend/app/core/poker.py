"""德州扑克核心逻辑"""
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class Suit(Enum):
    """花色"""
    SPADE = 0    # 黑桃
    HEART = 1    # 红心
    DIAMOND = 2  # 方块
    CLUB = 3     # 梅花


SUIT_SYMBOLS = ['♠', '♥', '♦', '♣']
RANK_SYMBOLS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']


@dataclass
class Card:
    """扑克牌"""
    suit: int  # 0-3
    rank: int  # 0-12 (2-A)

    def __str__(self) -> str:
        return f"{RANK_SYMBOLS[self.rank]}{SUIT_SYMBOLS[self.suit]}"

    def to_dict(self) -> dict:
        return {
            "suit": self.suit,
            "rank": self.rank,
            "display": str(self)
        }

    @property
    def value(self) -> int:
        """牌面值 (2-14)"""
        return self.rank + 2


class Deck:
    """牌堆"""

    def __init__(self):
        self.cards: List[Card] = []
        self.reset()

    def reset(self):
        """重置牌堆"""
        self.cards = [
            Card(suit, rank)
            for suit in range(4)
            for rank in range(13)
        ]

    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)

    def deal(self, n: int = 1) -> List[Card]:
        """发牌"""
        if len(self.cards) < n:
            raise ValueError("牌堆牌数不足")
        dealt = self.cards[:n]
        self.cards = self.cards[n:]
        return dealt

    def burn(self):
        """烧牌"""
        if self.cards:
            self.cards.pop(0)


@dataclass
class PlayerState:
    """玩家状态"""
    player_id: int
    position: int
    chips: float
    hole_cards: List[Card] = field(default_factory=list)
    current_bet: float = 0
    total_bet: float = 0
    is_active: bool = True
    is_all_in: bool = False
    has_acted: bool = False


class GameState(Enum):
    """游戏状态"""
    WAITING = "waiting"
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"
    FINISHED = "finished"


@dataclass
class PokerGame:
    """德州扑克游戏"""
    game_id: str
    small_blind: float = 1.0
    big_blind: float = 2.0
    deck: Deck = field(default_factory=Deck)
    players: List[PlayerState] = field(default_factory=list)
    community_cards: List[Card] = field(default_factory=list)
    pot: float = 0
    current_bet: float = 0
    current_player_idx: int = 0
    dealer_idx: int = 0
    state: GameState = GameState.WAITING

    def add_player(self, player_id: int, chips: float = 1000) -> PlayerState:
        """添加玩家"""
        position = len(self.players)
        player = PlayerState(
            player_id=player_id,
            position=position,
            chips=chips
        )
        self.players.append(player)
        return player

    def start_hand(self):
        """开始一手牌"""
        if len(self.players) < 2:
            raise ValueError("至少需要2名玩家")

        # 重置状态
        self.deck.reset()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0

        # 重置玩家状态
        for player in self.players:
            player.hole_cards = []
            player.current_bet = 0
            player.total_bet = 0
            player.is_active = True
            player.is_all_in = False
            player.has_acted = False

        # 发底牌
        for player in self.players:
            player.hole_cards = self.deck.deal(2)

        # 收取盲注
        self._post_blinds()
        self.state = GameState.PREFLOP

    def _post_blinds(self):
        """收取盲注"""
        sb_idx = (self.dealer_idx + 1) % len(self.players)
        bb_idx = (self.dealer_idx + 2) % len(self.players)

        # 小盲注
        sb_player = self.players[sb_idx]
        sb_amount = min(self.small_blind, sb_player.chips)
        sb_player.chips -= sb_amount
        sb_player.current_bet = sb_amount
        sb_player.total_bet = sb_amount
        self.pot += sb_amount

        # 大盲注
        bb_player = self.players[bb_idx]
        bb_amount = min(self.big_blind, bb_player.chips)
        bb_player.chips -= bb_amount
        bb_player.current_bet = bb_amount
        bb_player.total_bet = bb_amount
        self.pot += bb_amount

        self.current_bet = self.big_blind
        # 从大盲注后一位开始行动
        self.current_player_idx = (bb_idx + 1) % len(self.players)

    def deal_flop(self) -> List[Card]:
        """发翻牌"""
        if self.state != GameState.PREFLOP:
            raise ValueError("当前不是翻牌前阶段")

        self.deck.burn()
        flop = self.deck.deal(3)
        self.community_cards.extend(flop)
        self.state = GameState.FLOP
        self._reset_betting_round()
        return flop

    def deal_turn(self) -> Card:
        """发转牌"""
        if self.state != GameState.FLOP:
            raise ValueError("当前不是翻牌阶段")

        self.deck.burn()
        turn = self.deck.deal(1)[0]
        self.community_cards.append(turn)
        self.state = GameState.TURN
        self._reset_betting_round()
        return turn

    def deal_river(self) -> Card:
        """发河牌"""
        if self.state != GameState.TURN:
            raise ValueError("当前不是转牌阶段")

        self.deck.burn()
        river = self.deck.deal(1)[0]
        self.community_cards.append(river)
        self.state = GameState.RIVER
        self._reset_betting_round()
        return river

    def _reset_betting_round(self):
        """重置下注轮"""
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0
            player.has_acted = False

        # 从庄家后第一个活跃玩家开始
        self.current_player_idx = (self.dealer_idx + 1) % len(self.players)
        while not self.players[self.current_player_idx].is_active:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def player_action(self, player_id: int, action: str, amount: float = 0) -> dict:
        """处理玩家动作"""
        player = self._get_player(player_id)
        if not player:
            raise ValueError("玩家不存在")

        if player.position != self.current_player_idx:
            raise ValueError("还没轮到该玩家行动")

        result = {"action": action, "amount": 0}

        if action == "fold":
            player.is_active = False

        elif action == "check":
            if player.current_bet < self.current_bet:
                raise ValueError("必须跟注或弃牌")

        elif action == "call":
            call_amount = self.current_bet - player.current_bet
            actual_amount = min(call_amount, player.chips)
            player.chips -= actual_amount
            player.current_bet += actual_amount
            player.total_bet += actual_amount
            self.pot += actual_amount
            result["amount"] = actual_amount

            if player.chips == 0:
                player.is_all_in = True

        elif action == "raise":
            if amount <= self.current_bet:
                raise ValueError("加注金额必须大于当前下注")

            raise_amount = amount - player.current_bet
            if raise_amount > player.chips:
                raise ValueError("筹码不足")

            player.chips -= raise_amount
            player.current_bet = amount
            player.total_bet += raise_amount
            self.pot += raise_amount
            self.current_bet = amount
            result["amount"] = raise_amount

            # 重置其他玩家的行动状态
            for p in self.players:
                if p.player_id != player_id and p.is_active:
                    p.has_acted = False

        elif action == "all_in":
            all_in_amount = player.chips
            player.current_bet += all_in_amount
            player.total_bet += all_in_amount
            self.pot += all_in_amount
            player.chips = 0
            player.is_all_in = True
            result["amount"] = all_in_amount

            if player.current_bet > self.current_bet:
                self.current_bet = player.current_bet
                for p in self.players:
                    if p.player_id != player_id and p.is_active:
                        p.has_acted = False

        player.has_acted = True
        print(f"[Action] Player {player_id} {action} completed, calling _next_player()")
        self._next_player()
        print(f"[Action] _next_player() returned, current_player_idx now: {self.current_player_idx}")

        return result

    def _get_player(self, player_id: int) -> Optional[PlayerState]:
        """获取玩家"""
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def get_current_player(self) -> Optional[PlayerState]:
        """获取当前应该行动的玩家"""
        if not self.players:
            return None

        # 如果 current_player_idx 是 -1，表示没有当前玩家（游戏已结束或进入摊牌）
        if self.current_player_idx == -1:
            return None

        # 找到所有活跃且未all-in的玩家
        active_players = [p for p in self.players if p.is_active and not p.is_all_in]

        if len(active_players) == 0:
            return None  # 没有活跃玩家

        if len(active_players) == 1:
            return None  # 只剩一个玩家，无需继续行动

        # 从current_player_idx开始查找需要行动的玩家
        for i in range(len(self.players)):
            idx = (self.current_player_idx + i) % len(self.players)
            player = self.players[idx]

            # 玩家必须是活跃的且未all-in
            if player.is_active and not player.is_all_in:
                # 检查该玩家是否需要行动：
                # 1. 还没有行动过，或
                # 2. 当前下注小于全局下注（需要跟注或加注）
                if not player.has_acted or player.current_bet < self.current_bet:
                    return player

        return None  # 所有玩家都已完成行动

    def _next_player(self):
        """移动到下一个玩家"""
        print(f"[Next] Called from position {self.current_player_idx}, state: {self.state.value}")
        for _ in range(len(self.players)):
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            player = self.players[self.current_player_idx]
            # 玩家需要行动：活跃、未all-in、且(未行动过 或 需要跟注)
            if player.is_active and not player.is_all_in:
                if not player.has_acted or player.current_bet < self.current_bet:
                    print(f"[Next] Moving to player {player.player_id} (position {self.current_player_idx})")
                    return

        # 检查是否进入下一阶段
        print(f"[Next] No next player found, checking if betting round complete...")
        print(f"[Next] Player states: {[(p.player_id, p.is_active, p.is_all_in, p.has_acted, p.current_bet) for p in self.players]}")
        print(f"[Next] Current bet: {self.current_bet}")

        if self._is_betting_round_complete():
            print(f"[Next] Advancing state from {self.state.value}")
            self._advance_state()
        else:
            print(f"[Next] ERROR: Betting round not complete but no next player found!")
            print(f"[Next] This should not happen - setting current_player to -1")
            self.current_player_idx = -1

    def _is_betting_round_complete(self) -> bool:
        """检查下注轮是否结束"""
        active_players = [p for p in self.players if p.is_active and not p.is_all_in]

        if len(active_players) <= 1:
            print(f"[Betting] Round complete: only {len(active_players)} active player(s)")
            return True

        for player in active_players:
            if not player.has_acted:
                print(f"[Betting] Round NOT complete: player {player.player_id} has not acted")
                return False
            if player.current_bet < self.current_bet:
                print(f"[Betting] Round NOT complete: player {player.player_id} bet {player.current_bet} < {self.current_bet}")
                return False

        print(f"[Betting] Round complete: all {len(active_players)} players have acted and matched bet")
        return True

    def _advance_state(self):
        """推进游戏状态"""
        active_count = sum(1 for p in self.players if p.is_active)

        if active_count <= 1:
            print(f"[Advance] Only {active_count} active, moving to FINISHED")
            self.state = GameState.FINISHED
            self.current_player_idx = -1  # 没有当前玩家
        elif self.state == GameState.PREFLOP:
            print(f"[Advance] PREFLOP -> FLOP")
            self.deal_flop()
        elif self.state == GameState.FLOP:
            print(f"[Advance] FLOP -> TURN")
            self.deal_turn()
        elif self.state == GameState.TURN:
            print(f"[Advance] TURN -> RIVER")
            self.deal_river()
        elif self.state == GameState.RIVER:
            print(f"[Advance] RIVER -> SHOWDOWN, setting current_player to -1")
            self.state = GameState.SHOWDOWN
            self.current_player_idx = -1  # 没有当前玩家

    def showdown(self) -> dict:
        """
        摊牌阶段 - 评估所有手牌并确定获胜者

        Returns:
            包含获胜者信息和手牌评估结果的字典
        """
        if self.state != GameState.SHOWDOWN:
            raise ValueError("当前不是摊牌阶段")

        from .hand_evaluator import HandEvaluator

        # 评估所有未弃牌玩家的手牌
        player_hands = []
        for player in self.players:
            if player.is_active or player.is_all_in:
                # 检查玩家是否有底牌
                if not player.hole_cards or len(player.hole_cards) != 2:
                    raise ValueError(f"玩家 {player.player_id} 没有有效的底牌")

                # 检查是否有足够的公共牌
                if len(self.community_cards) < 5:
                    raise ValueError(f"公共牌不足（当前 {len(self.community_cards)} 张，需要 5 张）")

                try:
                    hand_rank, hand_values = HandEvaluator.evaluate_hand(
                        player.hole_cards,
                        self.community_cards
                    )
                    hand_description = HandEvaluator.hand_to_string(hand_rank, hand_values)
                except Exception as e:
                    raise ValueError(f"评估玩家 {player.player_id} 手牌时出错: {str(e)}")

                player_hands.append({
                    "player": player,
                    "rank": hand_rank,
                    "values": hand_values,
                    "description": hand_description
                })

        if not player_hands:
            raise ValueError("没有玩家参与摊牌")

        # 找出获胜者（可能有多个平局）
        player_hands.sort(
            key=lambda x: (x["rank"], x["values"]),
            reverse=True
        )

        winners = [player_hands[0]]
        best_rank = player_hands[0]["rank"]
        best_values = player_hands[0]["values"]

        # 检查是否有平局
        for hand_info in player_hands[1:]:
            result = HandEvaluator.compare_hands(
                (hand_info["rank"], hand_info["values"]),
                (best_rank, best_values)
            )
            if result == 0:  # 平局
                winners.append(hand_info)
            else:
                break  # 已经排序，后面的都更小

        # 分配奖池
        winnings = self._distribute_pot([w["player"] for w in winners])

        # 更新游戏状态
        self.state = GameState.FINISHED

        # 返回结果
        return {
            "winners": [
                {
                    "player_id": w["player"].player_id,
                    "hand_description": w["description"],
                    "hand_rank": w["rank"].name,
                    "hole_cards": [c.to_dict() for c in w["player"].hole_cards],
                    "winnings": winnings[w["player"].player_id]
                }
                for w in winners
            ],
            "all_hands": [
                {
                    "player_id": h["player"].player_id,
                    "hand_description": h["description"],
                    "hand_rank": h["rank"].name,
                    "hole_cards": [c.to_dict() for c in h["player"].hole_cards]
                }
                for h in player_hands
            ],
            "pot": self.pot
        }

    def _distribute_pot(self, winners: List[PlayerState]) -> Dict[int, float]:
        """
        分配奖池给获胜者

        Args:
            winners: 获胜玩家列表

        Returns:
            每个获胜者获得的奖金字典 {player_id: amount}
        """
        winnings = {winner.player_id: 0.0 for winner in winners}

        if not winners:
            return winnings

        # 简单平分（后续可以实现边池逻辑）
        share = self.pot / len(winners)

        for winner in winners:
            winner.chips += share
            winnings[winner.player_id] = share

        # 清空奖池
        self.pot = 0

        return winnings

    def get_state(self, include_hole_cards: bool = False) -> dict:
        """获取游戏状态

        Args:
            include_hole_cards: 是否包含所有玩家的底牌（调试用）
        """
        players_data = []
        for p in self.players:
            player_dict = {
                "player_id": p.player_id,
                "position": p.position,
                "chips": p.chips,
                "current_bet": p.current_bet,
                "is_active": p.is_active,
                "is_all_in": p.is_all_in
            }
            # 如果是调试模式或者游戏结束，包含底牌
            if include_hole_cards or self.state in [GameState.SHOWDOWN, GameState.FINISHED]:
                player_dict["hole_cards"] = [c.to_dict() for c in p.hole_cards]
            players_data.append(player_dict)

        return {
            "game_id": self.game_id,
            "state": self.state.value,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "current_player": self.current_player_idx,
            "dealer": self.dealer_idx,
            "community_cards": [c.to_dict() for c in self.community_cards],
            "players": players_data
        }
