#!/usr/bin/env python3
"""
测试自动游戏功能
Test the automatic game simulation end-to-end
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

def test_auto_game():
    """测试完整的自动游戏流程"""
    print("=" * 60)
    print("🎮 测试自动游戏模拟")
    print("=" * 60)

    # 1. 创建游戏
    print("\n1️⃣ 创建游戏...")
    response = requests.post(f"{BASE_URL}/games", json={
        "num_players": 6,
        "small_blind": 10,
        "big_blind": 20
    })

    if response.status_code != 200:
        print(f"❌ 创建游戏失败: {response.status_code}")
        print(response.text)
        return False

    game_data = response.json()
    game_id = game_data.get("game_id")
    print(f"✅ 游戏创建成功! Game ID: {game_id}")

    # 2. 运行自动模拟
    print("\n2️⃣ 开始自动模拟 (2倍速)...")
    start_time = time.time()

    response = requests.post(
        f"{BASE_URL}/simulation/{game_id}/auto-play",
        params={"speed": 2.0}
    )

    elapsed = time.time() - start_time

    if response.status_code != 200:
        print(f"❌ 自动模拟失败: {response.status_code}")
        print(response.text)
        return False

    result = response.json()
    print(f"✅ 自动模拟完成! 用时: {elapsed:.2f}秒")

    # 3. 分析游戏日志
    print("\n3️⃣ 游戏日志分析:")
    game_log = result.get("game_log", {})
    actions = game_log.get("actions", [])
    winners = game_log.get("winners", [])

    print(f"   总动作数: {len(actions)}")

    # 统计各类型动作
    action_types = {}
    for action in actions:
        action_type = action.get("type", "unknown")
        action_types[action_type] = action_types.get(action_type, 0) + 1

    print("\n   动作统计:")
    for action_type, count in sorted(action_types.items()):
        print(f"   - {action_type}: {count}")

    # 显示前10个动作
    print("\n   前10个动作:")
    for i, action in enumerate(actions[:10], 1):
        action_type = action.get("type")
        if action_type == "player_action":
            player_id = action.get("player_id")
            player_type = action.get("player_type")
            action_name = action.get("action")
            amount = action.get("amount", 0)
            pot = action.get("pot", 0)
            print(f"   {i}. 玩家 P{player_id} ({player_type}): {action_name} {amount} | 底池: {pot}")
        elif action_type == "flop_dealt":
            cards = action.get("cards", [])
            card_str = " ".join([f"{c['rank']}{c['suit']}" for c in cards])
            print(f"   {i}. 翻牌: {card_str}")
        elif action_type in ["turn_dealt", "river_dealt"]:
            card = action.get("card", {})
            print(f"   {i}. {action_type.split('_')[0].upper()}: {card.get('rank')}{card.get('suit')}")
        else:
            print(f"   {i}. {action_type}")

    # 显示获胜者
    print(f"\n4️⃣ 获胜者: ({len(winners)}人)")
    for winner in winners:
        player_id = winner.get("player_id")
        hand_desc = winner.get("hand_description")
        winnings = winner.get("winnings")
        print(f"   🏆 玩家 P{player_id}: {hand_desc} - 赢得 {winnings} 筹码")

    # 5. 验证最终游戏状态
    print("\n5️⃣ 验证最终游戏状态...")
    final_state = result.get("final_state", {})

    state = final_state.get("state")
    pot = final_state.get("pot")
    print(f"   游戏状态: {state}")
    print(f"   最终底池: {pot}")

    # 检查是否有获胜者
    if not winners:
        print("   ⚠️ 警告: 没有获胜者!")
        return False

    print("\n✅ 自动游戏测试通过!")
    return True


def test_single_action():
    """测试单步AI动作"""
    print("\n" + "=" * 60)
    print("🎮 测试单步AI动作")
    print("=" * 60)

    # 1. 创建游戏
    print("\n1️⃣ 创建游戏...")
    response = requests.post(f"{BASE_URL}/games", json={
        "num_players": 4,
        "small_blind": 5,
        "big_blind": 10
    })

    if response.status_code != 200:
        print(f"❌ 创建游戏失败")
        return False

    game_data = response.json()
    game_id = game_data.get("game_id")
    print(f"✅ 游戏创建成功! Game ID: {game_id}")

    # 2. 开始游戏
    print("\n2️⃣ 开始游戏...")
    response = requests.post(f"{BASE_URL}/games/{game_id}/start")
    if response.status_code != 200:
        print(f"❌ 开始游戏失败")
        return False
    print("✅ 游戏已开始")

    # 3. 发底牌
    print("\n3️⃣ 发底牌...")
    response = requests.post(f"{BASE_URL}/games/{game_id}/deal")
    if response.status_code != 200:
        print(f"❌ 发牌失败")
        return False
    print("✅ 底牌已发放")

    # 4. 测试3次单步AI动作
    print("\n4️⃣ 测试单步AI动作...")
    for i in range(3):
        print(f"\n   第 {i+1} 步:")
        response = requests.post(f"{BASE_URL}/simulation/{game_id}/single-action")

        if response.status_code != 200:
            print(f"   ⚠️ AI动作失败: {response.status_code}")
            print(f"   {response.text}")
            break

        result = response.json()
        player_id = result.get("player_id")
        player_type = result.get("player_type")
        action = result.get("action")
        amount = result.get("amount", 0)

        print(f"   ✅ 玩家 P{player_id} ({player_type}): {action} {amount}")

    print("\n✅ 单步AI动作测试完成!")
    return True


if __name__ == "__main__":
    try:
        print("\n🚀 开始测试...")

        # 测试1: 完整自动游戏
        success1 = test_auto_game()

        # 测试2: 单步AI动作
        success2 = test_single_action()

        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print(f"自动游戏测试: {'✅ 通过' if success1 else '❌ 失败'}")
        print(f"单步AI测试: {'✅ 通过' if success2 else '❌ 失败'}")

        if success1 and success2:
            print("\n🎉 所有测试通过!")
        else:
            print("\n⚠️ 部分测试失败，请检查日志")

    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器!")
        print("请确保后端服务正在运行 (http://localhost:8000)")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
