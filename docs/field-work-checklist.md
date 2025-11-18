# 雪場資料填寫操作指南
> 給實際填資料的人用的超簡短版 checklist

**預計時間：每個雪場約 25 分鐘**

---

## 🔹 基本識別（先建骨架）

| 欄位 | 去哪找 | 怎麼填 | 注意 |
|------|--------|--------|------|
| `id` | 自訂 | 英文 kebab-case，例如 `kamui-ski-links` | 全站唯一，不要含空格／大寫 |
| `name` | 官網 | 日文正式名稱 | 直接複製，不要用簡稱 |
| `name_en` | 官網 / Google Maps | 英文名稱 | 沒有就留空 |
| `region` | 自己定義表 | 從表中選一個：`hokkaido` / `nagano` / `niigata` / ... | 只能選表內值 |
| `prefecture` | 官網 / Google Maps | 日本的都道府縣名（例：`北海道`、`長野県`） | 用日文官方寫法 |

---

## 🔹 Tier 1 必備欄位（一定要填）

| 欄位 | 去哪找 | 怎麼填 | 注意 |
|------|--------|--------|------|
| `price` | 官網票價 | 依成人一日券價格：<4000 → `budget`；4000–6000 → `mid`；>6000 → `premium` | 看最近一季票價 |
| `travel` | 官網交通頁 / Google Maps | 用標準 key + 分鐘數，例如：`{"tokyo": 180, "sapporo": 120}` | key 必須是：`tokyo`/`osaka`/`nagoya`/`sapporo`/`asahikawa_city`/`asahikawa_airport`/`nagano` 之一 |
| `family_score` | 官網設施介紹 + 自己判斷 | 按規則：5=兒童專區+雪校+托兒；4=兒童專區+雪校；3=兒童專區；2=可帶小孩但沒特別設施；1=不適合兒童；不確定→`null` | 必須是 1–5 或 `null` |
| `kids_area` | 官網設施頁、照片 | 有明講「兒童滑雪區、雪盆區、玩雪區」→ `true`；否則 `false` |  |
| `beginner_score` | 坡道圖（trail map） | 以初級坡比例估：>50%→5；40–50%→4；30–40%→3；<30%→2；幾乎沒初級→1；不確定→`null` | 無法估就用 `null`，不要亂猜 |
| `coach_available` | 官網規則、合作雪校、不確定可問教練 | 明確允許外部教練／有合作教練平台→`true`；明寫不允許或只限自家教練→`false`；不清楚→`false` 並在 `notes` 註明 | 這跟你平台實務很相關，寧可保守 |
| `audience_tags` | 綜合上述判斷 | 從固定清單中選：`family` / `beginner` / `intermediate` / `advanced` / `backcountry` / `park` / `powder` | 例：親子＋粉雪場→ `["family","intermediate","powder"]` |

---

## 🔹 Tier 2 建議欄位（有力就填）

| 欄位 | 去哪找 | 怎麼填 | 用途 |
|------|--------|--------|------|
| `kids_school` | 官網、雪校網站 | 有兒童雪校就 `true`，否則 `false` | 親子細分（有課 vs 只有玩） |
| `facility_tags` | 官網 / 旅遊介紹 | 自由填：`["onsen","outlet","indoor_playground"]` | 未來做進階篩選 |
| `slope_count` | 坡道圖 | 數初、中、高級道數量：`{"beginner":x,"intermediate":y,"advanced":z}` | 之後做難度分析用 |
| `lift_count` | 坡道圖 / 官網 | 填纜車總數（含 gondola + chair） | 大小規模感 |
| `accommodation_nearby` | Google Maps / 旅遊網站 | 雪場步行／接駁可到的住宿很多→`true`，否則 `false` | 之後做「住場邊」推薦 |

---

## 🔹 緩衝區（不用想太多，想到就寫）

| 欄位 | 用法 |
|------|------|
| `extra_tags` | 看到任何特別特徵就加，例如：`["IG打卡","夜滑","粉雪天堂","公司旅遊熱門"]` |
| `notes` | 任何解釋／例外：為什麼 `beginner_score` 給 4？教練可用性是怎麼判斷的？價格不確定怎麼處理？ |

---

## 🔹 每一筆的實際操作順序（給填表的人）

1. **先填基本識別**：`id` / `name` / `name_en` / `region` / `prefecture`
2. **查價格** → 填 `price`
3. **看交通資訊** → 填 `travel`（至少 1 個城市）
4. **看設施** → 填 `family_score` + `kids_area` + `kids_school`（若有）
5. **看坡道圖** → 填 `beginner_score` + `slope_count`（若有力）
6. **確認教練狀況** → 填 `coach_available`
7. **依整體印象** → 填 `audience_tags`
8. **最後補** `extra_tags` + `notes` 有想到什麼就寫

---

## ✅ 資料品質檢查點

完成後請自己檢查：
- [ ] 必填欄位都有值（基本識別 + Tier 1）
- [ ] `price` 和實際票價相符
- [ ] `travel` 至少有 1 個城市
- [ ] `family_score` 和 `kids_area` 的邏輯一致（≥3 分通常 `kids_area=true`）
- [ ] `beginner_score` 和實際初級坡道比例相符
- [ ] `audience_tags` 只用固定清單的值
- [ ] 如果有 `null`，在 `notes` 註明原因

---

## 📖 參考資料

- 完整規則：`docs/data-cleaning-rules.md`
- Schema 定義：`docs/schema-design.md`
- 標準範本：`kamui-cleaning-report.md`（神居滑雪場檢查報告）
