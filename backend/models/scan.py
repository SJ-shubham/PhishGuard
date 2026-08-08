from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


# ── Request ───────────────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=2048)


# ── Sub-schemas (mirror PredictionResult fields) ──────────────────────────────

class ShapValues(BaseModel):
    base_value:   float
    final_value:  float
    top_risk:     list[dict] = []
    top_safe:     list[dict] = []


class ScoreBreakdown(BaseModel):
    ml_base:          float = 0.0
    brand_penalty:    float = 0.0
    ip_penalty:       float = 0.0
    ip_sub_penalty:   float = 0.0
    tld_penalty:      float = 0.0
    domain_age_penalty: float = 0.0
    content_penalty:  float = 0.0
    punycode_penalty: float = 0.0
    ssl_penalty:      float = 0.0
    dns_penalty:      float = 0.0
    keyword_penalty:  float = 0.0
    raw_score:        float = 0.0
    final_score:      float = 0.0
    trust_factor:     float = 1.0


# ── Full scan document stored in MongoDB ─────────────────────────────────────

class ScanDocument(BaseModel):
    user_id:        str
    url:            str
    timestamp:      datetime         = Field(default_factory=datetime.utcnow)
    score:          float
    risk_level:     str
    verdict:        str
    ml_probability: float
    trust_factor:   float
    elapsed_time:   float
    score_breakdown: dict            = {}
    heuristic_flags: dict            = {}
    features:       dict             = {}
    shap_values:    Optional[dict]   = None


# ── API Response ──────────────────────────────────────────────────────────────

class ScanResponse(BaseModel):
    id:             str
    url:            str
    timestamp:      datetime
    score:          float
    risk_level:     str
    verdict:        str
    ml_probability: float
    trust_factor:   float
    elapsed_time:   float
    score_breakdown: dict
    heuristic_flags: dict
    features:       dict
    shap_values:    Optional[dict]


# ── History list item ─────────────────────────────────────────────────────────

class ScanSummary(BaseModel):
    id:         str
    url:        str
    timestamp:  datetime
    score:      float
    risk_level: str
    verdict:    str


# ── Bulk request ──────────────────────────────────────────────────────────────

class BulkScanRequest(BaseModel):
    urls: list[str] = Field(..., min_length=1, max_length=10)
