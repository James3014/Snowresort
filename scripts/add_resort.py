#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新增雪場互動式工具 - 極簡 v0 版本
"""

import json
import sys
from datetime import date


def load_resorts():
    """載入現有雪場資料"""
    try:
        with open('data/resorts.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  找不到 data/resorts.json，將建立新檔案")
        return []


def save_resorts(resorts):
    """儲存雪場資料"""
    with open('data/resorts.json', 'w', encoding='utf-8') as f:
        json.dump(resorts, f, ensure_ascii=False, indent=2)


def get_input(prompt, default=None, required=True):
    """取得使用者輸入"""
    if default:
        full_prompt = f"{prompt} (預設: {default}): "
    else:
        full_prompt = f"{prompt}: "

    while True:
        value = input(full_prompt).strip()
        if value:
            return value
        elif default is not None:
            return default
        elif not required:
            return None
        else:
            print("❌ 此欄位為必填，請輸入內容")


def get_int_input(prompt, default=None, min_val=None, max_val=None):
    """取得整數輸入"""
    while True:
        try:
            value = get_input(prompt, default, required=(default is None))
            if value is None:
                return None
            num = int(value)
            if min_val is not None and num < min_val:
                print(f"❌ 數值不可小於 {min_val}")
                continue
            if max_val is not None and num > max_val:
                print(f"❌ 數值不可大於 {max_val}")
                continue
            return num
        except ValueError:
            print("❌ 請輸入有效的數字")


def add_resort_interactive():
    """互動式新增雪場"""
    print("\n" + "=" * 70)
    print("  新增雪場 - 互動式輸入")
    print("=" * 70)
    print("\n提示：按 Ctrl+C 可隨時取消\n")

    resort = {}

    # 基本資訊
    print("📍 基本資訊")
    print("-" * 70)
    resort['id'] = get_input("雪場 ID（英文小寫，用 - 分隔）", example="hakuba-happo")
    resort['name'] = get_input("雪場日文名稱")
    resort['name_en'] = get_input("雪場英文名稱", required=False)
    resort['region'] = get_input("地區 (hokkaido/tohoku/niigata/nagano/gunma/other)", "hokkaido")
    resort['prefecture'] = get_input("都道府縣", "北海道")
    resort['city'] = get_input("城市", required=False)

    # 評分與核心屬性
    print("\n⭐ 評分與核心屬性（1-5，僅整數）")
    print("-" * 70)
    resort['price'] = get_input("價位等級 (budget/mid/premium)", "mid")
    resort['family_score'] = get_int_input("親子友善度 (1-5，僅整數)", min_val=1, max_val=5)
    resort['beginner_score'] = get_int_input("初學者友善度 (1-5，僅整數)", min_val=1, max_val=5)
    resort['kids_area'] = get_input("是否有兒童專區/雪遊區？(y/n)", "n").lower() == 'y'
    resort['coach_available'] = get_input("是否允許教練進場授課？(y/n)", "y").lower() == 'y'

    # 交通時間
    print("\n🚗 交通時間（分鐘）")
    print("-" * 70)
    print("⚠️  僅使用標準城市 key（小寫英文）：")
    print("   tokyo, osaka, nagoya, sapporo, asahikawa_city, asahikawa_airport, nagano")
    resort['travel'] = {}
    cities = ['tokyo', 'osaka', 'nagoya', 'sapporo', 'asahikawa_city', 'asahikawa_airport', 'nagano']

    print("\n輸入從各城市的交通時間（直接按 Enter 跳過該城市）：")
    print("至少需要填入 1 個主要城市")
    for city in cities:
        minutes = get_int_input(f"  從 {city} 的時間（分鐘）", required=False, min_val=0)
        if minutes:
            resort['travel'][city] = minutes

    if not resort['travel']:
        print("⚠️  警告：未填入任何交通時間，請至少填入一個主要城市")
        city = get_input("  請填入一個城市 key", "tokyo")
        minutes = get_int_input(f"  從 {city} 的時間（分鐘）", min_val=0)
        resort['travel'][city] = minutes

    # 目標客群標籤
    print("\n🏷️  目標客群標籤（結構化）")
    print("-" * 70)
    print("可用標籤: family, beginner, intermediate, advanced, backcountry, park, powder")
    tags_input = get_input("標籤（用逗號分隔）", "family,beginner")
    resort['audience_tags'] = [t.strip() for t in tags_input.split(",") if t.strip()]

    # 雪場統計（選填）
    print("\n📊 雪場統計（選填，直接按 Enter 跳過）")
    print("-" * 70)
    add_stats = get_input("是否新增雪場統計資料？(y/n)", "n").lower() == 'y'

    if add_stats:
        resort['stats'] = {}
        resort['stats']['trails'] = get_int_input("  雪道總數", required=False, min_val=0)
        resort['stats']['beginner_trails'] = get_int_input("  初級雪道數", required=False, min_val=0)
        resort['stats']['beginner_percentage'] = get_int_input("  初級雪道比例 (%)", required=False, min_val=0, max_val=100)
        resort['stats']['vertical_drop'] = get_int_input("  垂直落差 (米)", required=False, min_val=0)
        resort['stats']['longest_run'] = get_int_input("  最長滑道 (米)", required=False, min_val=0)

    # 設施（Tier 2）
    print("\n🏗️  設施（Tier 2，選填）")
    print("-" * 70)
    resort['facilities'] = {}
    resort['facilities']['kids_school'] = get_input("  有兒童雪校？(y/n)", "n").lower() == 'y'
    resort['facilities']['rental_shop'] = get_input("  有租借店？(y/n)", "y").lower() == 'y'

    # 特色亮點
    print("\n✨ 特色亮點")
    print("-" * 70)
    print("輸入雪場特色（每行一個，輸入空白行結束）：")
    highlights = []
    while True:
        highlight = input("  • ").strip()
        if not highlight:
            break
        highlights.append(highlight)
    if highlights:
        resort['highlights'] = highlights

    # 備註
    print("\n📝 備註")
    print("-" * 70)
    notes = get_input("備註說明", required=False)
    if notes:
        resort['notes'] = notes

    # 後設資料
    resort['data_source'] = {
        'manual_inspection': True
    }
    resort['last_updated'] = str(date.today())
    resort['data_quality'] = 'partial'

    # 確認並儲存
    print("\n" + "=" * 70)
    print("  資料預覽")
    print("=" * 70)
    print(json.dumps(resort, ensure_ascii=False, indent=2))
    print("=" * 70)

    confirm = get_input("\n確定要新增這個雪場嗎？(y/n)", "y").lower()
    if confirm != 'y':
        print("❌ 已取消新增")
        return None

    # 載入現有資料並新增
    resorts = load_resorts()

    # 檢查 ID 是否已存在
    if any(r['id'] == resort['id'] for r in resorts):
        print(f"❌ 雪場 ID '{resort['id']}' 已存在")
        overwrite = get_input("是否要覆蓋現有資料？(y/n)", "n").lower()
        if overwrite == 'y':
            resorts = [r for r in resorts if r['id'] != resort['id']]
        else:
            print("❌ 已取消新增")
            return None

    resorts.append(resort)
    save_resorts(resorts)

    print(f"\n✅ 成功新增雪場：{resort['name']}")
    print(f"   ID: {resort['id']}")
    print(f"   總雪場數: {len(resorts)}")

    return resort


def add_resort_from_args():
    """從命令列參數快速新增雪場（簡化版）"""
    if len(sys.argv) < 8:
        print("❌ 參數不足")
        print("\n使用方式:")
        print("  python scripts/add_resort.py quick <id> <name> <region> <price> <family_score> <beginner_score>")
        print("\n範例:")
        print("  python scripts/add_resort.py quick niseko-grand-hirafu 'ニセコグラン・ヒラフ' hokkaido premium 3 2")
        return None

    resort = {
        'id': sys.argv[2],
        'name': sys.argv[3],
        'region': sys.argv[4],
        'prefecture': '北海道' if sys.argv[4] == 'hokkaido' else sys.argv[4],
        'price': sys.argv[5],
        'family_score': int(sys.argv[6]),
        'beginner_score': int(sys.argv[7]),
        'kids_area': False,
        'coach_available': True,
        'travel': {},
        'audience_tags': [],
        'facilities': {
            'kids_school': False
        },
        'data_source': {'manual_inspection': True},
        'last_updated': str(date.today()),
        'data_quality': 'needs_review'
    }

    resorts = load_resorts()

    # 檢查重複
    if any(r['id'] == resort['id'] for r in resorts):
        print(f"❌ 雪場 ID '{resort['id']}' 已存在")
        return None

    resorts.append(resort)
    save_resorts(resorts)

    print(f"✅ 成功新增雪場：{resort['name']} (ID: {resort['id']})")
    print(f"   總雪場數: {len(resorts)}")
    print("⚠️  請使用互動模式補充完整資訊")

    return resort


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "quick":
            add_resort_from_args()
        else:
            add_resort_interactive()
    except KeyboardInterrupt:
        print("\n\n❌ 已取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
