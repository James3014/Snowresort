# 代碼實現計劃

## 專案目標

建立一個雪場資料清洗、驗證、儲存和查詢系統，支援：
- 資料清洗流程自動化
- 資料品質驗證
- 推薦系統基礎功能（相似雪場推薦）
- API 查詢介面

---

## 技術棧選擇

### 後端
- **語言**: Python 3.11+
- **資料庫**: PostgreSQL (結構化資料) + JSON 欄位 (彈性資料)
- **ORM**: SQLAlchemy
- **驗證**: Pydantic
- **API**: FastAPI

### 資料處理
- **清洗工具**: Pandas
- **相似度計算**: scikit-learn (cosine similarity)
- **資料驗證**: JSON Schema + Custom validators

### 開發工具
- **測試**: pytest
- **格式化**: black, isort
- **型別檢查**: mypy
- **版本控制**: git

---

## 專案結構

```
snowresort/
├── src/
│   ├── models/           # 資料模型
│   │   ├── resort.py     # Resort Pydantic model
│   │   └── db_models.py  # SQLAlchemy models
│   ├── services/         # 業務邏輯
│   │   ├── cleaner.py    # 資料清洗
│   │   ├── validator.py  # 資料驗證
│   │   └── recommender.py # 推薦引擎
│   ├── api/              # API endpoints
│   │   ├── resorts.py    # 雪場查詢 API
│   │   └── recommendations.py # 推薦 API
│   ├── db/               # 資料庫相關
│   │   ├── connection.py # 連線設定
│   │   └── queries.py    # 查詢邏輯
│   └── utils/            # 工具函數
│       ├── similarity.py # 相似度計算
│       └── constants.py  # 常數定義
├── data/                 # 資料檔案
│   ├── raw/              # 原始資料
│   ├── processed/        # 清洗後資料
│   └── schemas/          # JSON schemas
├── scripts/              # 執行腳本
│   ├── import_data.py    # 匯入資料
│   ├── validate_data.py  # 驗證資料
│   └── generate_recommendations.py
├── tests/                # 測試
│   ├── test_models.py
│   ├── test_services.py
│   └── test_api.py
├── docs/                 # 文檔（已建立）
├── requirements.txt      # Python 依賴
├── .env.example          # 環境變數範例
└── README.md
```

---

## Phase 1: 基礎架構建立（Week 1）

### 1.1 專案初始化
```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic pandas pytest
```

### 1.2 定義 Pydantic Model

**檔案**: `src/models/resort.py`

```python
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import date

class Region(str, Enum):
    HOKKAIDO = "hokkaido"
    TOHOKU = "tohoku"
    NIIGATA = "niigata"
    NAGANO = "nagano"
    GUNMA = "gunma"
    OTHER_KANTO = "other-kanto"
    CHUBU = "chubu"
    KANSAI = "kansai"
    OTHER = "other"

class PriceLevel(str, Enum):
    BUDGET = "budget"
    MID = "mid"
    PREMIUM = "premium"

class TargetProfile(str, Enum):
    FAMILY = "family"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    BACKCOUNTRY = "backcountry"
    PARK = "park"
    FREESTYLE = "freestyle"

class TravelInfo(BaseModel):
    minutes: int = Field(..., ge=0)
    method: Optional[str] = None
    cost_estimate: Optional[int] = Field(None, ge=0)

class SlopeCount(BaseModel):
    beginner: int = Field(0, ge=0)
    intermediate: int = Field(0, ge=0)
    advanced: int = Field(0, ge=0)

class DataSource(BaseModel):
    official_website: bool = False
    third_party_review: bool = False
    google_maps: bool = False
    manual_inspection: bool = False

class Resort(BaseModel):
    # 基礎識別
    resort_id: str = Field(..., pattern="^[a-z0-9-]+$")
    name_jp: str
    name_en: Optional[str] = None
    website: Optional[str] = None

    # Tier 1: 必備欄位
    region: Region
    prefecture: str
    price_level: PriceLevel
    family_friendly_score: int = Field(..., ge=1, le=5)
    beginner_friendly_level: int = Field(..., ge=1, le=5)
    travel_time_from_city: Dict[str, TravelInfo] = {}
    target_profile: List[TargetProfile] = []

    # Tier 2: 建議欄位
    kids_school: Optional[bool] = None
    facility_tags: Optional[List[str]] = []
    coach_available: Optional[bool] = None
    slope_count: Optional[SlopeCount] = None
    lift_count: Optional[int] = Field(None, ge=0)
    accommodation_nearby: Optional[bool] = None

    # Tier 3: 緩衝區
    tags: List[str] = []
    notes_for_future: Optional[str] = None

    # Meta
    data_source: Optional[DataSource] = None
    last_updated: Optional[date] = None
    data_quality: Optional[str] = Field(None, pattern="^(complete|partial|needs_review)$")

    @validator('target_profile')
    def validate_target_profile(cls, v, values):
        """確保 target_profile 與評分一致"""
        if 'family_friendly_score' in values:
            if values['family_friendly_score'] >= 4 and TargetProfile.FAMILY not in v:
                raise ValueError("親子友善度>=4 應包含 'family' 標籤")
        return v

    class Config:
        use_enum_values = True
```

### 1.3 建立 SQLAlchemy Model

**檔案**: `src/models/db_models.py`

```python
from sqlalchemy import Column, String, Integer, Boolean, JSON, Date, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class RegionEnum(enum.Enum):
    HOKKAIDO = "hokkaido"
    TOHOKU = "tohoku"
    NIIGATA = "niigata"
    NAGANO = "nagano"
    GUNMA = "gunma"
    OTHER_KANTO = "other-kanto"
    CHUBU = "chubu"
    KANSAI = "kansai"
    OTHER = "other"

class PriceLevelEnum(enum.Enum):
    BUDGET = "budget"
    MID = "mid"
    PREMIUM = "premium"

class ResortDB(Base):
    __tablename__ = "resorts"

    resort_id = Column(String, primary_key=True)
    name_jp = Column(String, nullable=False)
    name_en = Column(String)
    website = Column(String)

    region = Column(SQLEnum(RegionEnum), nullable=False)
    prefecture = Column(String, nullable=False)
    price_level = Column(SQLEnum(PriceLevelEnum), nullable=False)

    family_friendly_score = Column(Integer, nullable=False)
    beginner_friendly_level = Column(Integer, nullable=False)

    # JSON 欄位儲存複雜資料
    travel_time_from_city = Column(JSON)
    target_profile = Column(JSON)

    kids_school = Column(Boolean)
    facility_tags = Column(JSON)
    coach_available = Column(Boolean)
    slope_count = Column(JSON)
    lift_count = Column(Integer)
    accommodation_nearby = Column(Boolean)

    tags = Column(JSON)
    notes_for_future = Column(String)

    data_source = Column(JSON)
    last_updated = Column(Date)
    data_quality = Column(String)
```

### 1.4 資料庫初始化腳本

**檔案**: `scripts/init_db.py`

```python
from sqlalchemy import create_engine
from src.models.db_models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/snowresort")

def init_database():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("資料庫初始化完成")

if __name__ == "__main__":
    init_database()
```

---

## Phase 2: 資料清洗與驗證（Week 2）

### 2.1 資料清洗工具

**檔案**: `src/services/cleaner.py`

```python
import pandas as pd
from typing import List, Dict
from src.models.resort import Resort
import json

class ResortDataCleaner:
    """雪場資料清洗工具"""

    def __init__(self, raw_data_path: str):
        self.raw_data = pd.read_csv(raw_data_path)

    def clean_price_level(self, lift_ticket_price: int) -> str:
        """根據纜車票價判定價位等級"""
        if lift_ticket_price < 4000:
            return "budget"
        elif lift_ticket_price <= 6000:
            return "mid"
        else:
            return "premium"

    def calculate_family_score(self, row: Dict) -> int:
        """計算親子友善度"""
        score = 1

        if row.get('kids_area'):
            score += 1
        if row.get('kids_school'):
            score += 1
        if row.get('childcare_service'):
            score += 1
        if row.get('family_facilities'):
            score += 1

        return min(score, 5)

    def calculate_beginner_level(self, beginner_slope_ratio: float) -> int:
        """計算初學者友善度"""
        if beginner_slope_ratio >= 0.5:
            return 5
        elif beginner_slope_ratio >= 0.4:
            return 4
        elif beginner_slope_ratio >= 0.3:
            return 3
        elif beginner_slope_ratio >= 0.2:
            return 2
        else:
            return 1

    def process_all(self) -> List[Resort]:
        """處理所有資料"""
        resorts = []

        for _, row in self.raw_data.iterrows():
            try:
                resort = Resort(
                    resort_id=row['resort_id'],
                    name_jp=row['name_jp'],
                    name_en=row.get('name_en'),
                    region=row['region'],
                    prefecture=row['prefecture'],
                    price_level=self.clean_price_level(row['lift_ticket_price']),
                    family_friendly_score=self.calculate_family_score(row),
                    beginner_friendly_level=self.calculate_beginner_level(
                        row['beginner_slope_ratio']
                    ),
                    travel_time_from_city=json.loads(row.get('travel_time', '{}')),
                    target_profile=json.loads(row.get('target_profile', '[]')),
                    data_quality="complete"
                )
                resorts.append(resort)
            except Exception as e:
                print(f"處理 {row.get('name_jp')} 時出錯: {e}")

        return resorts

    def export_to_json(self, resorts: List[Resort], output_path: str):
        """匯出為 JSON"""
        data = [r.dict() for r in resorts]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
```

### 2.2 資料驗證工具

**檔案**: `src/services/validator.py`

```python
from typing import List, Dict
from src.models.resort import Resort

class ResortValidator:
    """資料品質驗證工具"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_completeness(self, resort: Resort) -> bool:
        """檢查必備欄位完整度"""
        required_fields = [
            'resort_id', 'name_jp', 'region', 'prefecture',
            'price_level', 'family_friendly_score', 'beginner_friendly_level'
        ]

        for field in required_fields:
            if getattr(resort, field) is None:
                self.errors.append(f"{resort.resort_id}: 缺少必備欄位 {field}")
                return False

        return True

    def validate_consistency(self, resort: Resort):
        """檢查邏輯一致性"""
        # 親子友善度 vs 兒童設施
        if resort.family_friendly_score == 5 and not resort.kids_school:
            self.warnings.append(
                f"{resort.resort_id}: 親子友善度5分但沒有兒童雪校"
            )

        # 目標客群 vs 評分
        if 'beginner' in resort.target_profile and resort.beginner_friendly_level < 3:
            self.warnings.append(
                f"{resort.resort_id}: 目標客群含初學者但友善度<3"
            )

    def validate_batch(self, resorts: List[Resort]) -> Dict:
        """批次驗證"""
        total = len(resorts)
        valid = 0

        for resort in resorts:
            if self.validate_completeness(resort):
                valid += 1
            self.validate_consistency(resort)

        return {
            "total": total,
            "valid": valid,
            "completion_rate": valid / total if total > 0 else 0,
            "errors": self.errors,
            "warnings": self.warnings
        }
```

---

## Phase 3: 推薦系統（Week 3）

### 3.1 相似度計算

**檔案**: `src/utils/similarity.py`

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from src.models.resort import Resort

class ResortSimilarityCalculator:
    """計算雪場相似度"""

    REGION_WEIGHTS = {
        "hokkaido": [1, 0, 0, 0, 0],
        "tohoku": [0, 1, 0, 0, 0],
        "niigata": [0, 0, 1, 0, 0],
        "nagano": [0, 0, 0, 1, 0],
        "other": [0, 0, 0, 0, 1]
    }

    PRICE_WEIGHTS = {
        "budget": [1, 0, 0],
        "mid": [0, 1, 0],
        "premium": [0, 0, 1]
    }

    def vectorize_resort(self, resort: Resort) -> np.ndarray:
        """將雪場資料向量化"""
        features = []

        # 地區（5維）
        region_key = resort.region if resort.region in self.REGION_WEIGHTS else "other"
        features.extend(self.REGION_WEIGHTS[region_key])

        # 價位（3維）
        features.extend(self.PRICE_WEIGHTS[resort.price_level])

        # 評分（正規化到 0-1）
        features.append(resort.family_friendly_score / 5)
        features.append(resort.beginner_friendly_level / 5)

        # 目標客群（one-hot, 7維）
        profiles = ["family", "beginner", "intermediate", "advanced",
                   "backcountry", "park", "freestyle"]
        for p in profiles:
            features.append(1 if p in resort.target_profile else 0)

        return np.array(features)

    def find_similar(
        self,
        target_resort: Resort,
        all_resorts: List[Resort],
        top_n: int = 5
    ) -> List[Dict]:
        """找出最相似的雪場"""
        target_vec = self.vectorize_resort(target_resort)

        similarities = []
        for resort in all_resorts:
            if resort.resort_id == target_resort.resort_id:
                continue

            resort_vec = self.vectorize_resort(resort)
            similarity = cosine_similarity(
                target_vec.reshape(1, -1),
                resort_vec.reshape(1, -1)
            )[0][0]

            similarities.append({
                "resort": resort,
                "similarity_score": float(similarity)
            })

        # 排序並回傳 top N
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:top_n]
```

### 3.2 推薦服務

**檔案**: `src/services/recommender.py`

```python
from typing import List, Dict, Optional
from src.models.resort import Resort
from src.utils.similarity import ResortSimilarityCalculator

class ResortRecommender:
    """雪場推薦服務"""

    def __init__(self, resorts: List[Resort]):
        self.resorts = resorts
        self.calculator = ResortSimilarityCalculator()

    def recommend_similar(self, resort_id: str, top_n: int = 5) -> List[Dict]:
        """推薦相似雪場"""
        target = next((r for r in self.resorts if r.resort_id == resort_id), None)
        if not target:
            return []

        return self.calculator.find_similar(target, self.resorts, top_n)

    def filter_by_criteria(
        self,
        region: Optional[str] = None,
        price_level: Optional[str] = None,
        min_family_score: Optional[int] = None,
        min_beginner_level: Optional[int] = None,
        target_profile: Optional[List[str]] = None
    ) -> List[Resort]:
        """根據條件篩選雪場"""
        filtered = self.resorts

        if region:
            filtered = [r for r in filtered if r.region == region]

        if price_level:
            filtered = [r for r in filtered if r.price_level == price_level]

        if min_family_score:
            filtered = [r for r in filtered if r.family_friendly_score >= min_family_score]

        if min_beginner_level:
            filtered = [r for r in filtered if r.beginner_friendly_level >= min_beginner_level]

        if target_profile:
            filtered = [
                r for r in filtered
                if any(p in r.target_profile for p in target_profile)
            ]

        return filtered
```

---

## Phase 4: API 開發（Week 4）

### 4.1 FastAPI 應用

**檔案**: `src/api/main.py`

```python
from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from src.models.resort import Resort
from src.services.recommender import ResortRecommender
import json

app = FastAPI(title="Snow Resort API", version="0.1.0")

# 載入資料（實際應從資料庫讀取）
with open('data/processed/resorts.json', 'r', encoding='utf-8') as f:
    resorts_data = json.load(f)
    resorts = [Resort(**r) for r in resorts_data]

recommender = ResortRecommender(resorts)

@app.get("/")
def root():
    return {"message": "Snow Resort API v0.1"}

@app.get("/resorts", response_model=List[Resort])
def list_resorts(
    region: Optional[str] = Query(None),
    price_level: Optional[str] = Query(None),
    min_family_score: Optional[int] = Query(None, ge=1, le=5),
    min_beginner_level: Optional[int] = Query(None, ge=1, le=5)
):
    """列出所有雪場，支援篩選"""
    filtered = recommender.filter_by_criteria(
        region=region,
        price_level=price_level,
        min_family_score=min_family_score,
        min_beginner_level=min_beginner_level
    )
    return filtered

@app.get("/resorts/{resort_id}", response_model=Resort)
def get_resort(resort_id: str):
    """取得單一雪場資訊"""
    resort = next((r for r in resorts if r.resort_id == resort_id), None)
    if not resort:
        raise HTTPException(status_code=404, detail="雪場不存在")
    return resort

@app.get("/resorts/{resort_id}/similar")
def get_similar_resorts(resort_id: str, top_n: int = Query(5, ge=1, le=10)):
    """取得相似雪場推薦"""
    recommendations = recommender.recommend_similar(resort_id, top_n)
    if not recommendations:
        raise HTTPException(status_code=404, detail="雪場不存在")

    return {
        "resort_id": resort_id,
        "recommendations": [
            {
                "resort_id": r['resort'].resort_id,
                "name_jp": r['resort'].name_jp,
                "similarity_score": r['similarity_score'],
                "region": r['resort'].region,
                "price_level": r['resort'].price_level
            }
            for r in recommendations
        ]
    }

@app.get("/search/family-friendly")
def search_family_friendly(min_score: int = Query(4, ge=1, le=5)):
    """搜尋親子友善雪場"""
    results = recommender.filter_by_criteria(min_family_score=min_score)
    return {
        "count": len(results),
        "resorts": [
            {
                "resort_id": r.resort_id,
                "name_jp": r.name_jp,
                "family_friendly_score": r.family_friendly_score,
                "kids_school": r.kids_school
            }
            for r in results
        ]
    }
```

---

## 開發時間表

| Week | 任務 | 產出 |
|------|------|------|
| 1 | 建立專案架構、定義 Models、初始化資料庫 | 可運行的基礎框架 |
| 2 | 開發清洗工具、驗證工具 | 可清洗並驗證資料 |
| 3 | 實現相似度計算、推薦引擎 | 可產生推薦結果 |
| 4 | 開發 FastAPI、編寫測試、部署 | 可用的 API 服務 |

---

## 下一步

1. **立即開始**：建立專案結構和依賴安裝
2. **準備範例資料**：手動清洗 5-10 個雪場作為測試資料
3. **驗證流程**：用範例資料測試整個 pipeline
4. **逐步擴展**：清洗更多雪場資料

需要我開始實現第一個 Phase 嗎？
