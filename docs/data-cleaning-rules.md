# 雪場資料清洗規則 v0

## 一、核心問題清單（3-6個月內一定會用到）

### Q1：學員如何挑出「親子友善」的雪場？
- **使用場景**：家長帶小孩找適合的雪場
- **需要資訊**：兒童設施、親子友善度、適合年齡層

### Q2：在某個雪場頁面，推薦3-5個「類似的」雪場
- **使用場景**：學員看完一個雪場，系統推薦類似選項
- **需要資訊**：地區、價位、難度、特色相似度

### Q3：學員可以快速看懂雪場的大致價位區間
- **使用場景**：篩選預算內的雪場
- **需要資訊**：價位等級（低/中/高）

### Q4：知道從主要城市出發的交通負擔
- **使用場景**：評估交通便利性
- **需要資訊**：距離、交通時間、主要出發城市

### Q5：哪些雪場適合帶初學者上課（教練端需求）
- **使用場景**：教練選擇教學地點
- **需要資訊**：初學者坡道比例、教學友善度

---

## 二、欄位分級架構

### 🔴 必備欄位（Tier 1）- 現在一定會用
**為 Q1-Q5 而生，每個雪場必須有值**

| 欄位名稱 | 類型 | 說明 | 支援問題 |
|---------|------|------|---------|
| `resort_id` | string | 唯一識別碼 | 全部 |
| `name_jp` | string | 日文名稱 | 全部 |
| `name_en` | string | 英文名稱（選填） | 全部 |
| `region` | enum | 地區（北海道/長野/新潟等） | Q2, Q4 |
| `prefecture` | string | 都道府縣 | Q2, Q4 |
| `price_level` | enum | 價位等級（budget/mid/premium） | Q2, Q3 |
| `family_friendly_score` | int | 親子友善度 (1-5) | Q1, Q2 |
| `beginner_friendly_level` | int | 初學者友善度 (1-5) | Q2, Q5 |
| `travel_time_from_city` | object | 從主要城市的交通時間 | Q4 |
| `target_profile` | array | 目標客群標籤 | Q1, Q2 |

### 🟡 建議欄位（Tier 2）- 高機率未來會用
**不影響 v0 核心問題，但長期有價值**

| 欄位名稱 | 類型 | 說明 | 預期用途 |
|---------|------|------|---------|
| `kids_school` | boolean | 是否有兒童雪校 | 親子功能擴充 |
| `facility_tags` | array | 設施標籤（溫泉/outlet/室內遊戲區） | 篩選條件擴充 |
| `coach_available` | boolean | 是否可安排教練 | 教練媒合功能 |
| `slope_count` | object | 坡道數量（初/中/高級） | 難度分析 |
| `lift_count` | int | 纜車數量 | 規模評估 |
| `accommodation_nearby` | boolean | 附近是否有住宿 | 旅遊規劃 |

### ⚪ 未來欄位（Tier 3）- 暫不入 schema
**先記在 tags 或 notes，等確定要用再正式化**

- IG打卡友善度
- 夜滑氛圍
- 公司旅遊適配度
- 雪質類型（粉雪/壓雪）
- 滑雪場氛圍（熱鬧/安靜）

---

## 三、清洗優先級

### Phase 1：建立骨架（Week 1）
1. 建立雪場清單（resort_id, name_jp, region, prefecture）
2. 確保每個雪場都有唯一 ID
3. 建立基礎地區分類

### Phase 2：填入核心欄位（Week 2-3）
**按照重要性順序填值：**

1. **價位等級** (`price_level`)
   - 來源：官網票價、住宿價格帶
   - 分類標準：
     - budget: 纜車一日券 < ¥4,000
     - mid: ¥4,000 - ¥6,000
     - premium: > ¥6,000

2. **交通時間** (`travel_time_from_city`)
   - 格式：
     ```json
     {
       "tokyo": {"minutes": 180, "method": "新幹線+巴士"},
       "nagano": {"minutes": 60, "method": "巴士"}
     }
     ```
   - 來源：官網、Google Maps

3. **親子友善度** (`family_friendly_score`)
   - 評分標準：
     - 5分：有兒童樂園+雪校+托兒服務
     - 4分：有兒童專區+雪校
     - 3分：有兒童專區
     - 2分：允許兒童但無特別設施
     - 1分：主要為進階滑雪者設計

4. **初學者友善度** (`beginner_friendly_level`)
   - 評分標準：
     - 5分：>50% 初級坡道 + 專業教學
     - 4分：40-50% 初級坡道
     - 3分：30-40% 初級坡道
     - 2分：<30% 初級坡道
     - 1分：主要為進階者

5. **目標客群** (`target_profile`)
   - 可複選：`["family", "beginner", "advanced", "backcountry", "park"]`
   - 依據設施和坡道配置判斷

### Phase 3：補充建議欄位（Week 4）
**有餘力再填，不強制完成**

- `kids_school`
- `facility_tags`
- `coach_available`

---

## 四、資料品質標準

### 必備欄位完整度要求
- **100% 必須有值**：resort_id, name_jp, region, prefecture
- **90% 以上有值**：price_level, family_friendly_score, beginner_friendly_level
- **80% 以上有值**：travel_time_from_city（至少一個主要城市）

### 建議欄位完整度要求
- **60% 以上有值**即可
- 如果查不到，可以留空或標記 `null`

### 品質檢查點
1. **一致性**：同一個評分標準在所有雪場都用同樣邏輯
2. **可驗證**：每個數值都有來源備註
3. **合理性**：price_level 和實際價格相符

---

## 五、緩衝區設計（tags & notes）

### 在 schema 中加入兩個彈性欄位：

```json
{
  "tags": ["IG打卡", "夜滑", "粉雪天堂"],
  "notes_for_future": "這個雪場很適合公司旅遊，附近有大型度假村和溫泉街"
}
```

**使用規則：**
- `tags`：自由關鍵字，未來可能升級成正式欄位
- `notes_for_future`：任何想記錄但還沒正式化的資訊

---

## 六、什麼時候該「升級欄位」？

### 三個判斷提示：

1. **這個欄位描述的是雪場固有屬性嗎？**
   - 如果是 → 可以考慮正式化
   - 如果是情境性的（如「IG打卡」）→ 先放 tags

2. **在 1 年 roadmap 裡，這個欄位會出現在哪個功能上？**
   - 如果沒有明確功能 → 不要加
   - 如果已經在規劃中 → 可以加到建議欄位

3. **如果現在不加，未來補回來會不會很痛苦？**
   - 如果要重新查 200 個雪場官網 → 現在就加
   - 如果可以快速補回 → 晚點再說

---

## 七、清洗作業 SOP

### 每個雪場的清洗流程：

1. **建立基礎資料**（5分鐘）
   - 從官網抓：名稱、地區、聯絡方式

2. **填必備欄位**（15分鐘）
   - 查價格 → price_level
   - 看坡道圖 → beginner_friendly_level
   - 看設施 → family_friendly_score
   - 查交通 → travel_time_from_city

3. **標記 tags**（3分鐘）
   - 看到任何特色就先記在 tags
   - 例如：粉雪、夜滑、溫泉、outlet

4. **品質檢查**（2分鐘）
   - 必備欄位都有值？
   - 評分邏輯一致？

**單一雪場預計時間：~25分鐘**

---

## 八、範例：清洗一個雪場

### 範例：白馬八方尾根

```json
{
  "resort_id": "hakuba-happo",
  "name_jp": "白馬八方尾根スキー場",
  "name_en": "Hakuba Happo-one",
  "region": "nagano",
  "prefecture": "長野県",

  // 必備欄位
  "price_level": "premium",
  "family_friendly_score": 3,
  "beginner_friendly_level": 3,
  "travel_time_from_city": {
    "tokyo": {"minutes": 240, "method": "新幹線+巴士"},
    "nagano": {"minutes": 90, "method": "巴士"}
  },
  "target_profile": ["advanced", "backcountry"],

  // 建議欄位
  "kids_school": true,
  "facility_tags": ["溫泉", "國際級"],
  "coach_available": true,
  "slope_count": {"beginner": 5, "intermediate": 8, "advanced": 9},

  // 緩衝區
  "tags": ["粉雪", "1998冬奧", "國際村"],
  "notes_for_future": "國際滑雪者多，英文友善，適合進階玩家"
}
```

---

## 九、常見問題 FAQ

### Q：如果某個雪場查不到價格怎麼辦？
A：標記為 `null`，並在 notes 註明「官網未公開價格」，後續統一處理

### Q：親子友善度很主觀，怎麼評？
A：用固定標準（見 Phase 2），並保持一致性。可以 2-3 個人交叉檢查。

### Q：發現新的重要欄位怎麼辦？
A：先記在 tags，累積 10+ 個雪場都有同樣需求時，再提升為正式欄位

### Q：資料來源不一致怎麼辦？
A：優先順序：官網 > Google Maps > 部落格/評論

---

**版本**：v0.1
**更新日期**：2025-11-18
**下次檢討**：完成 30 個雪場清洗後
