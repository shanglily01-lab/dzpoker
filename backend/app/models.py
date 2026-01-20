"""数据库模型"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .core.database import Base


class Player(Base):
    """玩家表"""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    nickname = Column(String(50))
    password_hash = Column(String(255), nullable=False)
    chips = Column(Float, default=10000.0)
    level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联
    stats = relationship("PlayerStats", back_populates="player", uselist=False)


class PlayerStats(Base):
    """玩家统计表"""
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), unique=True)
    total_games = Column(Integer, default=0)
    total_hands = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    vpip = Column(Float, default=0.0)  # 入池率
    pfr = Column(Float, default=0.0)   # 翻前加注率
    af = Column(Float, default=0.0)    # 激进因子
    win_rate = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关联
    player = relationship("Player", back_populates="stats")


class Game(Base):
    """游戏记录表"""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    game_uuid = Column(String(36), unique=True, nullable=False, index=True)
    num_players = Column(Integer, nullable=False)
    small_blind = Column(Float, default=1.0)
    big_blind = Column(Float, default=2.0)
    total_pot = Column(Float, default=0.0)
    winner_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    status = Column(String(20), default="waiting")  # waiting, playing, finished
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # 关联
    hands = relationship("Hand", back_populates="game")


class Hand(Base):
    """手牌记录表"""
    __tablename__ = "hands"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer)  # 虚拟玩家ID（不关联players表）
    position = Column(Integer)  # 座位位置 0-9
    hole_cards = Column(String(10))  # 底牌, 如 "AhKd"
    final_hand = Column(String(30))  # 最终牌型
    profit_loss = Column(Float, default=0.0)
    is_winner = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    game = relationship("Game", back_populates="hands")
    actions = relationship("Action", back_populates="hand")


class Action(Base):
    """玩家动作记录表"""
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True)
    hand_id = Column(Integer, ForeignKey("hands.id"))
    player_id = Column(Integer)  # 虚拟玩家ID（不关联players表）
    street = Column(String(20))  # preflop, flop, turn, river
    action_type = Column(String(20))  # fold, call, raise, check, all_in, small_blind, big_blind
    amount = Column(Float, default=0.0)
    pot_size = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联
    hand = relationship("Hand", back_populates="actions")
