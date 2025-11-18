# Linus 式代碼審查：雪場資料清洗專案

> "Talk is cheap. Show me the code." - Linus Torvalds

---

## 需求理解確認

**基於現有信息，我理解您的需求是：**

你要建立一個雪場資料庫，**目前只需要回答 3-5 個具體問題**：
1. 哪些雪場適合親子？
2. 推薦與某雪場類似的其他雪場
3. 快速看懂價位區間
4. 知道從主要城市出發的交通負擔
5. 哪些雪場適合教練帶初學者

**你不需要：**
- 一個萬用的、永遠不會改的雪場資料結構
- 為未來所有可能問題準備的複雜系統
- 過度設計的架構

**你需要的是：**
- 一個 v0 版本，能穩定回答這 5 個問題
- 清洗規則明確、可執行
- 有一點緩衝空間給未來擴展，但不要過度

**請確認我的理解是否準確？**

---

## Linus 式問題分解思考

### 第一層：數據結構分析
> "Bad programmers worry about the code. Good programmers worry about data structures."

**核心數據是什麼？**
- 雪場的基本屬性（名稱、地區、價位）
- 可比較的維度（親子友善度、初學者友善度、目標客群）
- 交通資訊（從主要城市的時間）

**數據流向哪裡？**
1. 原始資料（官網、人工整理）→ 清洗 → 結構化 JSON
2. 結構化 JSON → 查詢/篩選/推薦

**有沒有不必要的數據複製或轉換？**
- ⚠️ 當前設計：CSV → Pandas → Pydantic → SQLAlchemy → PostgreSQL → FastAPI
- 🤔 **這他媽太複雜了！** 你只有 5 個問題要回答，為什麼需要這麼多層？

**Linus 的建議：**
```
第一版只需要：
1. 一個 JSON 文件存資料（不要資料庫）
2. 一個 Python 腳本讀取並回答問題
3. 就這樣

等你真的有 200+ 個雪場、每秒 100+ 查詢時，再考慮 PostgreSQL。
現在用資料庫是在解決不存在的問題。
```

---

### 第二層：特殊情況識別
> "好代碼沒有特殊情況"

**當前設計中的 if/else 分支：**

```python
# 在 validator.py 中
if resort.family_friendly_score == 5 and not resort.kids_school:
    self.warnings.append("警告...")

if 'beginner' in resort.target_profile and resort.beginner_friendly_level < 3:
    self.warnings.append("警告...")
```

**Linus 的問題：**
- 這些驗證邏輯是真正的業務邏輯，還是糟糕設計的補丁？
- 如果你的數據結構設計得當，還需要這麼多驗證嗎？

**能否重新設計來消除這些分支？**

```python
# 與其驗證「親子友善度5分但沒兒童雪校」
# 不如直接根據設施計算親子友善度

def calculate_family_score(kids_area, kids_school, childcare):
    score = 1
    if kids_area: score += 1
    if kids_school: score += 1
    if childcare: score += 2  # 更重要
    return score

# 這樣就不需要驗證了，因為數據本身就是一致的
```

**Linus 的建議：**
- 消除驗證邏輯，讓數據結構本身保證一致性
- 評分應該是計算出來的，不是人工填的

---

### 第三層：複雜度審查
> "如果實現需要超過3層縮進，重新設計它"

**這個功能的本質是什麼？**
- 儲存雪場資料
- 根據條件篩選
- 計算相似度推薦

**當前方案用了多少概念？**
1. Pydantic Models
2. SQLAlchemy Models
3. Database Connection
4. FastAPI
5. Pandas DataFrames
6. scikit-learn
7. JSON Schema validation
8. Custom validators
9. Service layer
10. API layer

**能否減少到一半？再一半？**

**Linus 的 v0 方案（3個文件解決）：**

```
data/resorts.json          # 資料文件
scripts/query.py           # 查詢腳本
scripts/add_resort.py      # 新增雪場腳本
```

**為什麼不需要更多？**
- 沒有高並發查詢 → 不需要資料庫
- 沒有複雜業務邏輯 → 不需要 Service layer
- 沒有多人協作寫入 → 不需要 ORM
- 只有 5 個查詢問題 → 不需要 FastAPI

**什麼時候再擴展？**
- 當你有 >100 個雪場時，考慮加索引（可能還是 JSON + 緩存）
- 當你需要 Web UI 時，加 FastAPI
- 當你有寫入衝突時，加資料庫

---

### 第四層：破壞性分析
> "Never break userspace"

**當前階段沒有「用戶」，所以沒有破壞性問題**

但要考慮未來：
- 如果你現在用複雜的 schema，未來改動會很痛苦
- 如果你現在用簡單的 JSON，未來加欄位很容易

**Linus 的建議：**
- v0 用最簡單的結構
- 保持向後兼容就是「不要刪除欄位」
- 未來加欄位是安全的，改欄位是危險的

---

### 第五層：實用性驗證
> "Theory and practice sometimes clash. Theory loses. Every single time."

**這個問題在生產環境真實存在嗎？**
- ✅ 是的，你需要清洗雪場資料
- ✅ 是的，你需要回答那 5 個問題

**有多少用戶真正遇到這個問題？**
- 目前：只有你自己
- 未來可能有學員和教練

**解決方案的複雜度是否與問題的嚴重性匹配？**
- ❌ **不匹配！**
- 當前設計是為了處理「百萬級查詢、多人協作、複雜業務邏輯」
- 實際問題是「清洗 50 個雪場、回答 5 個問題」

---

## 決策輸出

### 【核心判斷】

❌ **當前 4 週計劃不值得做**

**原因：過度設計**
- 你在為不存在的高並發問題設計架構
- 你在為不存在的多人協作設計 ORM
- 你在為不存在的複雜業務邏輯設計 Service layer

✅ **值得做的是：極簡 v0 版本**

**原因：解決真實問題**
- 只用 3 個文件就能回答你的 5 個問題
- 可以在 1 天內完成，而不是 4 週
- 未來擴展時，數據遷移很容易

---

### 【關鍵洞察】

**1. 數據結構：**
```json
// resorts.json - 就這麼簡單
[
  {
    "id": "hakuba-happo",
    "name": "白馬八方尾根",
    "region": "nagano",
    "price": "premium",
    "family_score": 3,
    "beginner_score": 3,
    "travel": {
      "tokyo": 240
    },
    "tags": ["advanced", "backcountry"]
  }
]
```

**2. 複雜度：可以消除的複雜性**
- 刪除：SQLAlchemy, PostgreSQL, FastAPI, Pydantic
- 保留：JSON, Python 標準庫, 一個簡單的 cosine similarity 函數

**3. 風險點：過度設計導致開發週期長**
- 4 週後你可能還在調試 ORM，而不是在清洗資料
- 簡單方案 1 天完成，剩下 3 週 6 天清洗 100+ 個雪場

---

### 【Linus 式方案】

#### Phase 1：極簡 v0（1 天完成）

**三個文件解決所有問題：**

##### 1. `data/resorts.json`
```json
[
  {
    "id": "gala-yuzawa",
    "name": "GALA湯沢",
    "region": "niigata",
    "price": "mid",
    "family_score": 5,
    "beginner_score": 4,
    "travel": {"tokyo": 75},
    "tags": ["family", "beginner"]
  }
]
```

##### 2. `scripts/query.py`
```python
import json
from typing import List, Dict

def load_resorts() -> List[Dict]:
    with open('data/resorts.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Q1: 親子友善雪場
def find_family_friendly(min_score=4) -> List[Dict]:
    resorts = load_resorts()
    return [r for r in resorts if r['family_score'] >= min_score]

# Q2: 相似雪場（用最笨的方法）
def find_similar(resort_id: str, top_n=5) -> List[Dict]:
    resorts = load_resorts()
    target = next(r for r in resorts if r['id'] == resort_id)

    # 簡單的相似度：地區相同+1，價位相同+1，tags重疊+n
    def similarity(r):
        if r['id'] == resort_id:
            return -1
        score = 0
        if r['region'] == target['region']:
            score += 1
        if r['price'] == target['price']:
            score += 1
        score += len(set(r['tags']) & set(target['tags']))
        return score

    return sorted(resorts, key=similarity, reverse=True)[:top_n]

# Q3: 價位篩選
def filter_by_price(level: str) -> List[Dict]:
    resorts = load_resorts()
    return [r for r in resorts if r['price'] == level]

# Q4: 交通時間
def filter_by_travel_time(city: str, max_minutes: int) -> List[Dict]:
    resorts = load_resorts()
    return [r for r in resorts
            if city in r['travel'] and r['travel'][city] <= max_minutes]

# Q5: 初學者友善
def find_beginner_friendly(min_score=4) -> List[Dict]:
    resorts = load_resorts()
    return [r for r in resorts if r['beginner_score'] >= min_score]

if __name__ == "__main__":
    # 測試
    print("親子友善雪場：", find_family_friendly())
    print("類似白馬八方：", find_similar('hakuba-happo'))
```

##### 3. `scripts/add_resort.py`
```python
import json

def add_resort():
    """手動新增雪場的互動式腳本"""
    resort = {
        "id": input("ID (例: hakuba-happo): "),
        "name": input("名稱: "),
        "region": input("地區 (hokkaido/nagano/niigata...): "),
        "price": input("價位 (budget/mid/premium): "),
        "family_score": int(input("親子友善度 (1-5): ")),
        "beginner_score": int(input("初學者友善度 (1-5): ")),
        "travel": {},
        "tags": []
    }

    # 交通時間
    while True:
        city = input("城市名稱（輸入空白結束）: ")
        if not city:
            break
        minutes = int(input(f"從{city}的時間（分鐘）: "))
        resort["travel"][city] = minutes

    # Tags
    tags_input = input("標籤（用逗號分隔，例: family,beginner）: ")
    resort["tags"] = [t.strip() for t in tags_input.split(",") if t.strip()]

    # 讀取現有資料
    try:
        with open('data/resorts.json', 'r', encoding='utf-8') as f:
            resorts = json.load(f)
    except FileNotFoundError:
        resorts = []

    # 新增並儲存
    resorts.append(resort)
    with open('data/resorts.json', 'w', encoding='utf-8') as f:
        json.dump(resorts, f, ensure_ascii=False, indent=2)

    print(f"✅ 已新增雪場：{resort['name']}")

if __name__ == "__main__":
    add_resort()
```

---

#### 為什麼這個方案更好？

**1. 數據結構第一**
- JSON 就是最好的數據結構，人類可讀，機器可解析
- 不需要 ORM 的間接層

**2. 消除特殊情況**
- 沒有驗證邏輯，因為數據本身就簡單
- 評分就是數字，篩選就是比較，沒有特殊情況

**3. 複雜度控制**
- 每個函數 <10 行
- 沒有縮進 >2 層
- 一眼看懂在做什麼

**4. 向後兼容**
- JSON 格式加欄位很容易
- 舊代碼繼續工作

**5. 實用性**
- 1 天完成，立即可用
- 清洗 100 個雪場只需要改 JSON
- 需要 API 時再加 FastAPI（10 行代碼）

---

## 什麼時候升級？

### 觸發條件 → 對應方案

| 觸發條件 | 當前是否滿足 | 對應升級方案 |
|---------|------------|------------|
| 雪場數量 >100 | ❌ 目前 0 個 | 加 SQLite（不是 PostgreSQL） |
| 查詢 QPS >10 | ❌ 只有你一個用戶 | 加內存緩存 |
| 需要 Web UI | ❌ 只需要查詢腳本 | 加 FastAPI（20 行代碼） |
| 多人同時編輯 | ❌ 只有你在清洗 | 加版本控制 + git |
| 複雜推薦邏輯 | ❌ 簡單相似度足夠 | 再考慮 scikit-learn |

**目前一個都不滿足，所以不需要升級。**

---

## 審查清單

### ✅ 數據結構第一
- [x] 數據結構簡潔明瞭（純 JSON）
- [x] 沒有不必要的間接層（無 ORM）
- [x] 數據所有權清晰（一個文件）

### ✅ 消除特殊情況
- [x] 只有業務邏輯的 if（篩選條件）
- [x] 沒有邊界情況特殊處理
- [x] 評分是數字，標籤是數組，簡單明瞭

### ✅ 複雜度控制
- [x] 函數 <20 行
- [x] 縮進 ≤2 層
- [x] 一眼能看懂

### ✅ 向後兼容
- [x] JSON 格式易於擴展
- [x] 加欄位不會破壞舊代碼

### ✅ 實用性
- [x] 解決真實問題（5 個查詢）
- [x] 複雜度匹配（3 個文件 vs 4 週開發）
- [x] 沒有過度設計

---

## 最終建議

### 🔴 不要做的事
1. **不要建資料庫**（現在不需要）
2. **不要用 ORM**（過度抽象）
3. **不要寫 FastAPI**（沒有 Web 需求）
4. **不要用 Pydantic**（JSON schema 就夠了）
5. **不要花 4 週**（1 天就能完成）

### 🟢 應該做的事
1. **建立 `data/resorts.json`**（5 分鐘）
2. **寫 `scripts/query.py`**（30 分鐘）
3. **寫 `scripts/add_resort.py`**（30 分鐘）
4. **測試查詢是否正確**（10 分鐘）
5. **開始清洗雪場資料**（剩下的時間）

### 📅 時間分配
- Day 1：建立極簡 v0（1 小時）
- Week 1-4：清洗 50-100 個雪場資料
- 當真正需要時再升級架構

---

## "Talk is cheap. Show me the code."

下一步：
1. 建立 `data/resorts.json` 和兩個腳本
2. 手動清洗 3-5 個雪場作為範例
3. 測試所有 5 個查詢是否正確運作
4. 開始批量清洗

**需要我實現這個極簡版本嗎？**

---

**版本**: v0.1 (Linus-approved)
**更新日期**: 2025-11-18
**核心原則**: "Simplicity is prerequisite for reliability." - Edsger W. Dijkstra (Linus 也會同意的)
