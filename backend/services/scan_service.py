import json
import hashlib
from datetime import datetime, timezone

from backend.redis_client import get_redis

_CACHE_TTL = 3600  # 1 hour


def _cache_key(url: str) -> str:
    return f"scan:cache:{hashlib.sha256(url.encode()).hexdigest()}"


async def get_cached_scan(url: str) -> dict | None:
    try:
        raw = await get_redis().get(_cache_key(url))
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None


async def cache_scan(url: str, data: dict) -> None:
    try:
        serialisable = json.loads(json.dumps(data, default=str))
        await get_redis().setex(_cache_key(url), _CACHE_TTL, json.dumps(serialisable))
    except Exception:
        pass  # Redis down — skip caching


def result_to_document(result, user_id: str) -> dict:
    """Convert PredictionResult -> MongoDB document dict."""
    shap = None
    if result.shap_explanation:
        e = result.shap_explanation
        shap = {
            "base_value":       float(e.base_value),
            "prediction_value": float(e.prediction_value),
            "top_risk": [
                {"feature": f, "value": float(v)}
                for f, v in (e.top_risk_features or [])
            ],
            "top_safe": [
                {"feature": f, "value": float(v)}
                for f, v in (e.top_safe_features or [])
            ],
        }

    sb = result.score_breakdown or {}

    return {
        "user_id":         user_id,
        "url":             result.url,
        "timestamp":       datetime.now(timezone.utc),
        "score":           result.risk_score,
        "risk_level":      result.risk_level,
        "verdict":         result.verdict,
        "ml_probability":  result.phishing_prob,
        "trust_factor":    sb.get("trust_factor", 1.0),
        "elapsed_time":    result.elapsed_sec,
        "score_breakdown": sb,
        "heuristic_flags": result.heuristic_flags or {},
        "features":        {
            k: float(v) if hasattr(v, "__float__") else v
            for k, v in (result.features or {}).items()
        },
        "shap_values": shap,
    }


def document_to_response(doc: dict) -> dict:
    """Convert MongoDB document -> API response dict."""
    return {
        "id":              str(doc["_id"]),
        "url":             doc["url"],
        "timestamp":       doc["timestamp"],
        "score":           doc["score"],
        "risk_level":      doc["risk_level"],
        "verdict":         doc["verdict"],
        "ml_probability":  doc["ml_probability"],
        "trust_factor":    doc.get("trust_factor", 1.0),
        "elapsed_time":    doc.get("elapsed_time", 0.0),
        "score_breakdown": doc.get("score_breakdown", {}),
        "heuristic_flags": doc.get("heuristic_flags", {}),
        "features":        doc.get("features", {}),
        "shap_values":     doc.get("shap_values"),
    }
