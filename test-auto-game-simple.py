#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test automatic game simulation
"""
import requests
import time
import json
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api"

def test_auto_game():
    """Test complete auto-game flow"""
    print("="* 60)
    print("Test Auto Game Simulation")
    print("=" * 60)

    # 1. Create game
    print("\n[1] Creating game...")
    try:
        response = requests.post(f"{BASE_URL}/games", json={
            "num_players": 6,
            "small_blind": 10,
            "big_blind": 20
        }, timeout=5)

        if response.status_code != 200:
            print(f"[ERROR] Failed to create game: {response.status_code}")
            print(response.text)
            return False

        game_data = response.json()
        game_id = game_data.get("game_id")
        print(f"[OK] Game created! ID: {game_id}")
    except Exception as e:
        print(f"[ERROR] Cannot create game: {e}")
        return False

    # 2. Run auto simulation
    print("\n[2] Starting auto simulation (2x speed)...")
    start_time = time.time()

    try:
        response = requests.post(
            f"{BASE_URL}/simulation/{game_id}/auto-play",
            params={"speed": 2.0},
            timeout=30
        )

        elapsed = time.time() - start_time

        if response.status_code != 200:
            print(f"[ERROR] Auto simulation failed: {response.status_code}")
            print(response.text)
            return False

        result = response.json()
        print(f"[OK] Simulation completed in {elapsed:.2f}s")

        # 3. Analyze game log
        print("\n[3] Game Log Analysis:")
        game_log = result.get("game_log", {})
        actions = game_log.get("actions", [])
        winners = game_log.get("winners", [])

        print(f"   Total actions: {len(actions)}")

        # Count action types
        action_types = {}
        for action in actions:
            action_type = action.get("type", "unknown")
            action_types[action_type] = action_types.get(action_type, 0) + 1

        print("\n   Action statistics:")
        for action_type, count in sorted(action_types.items()):
            print(f"   - {action_type}: {count}")

        # Show first 10 actions
        print("\n   First 10 actions:")
        for i, action in enumerate(actions[:10], 1):
            action_type = action.get("type")
            if action_type == "player_action":
                player_id = action.get("player_id")
                player_type = action.get("player_type", "?")
                action_name = action.get("action")
                amount = action.get("amount", 0)
                pot = action.get("pot", 0)
                print(f"   {i}. Player P{player_id} ({player_type}): {action_name} {amount} | Pot: {pot}")
            elif action_type == "flop_dealt":
                cards = action.get("cards", [])
                card_str = " ".join([f"{c['rank']}{c['suit']}" for c in cards])
                print(f"   {i}. Flop: {card_str}")
            elif action_type in ["turn_dealt", "river_dealt"]:
                card = action.get("card", {})
                print(f"   {i}. {action_type.split('_')[0].upper()}: {card.get('rank')}{card.get('suit')}")
            else:
                print(f"   {i}. {action_type}")

        # Show winners
        print(f"\n[4] Winners ({len(winners)}):")
        for winner in winners:
            player_id = winner.get("player_id")
            hand_desc = winner.get("hand_description", "?")
            winnings = winner.get("winnings", 0)
            print(f"   [WIN] Player P{player_id}: {hand_desc} - Won {winnings} chips")

        # Check winners exist
        if not winners:
            print("   [WARNING] No winners found!")
            return False

        print("\n[OK] Auto-game test PASSED!")
        return True

    except requests.exceptions.Timeout:
        print(f"[ERROR] Request timeout after 30 seconds")
        return False
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        print("\nStarting tests...\n")
        success = test_auto_game()

        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        print(f"Auto-game test: {'PASSED' if success else 'FAILED'}")

        if success:
            print("\n[SUCCESS] All tests passed!")
            sys.exit(0)
        else:
            print("\n[FAILED] Some tests failed!")
            sys.exit(1)

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server!")
        print("Please ensure backend is running at http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
