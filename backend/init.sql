-- 初始化数据库脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 注意: 表结构由SQLAlchemy自动创建
-- 这里只放一些初始化数据

-- 插入测试玩家
INSERT INTO players (username, nickname, password_hash, chips, level)
VALUES
    ('player1', '玩家1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.T5Q5vL5FvKj.Pu', 10000, 1),
    ('player2', '玩家2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.T5Q5vL5FvKj.Pu', 10000, 1),
    ('player3', '玩家3', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.T5Q5vL5FvKj.Pu', 10000, 1)
ON CONFLICT (username) DO NOTHING;

-- 插入玩家统计
INSERT INTO player_stats (player_id, total_games, total_hands, wins, vpip, pfr, af, win_rate)
SELECT id, 0, 0, 0, 0, 0, 0, 0
FROM players
ON CONFLICT (player_id) DO NOTHING;
