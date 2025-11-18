#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神居滑雪場資料查詢工具 - 極簡 v0 版本
支援 5 個核心查詢問題
"""

import json
from typing import List, Dict, Optional


def load_resorts() -> List[Dict]:
    """載入雪場資料"""
    with open('data/resorts.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def save_resorts(resorts: List[Dict]):
    """儲存雪場資料"""
    with open('data/resorts.json', 'w', encoding='utf-8') as f:
        json.dump(resorts, f, ensure_ascii=False, indent=2)


# ===== 核心查詢功能 =====

def find_family_friendly(min_score: int = 4) -> List[Dict]:
    """
    Q1: 找出親子友善的雪場

    Args:
        min_score: 最低親子友善度分數 (1-5)

    Returns:
        符合條件的雪場列表
    """
    resorts = load_resorts()
    results = [r for r in resorts if r['family_score'] >= min_score]

    print(f"\n📍 親子友善雪場（最低分數 {min_score}）：")
    print("=" * 60)
    for r in results:
        print(f"✓ {r['name']} ({r['name_en']})")
        print(f"  親子友善度: {r['family_score']}/5")
        print(f"  有兒童專區: {'是' if r.get('kids_area', False) else '否'}")
        print(f"  有兒童雪校: {'是' if r.get('facilities', {}).get('kids_school', False) else '否'}")
        print(f"  地區: {r['prefecture']} {r.get('city', '')}")
        print()

    return results


def find_similar(resort_id: str, top_n: int = 5) -> List[Dict]:
    """
    Q2: 找出與指定雪場相似的其他雪場

    使用簡單的相似度計算：
    - 地區相同 +1 分
    - 價位相同 +1 分
    - 標籤重疊每個 +1 分

    Args:
        resort_id: 目標雪場 ID
        top_n: 返回前 N 個相似雪場

    Returns:
        相似雪場列表，按相似度排序
    """
    resorts = load_resorts()
    target = next((r for r in resorts if r['id'] == resort_id), None)

    if not target:
        print(f"\n❌ 找不到雪場 ID: {resort_id}")
        return []

    def calc_similarity(r: Dict) -> int:
        if r['id'] == resort_id:
            return -1

        score = 0
        if r['region'] == target['region']:
            score += 1
        if r['price'] == target['price']:
            score += 1
        score += len(set(r['audience_tags']) & set(target['audience_tags']))

        return score

    similar = sorted(resorts, key=calc_similarity, reverse=True)[:top_n]

    print(f"\n🔍 與「{target['name']}」相似的雪場：")
    print("=" * 60)
    print(f"目標雪場: {target['name']} ({target['name_en']})")
    print(f"地區: {target['region']} | 價位: {target['price']} | 標籤: {', '.join(target['audience_tags'][:3])}")
    print("\n相似雪場：")
    for i, r in enumerate(similar, 1):
        if r['id'] == resort_id:
            continue
        similarity = calc_similarity(r)
        print(f"{i}. {r['name']} ({r['name_en']})")
        print(f"   相似度: {similarity} | 地區: {r['region']} | 價位: {r['price']}")
        print()

    return similar


def filter_by_price(level: str) -> List[Dict]:
    """
    Q3: 根據價位篩選雪場

    Args:
        level: 價位等級 (budget/mid/premium)

    Returns:
        符合價位的雪場列表
    """
    resorts = load_resorts()
    results = [r for r in resorts if r['price'] == level]

    price_labels = {
        'budget': '經濟型（< ¥4,000）',
        'mid': '中價位（¥4,000-6,000）',
        'premium': '高價位（> ¥6,000）'
    }

    print(f"\n💰 {price_labels.get(level, level)} 雪場：")
    print("=" * 60)
    for r in results:
        print(f"✓ {r['name']} ({r['name_en']})")
        if 'prices_2024_25' in r:
            print(f"  一日券: 成人 ¥{r['prices_2024_25'].get('all_day_adult', 'N/A')}")
        print(f"  地區: {r['prefecture']}")
        print()

    return results


def filter_by_travel_time(city: str, max_minutes: int) -> List[Dict]:
    """
    Q4: 根據從指定城市的交通時間篩選雪場

    Args:
        city: 出發城市（如 'tokyo', 'sapporo', 'asahikawa_city'）
        max_minutes: 最長可接受的交通時間（分鐘）

    Returns:
        符合條件的雪場列表
    """
    resorts = load_resorts()
    results = []

    for r in resorts:
        if city in r['travel'] and r['travel'][city] <= max_minutes:
            results.append(r)

    print(f"\n🚗 從 {city} 出發 {max_minutes} 分鐘內可達的雪場：")
    print("=" * 60)
    for r in results:
        print(f"✓ {r['name']} ({r['name_en']})")
        print(f"  交通時間: {r['travel'].get(city, 'N/A')} 分鐘")
        if 'access' in r and city.replace('_', '_') in str(r['access']):
            for key, info in r['access'].items():
                if city in key:
                    print(f"  方式: {info.get('method', 'N/A')}")
                    break
        print()

    return results


def find_beginner_friendly(min_score: int = 4) -> List[Dict]:
    """
    Q5: 找出適合初學者的雪場（教練需求）

    Args:
        min_score: 最低初學者友善度分數 (1-5)

    Returns:
        符合條件的雪場列表
    """
    resorts = load_resorts()
    results = [r for r in resorts if r['beginner_score'] >= min_score]

    print(f"\n🎿 初學者友善雪場（最低分數 {min_score}）：")
    print("=" * 60)
    for r in results:
        print(f"✓ {r['name']} ({r['name_en']})")
        print(f"  初學者友善度: {r['beginner_score']}/5")
        if 'stats' in r:
            print(f"  初級雪道: {r['stats'].get('beginner_trails', 'N/A')} 條 ({r['stats'].get('beginner_percentage', 'N/A')}%)")
        print(f"  教練可進場: {'是' if r.get('coach_available', False) else '否'}")
        print()

    return results


# ===== 進階查詢功能 =====

def get_resort_detail(resort_id: str):
    """顯示雪場詳細資訊"""
    resorts = load_resorts()
    resort = next((r for r in resorts if r['id'] == resort_id), None)

    if not resort:
        print(f"\n❌ 找不到雪場 ID: {resort_id}")
        return None

    print(f"\n{'=' * 70}")
    print(f"  {resort['name']} ({resort['name_en']})")
    print(f"{'=' * 70}")
    print(f"\n📍 基本資訊")
    print(f"  地區: {resort['prefecture']} {resort.get('city', '')}")
    print(f"  價位等級: {resort['price']}")
    print(f"  親子友善度: {resort['family_score']}/5")
    print(f"  初學者友善度: {resort['beginner_score']}/5")

    if 'stats' in resort:
        print(f"\n📊 雪場統計")
        stats = resort['stats']
        print(f"  雪道總數: {stats.get('trails', 'N/A')} 條")
        print(f"  初級雪道: {stats.get('beginner_trails', 'N/A')} 條 ({stats.get('beginner_percentage', 'N/A')}%)")
        print(f"  垂直落差: {stats.get('vertical_drop', 'N/A')} 米")
        print(f"  最長滑道: {stats.get('longest_run', 'N/A')} 米")

    if 'prices_2024_25' in resort:
        print(f"\n💰 雪票價格 (2024-25雪季)")
        prices = resort['prices_2024_25']
        print(f"  一日券: 成人 ¥{prices.get('all_day_adult', 'N/A')} / 兒童 ¥{prices.get('all_day_child', 'N/A')}")
        print(f"  4小時券: 成人 ¥{prices.get('4hour_adult', 'N/A')} / 兒童 ¥{prices.get('4hour_child', 'N/A')}")

    if 'highlights' in resort:
        print(f"\n✨ 特色亮點")
        for highlight in resort['highlights'][:5]:
            print(f"  • {highlight}")

    if 'notes' in resort:
        print(f"\n📝 備註")
        print(f"  {resort['notes']}")

    print(f"\n{'=' * 70}\n")
    return resort


def list_all_resorts():
    """列出所有雪場"""
    resorts = load_resorts()

    print(f"\n📋 雪場列表（共 {len(resorts)} 個）")
    print("=" * 60)
    for r in resorts:
        print(f"• {r['id']}")
        print(f"  {r['name']} ({r['name_en']})")
        print(f"  {r['prefecture']} | 價位: {r['price']} | 親子: {r['family_score']}/5 | 初學: {r['beginner_score']}/5")
        print()


# ===== 主程式 =====

if __name__ == "__main__":
    import sys

    print("\n" + "=" * 70)
    print("  神居滑雪場資料查詢系統 v0.1")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\n使用方式:")
        print("  python scripts/query.py <command> [args]")
        print("\n可用指令:")
        print("  list                          - 列出所有雪場")
        print("  detail <resort_id>            - 顯示雪場詳細資訊")
        print("  family [min_score]            - 找親子友善雪場（預設 4）")
        print("  beginner [min_score]          - 找初學者友善雪場（預設 4）")
        print("  similar <resort_id> [top_n]   - 找相似雪場（預設前 5 個）")
        print("  price <level>                 - 依價位篩選 (budget/mid/premium)")
        print("  travel <city> <max_minutes>   - 依交通時間篩選")
        print("\n範例:")
        print("  python scripts/query.py list")
        print("  python scripts/query.py detail kamui-ski-links")
        print("  python scripts/query.py family 4")
        print("  python scripts/query.py similar kamui-ski-links 3")
        print("  python scripts/query.py price mid")
        print("  python scripts/query.py travel asahikawa_city 60")
        sys.exit(0)

    command = sys.argv[1]

    try:
        if command == "list":
            list_all_resorts()

        elif command == "detail":
            if len(sys.argv) < 3:
                print("❌ 請提供雪場 ID")
                sys.exit(1)
            get_resort_detail(sys.argv[2])

        elif command == "family":
            min_score = int(sys.argv[2]) if len(sys.argv) > 2 else 4
            find_family_friendly(min_score)

        elif command == "beginner":
            min_score = int(sys.argv[2]) if len(sys.argv) > 2 else 4
            find_beginner_friendly(min_score)

        elif command == "similar":
            if len(sys.argv) < 3:
                print("❌ 請提供雪場 ID")
                sys.exit(1)
            resort_id = sys.argv[2]
            top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            find_similar(resort_id, top_n)

        elif command == "price":
            if len(sys.argv) < 3:
                print("❌ 請提供價位等級 (budget/mid/premium)")
                sys.exit(1)
            filter_by_price(sys.argv[2])

        elif command == "travel":
            if len(sys.argv) < 4:
                print("❌ 請提供城市和最大時間")
                print("範例: python scripts/query.py travel asahikawa_city 60")
                sys.exit(1)
            filter_by_travel_time(sys.argv[2], int(sys.argv[3]))

        else:
            print(f"❌ 未知的指令: {command}")
            print("使用 'python scripts/query.py' 查看可用指令")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
