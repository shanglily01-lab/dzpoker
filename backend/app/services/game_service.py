"""游戏数据持久化服务"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..models import Game, Hand, Action, Player, PlayerStats
from ..core.poker import PokerGame, GameState


class GameService:
    """游戏数据持久化服务"""

    @staticmethod
    async def create_game_record(
        db: AsyncSession,
        game: PokerGame
    ) -> Game:
        """
        创建游戏记录

        Args:
            db: 数据库会话
            game: 扑克游戏实例

        Returns:
            Game: 游戏记录
        """
        try:
            game_record = Game(
                game_uuid=game.game_id,
                num_players=len(game.players),
                small_blind=game.small_blind,
                big_blind=game.big_blind,
                total_pot=game.pot,
                status="playing",
                started_at=datetime.utcnow()
            )
            db.add(game_record)
            await db.commit()
            await db.refresh(game_record)
            print(f"[Database] Game {game.game_id} record created")
            return game_record
        except Exception as e:
            # 如果记录已存在（重复key），回滚并查询现有记录
            await db.rollback()
            if "duplicate key" in str(e) or "UniqueViolation" in str(e):
                print(f"[Database] Game {game.game_id} already exists, fetching existing record")
                result = await db.execute(
                    select(Game).where(Game.game_uuid == game.game_id)
                )
                existing_record = result.scalar_one()
                return existing_record
            else:
                # 其他错误继续抛出
                print(f"[Database] Failed to create game record: {e}")
                raise

    @staticmethod
    async def update_game_status(
        db: AsyncSession,
        game_uuid: str,
        status: str,
        winner_id: Optional[int] = None,
        total_pot: Optional[float] = None
    ):
        """
        更新游戏状态

        Args:
            db: 数据库会话
            game_uuid: 游戏UUID
            status: 游戏状态 (playing/finished)
            winner_id: 获胜者ID
            total_pot: 总底池
        """
        result = await db.execute(
            select(Game).where(Game.game_uuid == game_uuid)
        )
        game_record = result.scalar_one_or_none()

        if game_record:
            game_record.status = status
            if winner_id is not None:
                game_record.winner_id = winner_id
            if total_pot is not None:
                game_record.total_pot = total_pot
            if status == "finished":
                game_record.ended_at = datetime.utcnow()

            await db.commit()

    @staticmethod
    async def save_hand(
        db: AsyncSession,
        game_id: int,
        player_id: int,
        position: int,
        hole_cards: str,
        final_hand: Optional[str] = None,
        profit_loss: float = 0.0,
        is_winner: bool = False
    ) -> Hand:
        """
        保存手牌记录

        Args:
            db: 数据库会话
            game_id: 游戏ID
            player_id: 玩家ID
            position: 座位位置
            hole_cards: 底牌字符串 (如 "AhKd")
            final_hand: 最终牌型
            profit_loss: 盈亏
            is_winner: 是否获胜

        Returns:
            Hand: 手牌记录
        """
        hand_record = Hand(
            game_id=game_id,
            player_id=player_id,
            position=position,
            hole_cards=hole_cards,
            final_hand=final_hand,
            profit_loss=profit_loss,
            is_winner=is_winner
        )
        db.add(hand_record)
        await db.commit()
        await db.refresh(hand_record)
        return hand_record

    @staticmethod
    async def save_action(
        db: AsyncSession,
        hand_id: int,
        player_id: int,
        street: str,
        action_type: str,
        amount: float = 0.0,
        pot_size: float = 0.0
    ) -> Action:
        """
        保存玩家动作记录

        Args:
            db: 数据库会话
            hand_id: 手牌ID
            player_id: 玩家ID
            street: 阶段 (preflop/flop/turn/river)
            action_type: 动作类型 (fold/call/raise/check/all_in)
            amount: 金额
            pot_size: 底池大小

        Returns:
            Action: 动作记录
        """
        action_record = Action(
            hand_id=hand_id,
            player_id=player_id,
            street=street.lower(),
            action_type=action_type.lower(),
            amount=amount,
            pot_size=pot_size
        )
        db.add(action_record)
        await db.commit()
        await db.refresh(action_record)
        return action_record

    @staticmethod
    async def update_player_stats(
        db: AsyncSession,
        player_id: int,
        won: bool = False,
        profit: float = 0.0,
        played_hand: bool = True
    ):
        """
        更新玩家统计数据

        Args:
            db: 数据库会话
            player_id: 玩家ID
            won: 是否获胜
            profit: 盈亏
            played_hand: 是否参与了这手牌
        """
        # 获取或创建玩家统计
        result = await db.execute(
            select(PlayerStats).where(PlayerStats.player_id == player_id)
        )
        stats = result.scalar_one_or_none()

        if not stats:
            stats = PlayerStats(
                player_id=player_id,
                total_games=0,
                total_hands=0,
                wins=0,
                vpip=0.0,
                pfr=0.0,
                af=0.0,
                win_rate=0.0,
                total_profit=0.0
            )
            db.add(stats)

        # 更新统计
        if played_hand:
            stats.total_hands += 1

        if won:
            stats.wins += 1

        stats.total_profit += profit

        # 计算胜率
        if stats.total_hands > 0:
            stats.win_rate = (stats.wins / stats.total_hands) * 100

        await db.commit()

    @staticmethod
    async def finish_game(
        db: AsyncSession,
        game: PokerGame,
        winners: List[dict]
    ):
        """
        完成游戏并保存所有数据

        Args:
            db: 数据库会话
            game: 扑克游戏实例
            winners: 获胜者信息列表
        """
        # 获取游戏记录
        result = await db.execute(
            select(Game).where(Game.game_uuid == game.game_id)
        )
        game_record = result.scalar_one_or_none()

        if not game_record:
            # 如果没有游戏记录，创建一个
            game_record = await GameService.create_game_record(db, game)

        # 保存每个玩家的手牌记录
        saved_hands_count = 0
        skipped_players_count = 0
        player_hand_ids = {}  # 记录每个玩家的hand_id，用于后续保存action

        for player in game.players:
            if not player.hole_cards:
                print(f"[GameService] Skipping player {player.player_id} - no hole cards")
                skipped_players_count += 1
                continue

            # 检查是否是获胜者
            is_winner = any(w["player_id"] == player.player_id for w in winners)
            winnings = 0.0

            if is_winner:
                winner_info = next(w for w in winners if w["player_id"] == player.player_id)
                winnings = winner_info["winnings"]

            # 计算盈亏（赢得的筹码 - 总投入）
            profit_loss = winnings - player.total_bet

            # 将底牌转换为字符串格式
            hole_cards_str = "".join([f"{c.rank}{c.suit}" for c in player.hole_cards])

            # 获取最终牌型
            final_hand = None
            if is_winner:
                winner_info = next(w for w in winners if w["player_id"] == player.player_id)
                final_hand = winner_info["hand_description"]

            # 保存手牌记录
            hand_record = await GameService.save_hand(
                db=db,
                game_id=game_record.id,
                player_id=player.player_id,
                position=player.position,
                hole_cards=hole_cards_str,
                final_hand=final_hand,
                profit_loss=profit_loss,
                is_winner=is_winner
            )

            player_hand_ids[player.player_id] = hand_record.id
            saved_hands_count += 1
            print(f"[GameService] Saved hand for player {player.player_id}, hand_id={hand_record.id}")

            # 更新玩家统计（仅限真实玩家，虚拟玩家ID 1-10跳过）
            # 虚拟玩家不需要更新统计数据
            # if player.player_id > 10:  # 假设真实玩家ID > 10
            #     await GameService.update_player_stats(
            #         db=db,
            #         player_id=player.player_id,
            #         won=is_winner,
            #         profit=profit_loss,
            #         played_hand=True
            #     )

        print(f"[GameService] Total hands saved: {saved_hands_count}, skipped: {skipped_players_count}")

        # 保存所有玩家动作
        saved_actions_count = 0
        if hasattr(game, 'action_history') and game.action_history:
            print(f"[GameService] Saving {len(game.action_history)} actions...")
            for action in game.action_history:
                player_id = action["player_id"]
                # 只保存已记录手牌的玩家的动作
                if player_id in player_hand_ids:
                    await GameService.save_action(
                        db=db,
                        hand_id=player_hand_ids[player_id],
                        player_id=player_id,
                        street=action["street"],
                        action_type=action["action"],
                        amount=action["amount"],
                        pot_size=action["pot_after"]
                    )
                    saved_actions_count += 1
            print(f"[GameService] Total actions saved: {saved_actions_count}")
        else:
            print(f"[GameService] No action history to save")

        # 更新游戏状态为已完成
        winner_id = winners[0]["player_id"] if len(winners) == 1 else None
        await GameService.update_game_status(
            db=db,
            game_uuid=game.game_id,
            status="finished",
            winner_id=winner_id,
            total_pot=game.pot
        )
