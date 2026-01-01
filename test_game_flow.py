"""
测试完整游戏流程脚本
验证从创建游戏到摊牌结束的完整流程
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_complete_game_flow():
    """测试完整游戏流程"""
    print("=== DZPoker 游戏流程测试 ===\n")

    # 1. 创建游戏
    print("1. 创建游戏...")
    response = requests.post(f"{BASE_URL}/games", json={
        "num_players": 3,
        "blind": 10
    })
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"   ✓ 游戏已创建: {game_id}\n")

    # 2. 开始游戏
    print("2. 开始游戏...")
    response = requests.post(f"{BASE_URL}/games/{game_id}/start")
    print(f"   ✓ 游戏已开始\n")

    # 3. 发底牌（使用智能发牌）
    print("3. 发放底牌（智能发牌）...")
    response = requests.post(f"{BASE_URL}/games/{game_id}/deal?smart=true")
    cards_data = response.json()
    print(f"   ✓ 底牌已发放")
    for i, hole_cards in enumerate(cards_data["hole_cards"], 1):
        print(f"     玩家 {i}: {format_cards(hole_cards)}")
    print()

    # 4. 玩家动作 - Preflop
    print("4. 翻牌前（Preflop）下注...")
    game_state = get_game_state(game_id)
    print(f"   当前玩家: 玩家 {game_state['current_player'] + 1}")
    print(f"   底池: {game_state['pot']}")

    # 玩家1: Call
    response = requests.post(f"{BASE_URL}/games/{game_id}/action/1", json={
        "action": "call",
        "amount": 0
    })
    print("   玩家1: Call")

    # 玩家2: Raise
    response = requests.post(f"{BASE_URL}/games/{game_id}/action/2", json={
        "action": "raise",
        "amount": 30
    })
    print("   玩家2: Raise 30")

    # 玩家3: Call
    response = requests.post(f"{BASE_URL}/games/{game_id}/action/3", json={
        "action": "call",
        "amount": 0
    })
    print("   玩家3: Call")

    # 玩家1: Call raise
    response = requests.post(f"{BASE_URL}/games/{game_id}/action/1", json={
        "action": "call",
        "amount": 0
    })
    print("   玩家1: Call\n")

    # 5. 发翻牌
    print("5. 发放翻牌（Flop）...")
    response = requests.post(f"{BASE_URL}/games/{game_id}/flop")
    flop_data = response.json()
    print(f"   ✓ 翻牌: {format_cards(flop_data['cards'])}\n")

    # 6. 翻牌圈下注
    print("6. 翻牌圈下注...")
    # 所有玩家 Check
    for player_id in [1, 2, 3]:
        response = requests.post(f"{BASE_URL}/games/{game_id}/action/{player_id}", json={
            "action": "check"
        })
        print(f"   玩家{player_id}: Check")
    print()

    # 7. 发转牌
    print("7. 发放转牌（Turn）...")
    response = requests.post(f"{BASE_URL}/games/{game_id}/turn")
    turn_data = response.json()
    print(f"   ✓ 转牌: {format_card(turn_data['card'])}\n")

    # 8. 转牌圈下注
    print("8. 转牌圈下注...")
    for player_id in [1, 2, 3]:
        response = requests.post(f"{BASE_URL}/games/{game_id}/action/{player_id}", json={
            "action": "check"
        })
        print(f"   玩家{player_id}: Check")
    print()

    # 9. 发河牌
    print("9. 发放河牌（River）...")
    response = requests.post(f"{BASE_URL}/games/{game_id}/river")
    river_data = response.json()
    print(f"   ✓ 河牌: {format_card(river_data['card'])}\n")

    # 10. 河牌圈下注
    print("10. 河牌圈下注...")
    for player_id in [1, 2, 3]:
        response = requests.post(f"{BASE_URL}/games/{game_id}/action/{player_id}", json={
            "action": "check"
        })
        print(f"   玩家{player_id}: Check")
    print()

    # 11. 摊牌
    print("11. 摊牌（Showdown）...")
    response = requests.post(f"{BASE_URL}/games/{game_id}/showdown")
    showdown_data = response.json()

    print(f"\n   === 摊牌结果 ===")
    print(f"   底池: {showdown_data['pot']}\n")

    print("   所有玩家手牌:")
    for hand in showdown_data['all_hands']:
        player_id = hand['player_id']
        hand_desc = hand['hand_description']
        hole_cards = format_cards(hand['hole_cards'])
        print(f"   玩家 {player_id}: {hole_cards} - {hand_desc}")

    print(f"\n   🏆 获胜者:")
    for winner in showdown_data['winners']:
        print(f"   玩家 {winner['player_id']}: {winner['hand_description']}")
        print(f"   赢得: {winner['winnings']} 筹码")

    print("\n=== 测试完成 ===\n")

    return True


def get_game_state(game_id):
    """获取游戏状态"""
    response = requests.get(f"{BASE_URL}/games/{game_id}")
    return response.json()


def format_card(card):
    """格式化单张牌"""
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    return ranks[card['rank']] + suits[card['suit']]


def format_cards(cards):
    """格式化多张牌"""
    return ' '.join([format_card(card) for card in cards])


def test_hand_evaluator():
    """测试牌型评估器"""
    print("=== 测试牌型评估器 ===\n")

    from backend.app.core.poker import Card
    from backend.app.core.hand_evaluator import HandEvaluator, HandRank

    # 测试各种牌型
    test_cases = [
        {
            "name": "皇家同花顺",
            "hole": [Card('A', 0), Card('K', 0)],
            "community": [Card('Q', 0), Card('J', 0), Card('T', 0), Card('9', 0), Card('2', 1)],
            "expected": HandRank.ROYAL_FLUSH
        },
        {
            "name": "同花顺",
            "hole": [Card('9', 1), Card('8', 1)],
            "community": [Card('7', 1), Card('6', 1), Card('5', 1), Card('A', 0), Card('K', 0)],
            "expected": HandRank.STRAIGHT_FLUSH
        },
        {
            "name": "四条",
            "hole": [Card('A', 0), Card('A', 1)],
            "community": [Card('A', 2), Card('A', 3), Card('K', 0), Card('Q', 0), Card('J', 0)],
            "expected": HandRank.FOUR_OF_KIND
        },
        {
            "name": "葫芦",
            "hole": [Card('K', 0), Card('K', 1)],
            "community": [Card('K', 2), Card('Q', 0), Card('Q', 1), Card('J', 0), Card('T', 0)],
            "expected": HandRank.FULL_HOUSE
        },
        {
            "name": "同花",
            "hole": [Card('A', 0), Card('K', 0)],
            "community": [Card('Q', 0), Card('J', 0), Card('9', 0), Card('2', 1), Card('3', 1)],
            "expected": HandRank.FLUSH
        },
        {
            "name": "顺子",
            "hole": [Card('A', 0), Card('K', 1)],
            "community": [Card('Q', 2), Card('J', 3), Card('T', 0), Card('2', 1), Card('3', 1)],
            "expected": HandRank.STRAIGHT
        },
        {
            "name": "三条",
            "hole": [Card('A', 0), Card('A', 1)],
            "community": [Card('A', 2), Card('K', 0), Card('Q', 1), Card('J', 0), Card('T', 0)],
            "expected": HandRank.THREE_OF_KIND
        },
        {
            "name": "两对",
            "hole": [Card('A', 0), Card('A', 1)],
            "community": [Card('K', 2), Card('K', 0), Card('Q', 1), Card('J', 0), Card('T', 0)],
            "expected": HandRank.TWO_PAIR
        },
        {
            "name": "一对",
            "hole": [Card('A', 0), Card('A', 1)],
            "community": [Card('K', 2), Card('Q', 0), Card('J', 1), Card('T', 0), Card('9', 0)],
            "expected": HandRank.ONE_PAIR
        }
    ]

    for test in test_cases:
        rank, values = HandEvaluator.evaluate_hand(test["hole"], test["community"])
        description = HandEvaluator.hand_to_string(rank, values)
        status = "✓" if rank == test["expected"] else "✗"
        print(f"{status} {test['name']}: {description} (期望: {test['expected'].name})")

    print("\n=== 测试完成 ===\n")


if __name__ == "__main__":
    print("\n开始测试...\n")

    # 测试牌型评估器
    try:
        test_hand_evaluator()
    except Exception as e:
        print(f"牌型评估器测试失败: {e}\n")

    # 等待用户确认后再测试完整流程
    input("按 Enter 键开始测试完整游戏流程（需要后端服务运行）...")

    try:
        test_complete_game_flow()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到后端服务")
        print("请确保后端服务运行在 http://localhost:8000")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
