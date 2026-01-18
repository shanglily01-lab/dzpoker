-- 删除外键约束，允许虚拟玩家ID
-- 这个脚本需要在数据库中执行

-- 删除 hands 表的 player_id 外键约束
ALTER TABLE hands DROP CONSTRAINT IF EXISTS hands_player_id_fkey;

-- 删除 actions 表的 player_id 外键约束
ALTER TABLE actions DROP CONSTRAINT IF EXISTS actions_player_id_fkey;

-- 验证外键已删除
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint
WHERE contype = 'f'
AND (conrelid = 'hands'::regclass OR conrelid = 'actions'::regclass);
