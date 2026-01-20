-- 增加 actions 表字段长度以支持 'small_blind' 等较长的动作类型
-- 问题: action_type VARCHAR(10) 无法存储 'small_blind' (11个字符)
-- 解决: 将 action_type 和 street 增加到 VARCHAR(20)

-- 修改 street 字段长度
ALTER TABLE actions ALTER COLUMN street TYPE VARCHAR(20);

-- 修改 action_type 字段长度
ALTER TABLE actions ALTER COLUMN action_type TYPE VARCHAR(20);

-- 验证修改
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'actions'
AND column_name IN ('street', 'action_type');
