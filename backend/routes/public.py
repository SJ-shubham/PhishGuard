import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.models.scan import ScanRequest
from backend.services.scan_service import get_cached_scan, cache_scan, result_to_document

router = APIRouter()


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


def _run_predict(url: str):
    from src.predictor import predict
    return predict(url)


@router.post("/scan")
async def public_scan(body: ScanRequest):
    """
    One free scan without authentication.
    Result is NOT saved to the database.
    Redis cache is still used for repeated URLs.
    """
    url = body.url.strip()

    async def event_stream():
        cached = await get_cached_scan(url)
        if cached:
            cached_out = {k: v for k, v in cached.items() if k != "id"}
            yield _sse("cached", {"message": "Result loaded from cache"})
            yield _sse("done", cached_out)
            return

        steps = [
            ("progress", {"step": "dns",      "message": "Checking DNS resolution…"}),
            ("progress", {"step": "ssl",      "message": "Validating SSL certificate…"}),
            ("progress", {"step": "brand",    "message": "Checking brand impersonation…"}),
            ("progress", {"step": "whois",    "message": "Looking up domain age…"}),
            ("progress", {"step": "keywords", "message": "Scanning for phishing keywords…"}),
            ("progress", {"step": "ml",       "message": "Running ML model + SHAP…"}),
        ]

        loop     = asyncio.get_event_loop()
        task     = loop.run_in_executor(None, _run_predict, url)
        step_idx = 0

        while not task.done():
            if step_idx < len(steps):
                yield _sse(*steps[step_idx])
                step_idx += 1
            await asyncio.sleep(1.2)

        result = task.result()
        doc    = result_to_document(result, user_id="public")

        response_data = {
            "url":             doc["url"],
            "score":           doc["score"],
            "risk_level":      doc["risk_level"],
            "verdict":         doc["verdict"],
            "ml_probability":  doc["ml_probability"],
            "trust_factor":    doc.get("trust_factor", 1.0),
            "elapsed_time":    doc.get("elapsed_time", 0.0),
            "score_breakdown": doc.get("score_breakdown", {}),
            "heuristic_flags": doc.get("heuristic_flags", {}),
            "shap_values":     doc.get("shap_values"),
        }

        await cache_scan(url, response_data)
        yield _sse("done", response_data)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
