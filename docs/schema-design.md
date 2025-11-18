# 雪場資料 Schema 設計 v0

## Schema 結構

### 完整 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["resort_id", "name_jp", "region", "prefecture", "price_level"],
  "properties": {

    // ===== 基礎識別資訊 =====
    "resort_id": {
      "type": "string",
      "description": "唯一識別碼，使用 kebab-case",
      "pattern": "^[a-z0-9-]+$",
      "example": "hakuba-happo"
    },
    "name_jp": {
      "type": "string",
      "description": "日文正式名稱",
      "example": "白馬八方尾根スキー場"
    },
    "name_en": {
      "type": "string",
      "description": "英文名稱（選填）",
      "example": "Hakuba Happo-one"
    },
    "website": {
      "type": "string",
      "format": "uri",
      "description": "官方網站"
    },

    // ===== Tier 1: 必備欄位 =====
    "region": {
      "type": "string",
      "enum": [
        "hokkaido",
        "tohoku",
        "niigata",
        "nagano",
        "gunma",
        "other-kanto",
        "chubu",
        "kansai",
        "other"
      ],
      "description": "主要地區分類"
    },
    "prefecture": {
      "type": "string",
      "description": "都道府縣",
      "example": "長野県"
    },
    "price_level": {
      "type": "string",
      "enum": ["budget", "mid", "premium"],
      "description": "價位等級：budget(<¥4k), mid(¥4-6k), premium(>¥6k)"
    },
    "family_friendly_score": {
      "type": "integer",
      "minimum": 1,
      "maximum": 5,
      "description": "親子友善度 1-5，5最友善"
    },
    "beginner_friendly_level": {
      "type": "integer",
      "minimum": 1,
      "maximum": 5,
      "description": "初學者友善度 1-5，5最友善"
    },
    "travel_time_from_city": {
      "type": "object",
      "description": "從主要城市的交通時間",
      "properties": {
        "tokyo": {
          "$ref": "#/definitions/travelInfo"
        },
        "osaka": {
          "$ref": "#/definitions/travelInfo"
        },
        "nagoya": {
          "$ref": "#/definitions/travelInfo"
        },
        "sapporo": {
          "$ref": "#/definitions/travelInfo"
        },
        "nagano": {
          "$ref": "#/definitions/travelInfo"
        },
        "niigata": {
          "$ref": "#/definitions/travelInfo"
        }
      },
      "additionalProperties": false
    },
    "target_profile": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["family", "beginner", "intermediate", "advanced", "backcountry", "park", "freestyle"]
      },
      "description": "目標客群標籤，可複選"
    },

    // ===== Tier 2: 建議欄位 =====
    "kids_school": {
      "type": "boolean",
      "description": "是否有兒童雪校"
    },
    "facility_tags": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "溫泉", "outlet", "室內遊戲區", "托兒服務",
          "夜滑", "纜車餐廳", "租借設備",
          "國際級", "奧運場地", "樹林滑雪"
        ]
      },
      "description": "設施特色標籤"
    },
    "coach_available": {
      "type": "boolean",
      "description": "是否可安排教練課程"
    },
    "slope_count": {
      "type": "object",
      "properties": {
        "beginner": {"type": "integer", "minimum": 0},
        "intermediate": {"type": "integer", "minimum": 0},
        "advanced": {"type": "integer", "minimum": 0}
      },
      "description": "各難度坡道數量"
    },
    "lift_count": {
      "type": "integer",
      "minimum": 0,
      "description": "纜車總數"
    },
    "accommodation_nearby": {
      "type": "boolean",
      "description": "附近是否有住宿設施"
    },

    // ===== Tier 3: 緩衝區 =====
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "自由標籤，未來可能升級成正式欄位",
      "example": ["IG打卡", "粉雪", "夜滑浪漫"]
    },
    "notes_for_future": {
      "type": "string",
      "description": "未來功能的備註資訊"
    },

    // ===== Meta 資訊 =====
    "data_source": {
      "type": "object",
      "properties": {
        "official_website": {"type": "boolean"},
        "third_party_review": {"type": "boolean"},
        "google_maps": {"type": "boolean"},
        "manual_inspection": {"type": "boolean"}
      },
      "description": "資料來源標記"
    },
    "last_updated": {
      "type": "string",
      "format": "date",
      "description": "最後更新日期 (YYYY-MM-DD)"
    },
    "data_quality": {
      "type": "string",
      "enum": ["complete", "partial", "needs_review"],
      "description": "資料完整度狀態"
    }
  },

  // ===== 定義重用結構 =====
  "definitions": {
    "travelInfo": {
      "type": "object",
      "required": ["minutes"],
      "properties": {
        "minutes": {
          "type": "integer",
          "minimum": 0,
          "description": "交通時間（分鐘）"
        },
        "method": {
          "type": "string",
          "description": "交通方式",
          "example": "新幹線+巴士"
        },
        "cost_estimate": {
          "type": "integer",
          "description": "大約交通費用（日圓）"
        }
      }
    }
  }
}
```

---

## 資料範例

### 範例 1：親子友善的中價位雪場

```json
{
  "resort_id": "gala-yuzawa",
  "name_jp": "GALA湯沢スキー場",
  "name_en": "GALA Yuzawa",
  "website": "https://gala.co.jp/",

  "region": "niigata",
  "prefecture": "新潟県",
  "price_level": "mid",

  "family_friendly_score": 5,
  "beginner_friendly_level": 4,
  "travel_time_from_city": {
    "tokyo": {
      "minutes": 75,
      "method": "新幹線直達",
      "cost_estimate": 6000
    }
  },
  "target_profile": ["family", "beginner", "intermediate"],

  "kids_school": true,
  "facility_tags": ["新幹線直達", "室內遊戲區", "租借設備"],
  "coach_available": true,
  "slope_count": {
    "beginner": 6,
    "intermediate": 10,
    "advanced": 1
  },
  "lift_count": 12,
  "accommodation_nearby": true,

  "tags": ["交通最方便", "東京當日來回"],
  "notes_for_future": "新幹線站內就是雪場，最適合不想舟車勞頓的家庭",

  "data_source": {
    "official_website": true,
    "google_maps": true,
    "manual_inspection": true
  },
  "last_updated": "2025-11-18",
  "data_quality": "complete"
}
```

### 範例 2：進階玩家的高價位雪場

```json
{
  "resort_id": "niseko-grand-hirafu",
  "name_jp": "ニセコグラン・ヒラフ",
  "name_en": "Niseko Grand Hirafu",
  "website": "https://www.grand-hirafu.jp/",

  "region": "hokkaido",
  "prefecture": "北海道",
  "price_level": "premium",

  "family_friendly_score": 3,
  "beginner_friendly_level": 2,
  "travel_time_from_city": {
    "sapporo": {
      "minutes": 150,
      "method": "巴士",
      "cost_estimate": 3000
    },
    "tokyo": {
      "minutes": 240,
      "method": "飛機+巴士"
    }
  },
  "target_profile": ["advanced", "backcountry", "intermediate"],

  "kids_school": true,
  "facility_tags": ["粉雪", "國際級", "溫泉", "夜滑"],
  "coach_available": true,
  "slope_count": {
    "beginner": 8,
    "intermediate": 15,
    "advanced": 12
  },
  "lift_count": 13,
  "accommodation_nearby": true,

  "tags": ["世界級粉雪", "國際村", "英文友善", "高級度假村"],
  "notes_for_future": "國際滑雪者比例高，住宿選擇多元，夜生活豐富",

  "data_source": {
    "official_website": true,
    "third_party_review": true,
    "manual_inspection": true
  },
  "last_updated": "2025-11-18",
  "data_quality": "complete"
}
```

### 範例 3：資料不完整的雪場（標記需要補充）

```json
{
  "resort_id": "myoko-akakura",
  "name_jp": "妙高赤倉温泉スキー場",
  "name_en": "Myoko Akakura Onsen",

  "region": "niigata",
  "prefecture": "新潟県",
  "price_level": "mid",

  "family_friendly_score": 3,
  "beginner_friendly_level": 3,
  "travel_time_from_city": {
    "tokyo": {
      "minutes": 180,
      "method": "新幹線+巴士"
    }
  },
  "target_profile": ["intermediate", "advanced"],

  "facility_tags": ["溫泉"],
  "tags": ["粉雪", "溫泉街"],
  "notes_for_future": "待補充：兒童設施資訊、教練可用性",

  "data_source": {
    "official_website": true
  },
  "last_updated": "2025-11-18",
  "data_quality": "needs_review"
}
```

---

## 欄位填值指南

### region 分類對照表

| region 值 | 包含都道府縣 | 特色 |
|-----------|------------|------|
| hokkaido | 北海道 | 粉雪、國際級 |
| tohoku | 青森、岩手、宮城、秋田、山形、福島 | 樹冰、溫泉 |
| niigata | 新潟 | 雪量大、交通便利 |
| nagano | 長野 | 奧運場地、多樣性 |
| gunma | 群馬 | 東京近郊 |
| other-kanto | 栃木、茨城、埼玉等 | 當日來回 |
| chubu | 富山、石川、福井、山梨、岐阜等 | 立山黑部 |
| kansai | 滋賀、京都、兵庫等 | 關西近郊 |
| other | 其他地區 | 特殊案例 |

### price_level 判定標準

| 等級 | 纜車一日券價格 | 典型住宿價格 |
|------|--------------|------------|
| budget | < ¥4,000 | < ¥8,000/晚 |
| mid | ¥4,000 - ¥6,000 | ¥8,000 - ¥15,000/晚 |
| premium | > ¥6,000 | > ¥15,000/晚 |

### target_profile 判定邏輯

```
family: 有兒童設施、兒童雪校、或 family_friendly_score >= 4
beginner: beginner_friendly_level >= 4
intermediate: 有中級坡道 >= 40%
advanced: 有高級坡道 >= 30%
backcountry: 有界外滑雪區域
park: 有地形公園、跳台
freestyle: 有half-pipe或專業公園
```

---

## 資料驗證規則

### 自動檢查項目

```javascript
// 必備欄位檢查
const requiredFields = [
  'resort_id',
  'name_jp',
  'region',
  'prefecture',
  'price_level'
];

// 評分合理性檢查
if (family_friendly_score === 5 && !kids_school) {
  warn("親子友善度5分但沒有兒童雪校，請確認");
}

// 一致性檢查
if (target_profile.includes('beginner') && beginner_friendly_level < 3) {
  warn("目標客群包含初學者但友善度<3，請確認");
}

// 交通時間合理性
if (travel_time_from_city.tokyo?.minutes < 60 && region !== 'gunma') {
  warn("非群馬地區但東京交通時間<60分鐘，請確認");
}
```

---

## 版本管理

- **Current Version**: v0.1
- **Last Updated**: 2025-11-18
- **Breaking Changes**: 無（初始版本）
- **Deprecation**: 無

### 升級規則

當 tags 中某個關鍵字出現在 **10+ 個雪場**，且有明確功能需求時，考慮升級為正式欄位。

**升級流程：**
1. 在團隊會議中討論必要性
2. 定義新欄位的 schema 和驗證規則
3. 更新文檔版本號
4. 批次清洗現有資料
