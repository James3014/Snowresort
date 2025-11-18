# 雪場資料管理系統 v0.1 (極簡版)

> "Talk is cheap. Show me the code." - Linus Torvalds

## 專案簡介

這是一個極簡的雪場資料管理與查詢系統，用於儲存、管理和查詢日本滑雪場資訊。

**設計理念：**
- 只用 3 個核心文件解決問題
- 純 JSON 儲存，無需資料庫
- 簡單的 Python 腳本，無複雜依賴
- 專注於回答 5 個核心問題

## 專案結構

```
Snowresort/
├── data/
│   └── resorts.json          # 雪場資料（JSON 格式）
├── scripts/
│   ├── query.py              # 查詢腳本
│   └── add_resort.py         # 新增雪場腳本
├── docs/                     # 文檔（設計規則、Schema 等）
├── Claude.md                 # Linus 式代碼審查與設計決策
└── README.md                 # 本文件
```

## 5 個核心問題

系統專注於回答以下問題：

1. **Q1：哪些雪場適合親子？**
2. **Q2：推薦與某雪場類似的其他雪場**
3. **Q3：快速看懂價位區間**
4. **Q4：從主要城市出發的交通負擔**
5. **Q5：哪些雪場適合教練帶初學者**

## 快速開始

### 安裝

無需安裝任何套件，只需要 Python 3.6+：

```bash
# 檢查 Python 版本
python3 --version
```

### 基本使用

#### 1. 列出所有雪場

```bash
python3 scripts/query.py list
```

#### 2. 查看雪場詳細資訊

```bash
python3 scripts/query.py detail kamui-ski-links
```

#### 3. 找親子友善雪場（Q1）

```bash
# 找親子友善度 >= 4 的雪場
python3 scripts/query.py family 4

# 找親子友善度 >= 3 的雪場
python3 scripts/query.py family 3
```

#### 4. 找初學者友善雪場（Q5）

```bash
# 找初學者友善度 >= 4 的雪場
python3 scripts/query.py beginner 4
```

#### 5. 依價位篩選（Q3）

```bash
# 找中價位雪場
python3 scripts/query.py price mid

# 找經濟型雪場
python3 scripts/query.py price budget

# 找高價位雪場
python3 scripts/query.py price premium
```

#### 6. 依交通時間篩選（Q4）

```bash
# 找從旭川市區 60 分鐘內可達的雪場
python3 scripts/query.py travel asahikawa_city 60

# 找從札幌 3 小時內可達的雪場
python3 scripts/query.py travel sapporo 180
```

#### 7. 找相似雪場（Q2）

```bash
# 找與神居最相似的 5 個雪場
python3 scripts/query.py similar kamui-ski-links 5

# 找與神居最相似的 3 個雪場
python3 scripts/query.py similar kamui-ski-links 3
```

### 新增雪場

#### 互動式新增（推薦）

```bash
python3 scripts/add_resort.py
```

系統會逐步引導你輸入所有必要資訊。

#### 快速新增（簡化版）

```bash
python3 scripts/add_resort.py quick <id> <名稱> <地區> <價位> <親子分數> <初學分數>
```

範例：
```bash
python3 scripts/add_resort.py quick niseko-village 'ニセコビレッジ' hokkaido premium 4 3
```

**注意：** 快速新增後，資料會標記為 `needs_review`，建議再用互動模式補充完整資訊。

## 資料格式說明

### 必填欄位

```json
{
  "id": "kamui-ski-links",           // 唯一識別碼（kebab-case）
  "name": "神居スキーリンクス",       // 日文名稱
  "region": "hokkaido",              // 地區
  "prefecture": "北海道",            // 都道府縣
  "price": "mid",                    // 價位 (budget/mid/premium)
  "family_score": 4,                 // 親子友善度 (1-5)
  "beginner_score": 4,               // 初學者友善度 (1-5)
  "travel": {},                      // 交通時間（分鐘）
  "tags": [],                        // 標籤
  "facilities": {}                   // 設施
}
```

### 建議欄位

```json
{
  "name_en": "Kamui Ski Links",      // 英文名稱
  "city": "旭川市",                  // 城市
  "stats": {                         // 雪場統計
    "trails": 25,
    "beginner_trails": 9,
    "beginner_percentage": 32,
    "vertical_drop": 601,
    "longest_run": 4000
  },
  "highlights": [],                  // 特色亮點
  "notes": "..."                     // 備註說明
}
```

完整 Schema 請參考 `docs/schema-design.md`。

## 目前資料

- ✅ **神居滑雪場 (Kamui Ski Links)** - 已完整整理自詳細報告

## 設計決策

### 為什麼用 JSON 而不是資料庫？

1. **當前規模不需要資料庫**
   - 現在只有 1 個雪場
   - 即使 100 個雪場，JSON 也足夠快

2. **JSON 的優勢**
   - 人類可讀，方便檢查和編輯
   - 無需配置資料庫連線
   - 可直接用 git 追蹤變更
   - 部署零成本

3. **何時升級？**
   - 當雪場數量 > 100 個
   - 當查詢 QPS > 10
   - 當需要多人同時編輯

### 為什麼沒有 FastAPI？

當前只需要命令列查詢，沒有 Web UI 需求。

**何時加入？**
- 當需要提供 Web 介面給使用者時
- 只需要 20 行代碼就能加入 FastAPI

### 相似度計算為什麼這麼簡單？

使用簡單的加權計分法：
- 地區相同 +1
- 價位相同 +1
- 每個重疊標籤 +1

**優點：**
- 邏輯清晰，易於理解
- 執行速度快
- 對於小資料集足夠準確

**何時升級？**
- 當需要更精準的推薦時
- 再考慮加入 scikit-learn 的 cosine similarity

完整設計理念請參考 `Claude.md`。

## 未來擴展

### 短期（當資料量增加）

1. **資料驗證**
   ```bash
   python3 scripts/validate.py
   ```

2. **資料匯出**
   ```bash
   python3 scripts/export.py --format csv
   ```

3. **批次匯入**
   ```bash
   python3 scripts/import.py data/batch_resorts.csv
   ```

### 中期（當需要 Web 介面）

1. **FastAPI 後端**（~20 行代碼）
2. **簡單的 HTML 前端**

### 長期（當真的需要時）

1. **SQLite 資料庫**（不是 PostgreSQL）
2. **快取機制**
3. **更精準的推薦演算法**

## 貢獻指南

### 新增雪場資料

1. 使用互動式腳本新增：
   ```bash
   python3 scripts/add_resort.py
   ```

2. 確保資料品質：
   - 必填欄位都有值
   - 評分（1-5）合理
   - 交通時間準確

3. Commit 訊息格式：
   ```
   Add: 新增XXX雪場資料
   Update: 更新XXX雪場價格資訊
   Fix: 修正XXX雪場交通時間
   ```

### 改進查詢功能

歡迎提交 PR 改進現有查詢邏輯或新增實用功能。

## 開發歷程

- **2025-11-18**: v0.1 發布
  - 極簡 3 文件架構
  - 5 個核心查詢功能
  - 神居滑雪場完整資料

## 授權

MIT License

## 參考資料

- [清洗規則文檔](docs/data-cleaning-rules.md)
- [Schema 設計](docs/schema-design.md)
- [實現計劃（參考用）](docs/implementation-plan.md)
- [Linus 式代碼審查](Claude.md)

---

**哲學：**
> 從最簡單能用的版本開始，只在真正需要時才增加複雜度。
