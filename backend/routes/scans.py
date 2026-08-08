import asyncio
import json
import os
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from backend.database import get_db
from backend.middleware.auth_guard import get_current_user
from backend.middleware.rate_limiter import check_scan_rate_limit
from backend.models.scan import ScanRequest, ScanResponse, ScanSummary, BulkScanRequest
from backend.services.scan_service import (
    get_cached_scan, cache_scan,
    result_to_document, document_to_response,
)
from backend.services.report_service import generate_report_to_tempfile

router = APIRouter()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


def _run_predict(url: str):
    """Run predict() synchronously — called in thread executor."""
    from src.predictor import predict
    return predict(url)


# ── POST /api/scan  (SSE stream) ──────────────────────────────────────────────

@router.post("/scan")
async def scan_url(
    body:         ScanRequest,
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    url     = body.url.strip()
    user_id = str(current_user["_id"])

    await check_scan_rate_limit(user_id)

    async def event_stream():
        # 1. Check cache first
        cached = await get_cached_scan(url)
        if cached:
            # Still create a user scan record from cached data
            doc = {**cached, "user_id": user_id,
                   "timestamp": datetime.utcnow()}
            doc.pop("_id", None)
            result = await db["scans"].insert_one(doc)
            await db["users"].update_one(
                {"_id": current_user["_id"]},
                {"$inc": {"scan_count": 1}},
            )
            cached["id"] = str(result.inserted_id)
            yield _sse("cached", {"message": "Result loaded from cache"})
            yield _sse("done", cached)
            return

        # 2. Emit progress events while scan runs
        steps = [
            ("progress", {"step": "dns",      "message": "Checking DNS resolution…"}),
            ("progress", {"step": "ssl",      "message": "Validating SSL certificate…"}),
            ("progress", {"step": "brand",    "message": "Checking brand impersonation…"}),
            ("progress", {"step": "whois",    "message": "Looking up domain age…"}),
            ("progress", {"step": "keywords", "message": "Scanning for phishing keywords…"}),
            ("progress", {"step": "ml",       "message": "Running ML model + SHAP…"}),
        ]

        loop      = asyncio.get_event_loop()
        task      = loop.run_in_executor(None, _run_predict, url)
        step_idx  = 0
        interval  = 1.2  # seconds between fake progress events

        while not task.done():
            if step_idx < len(steps):
                yield _sse(*steps[step_idx])
                step_idx += 1
            await asyncio.sleep(interval)

        result = task.result()

        # 3. Persist to MongoDB
        doc    = result_to_document(result, user_id)
        ins    = await db["scans"].insert_one(doc)
        doc_id = str(ins.inserted_id)
        await db["users"].update_one(
            {"_id": current_user["_id"]},
            {"$inc": {"scan_count": 1}},
        )

        # 4. Cache core result
        response_data = document_to_response({**doc, "_id": ins.inserted_id})
        await cache_scan(url, response_data)

        yield _sse("done", response_data)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":  "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── GET /api/scans  (paginated history) ───────────────────────────────────────

@router.get("/scans", response_model=dict)
async def list_scans(
    page:         int  = 1,
    limit:        int  = 20,
    risk_level:   str  = "",
    sort_by:      str  = "timestamp",   # "timestamp" | "score"
    order:        str  = "desc",
    search:       str  = "",
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    user_id = str(current_user["_id"])
    query: dict = {"user_id": user_id}

    if risk_level and risk_level != "All":
        query["risk_level"] = risk_level
    if search:
        query["url"] = {"$regex": search, "$options": "i"}

    sort_dir  = -1 if order == "desc" else 1
    sort_field = "timestamp" if sort_by == "timestamp" else "score"

    skip  = (page - 1) * limit
    total = await db["scans"].count_documents(query)
    docs  = await db["scans"].find(query)\
                             .sort(sort_field, sort_dir)\
                             .skip(skip)\
                             .limit(limit)\
                             .to_list(length=limit)

    items = [
        {
            "id":         str(d["_id"]),
            "url":        d["url"],
            "timestamp":  d["timestamp"],
            "score":      d["score"],
            "risk_level": d["risk_level"],
            "verdict":    d["verdict"],
        }
        for d in docs
    ]

    return {
        "items": items,
        "total": total,
        "page":  page,
        "pages": max(1, (total + limit - 1) // limit),
    }


# ── GET /api/scans/stats ──────────────────────────────────────────────────────

@router.get("/scans/stats")
async def scan_stats(
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    user_id = str(current_user["_id"])
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id":        None,
            "total":      {"$sum": 1},
            "avg_score":  {"$avg": "$score"},
            "phishing":   {"$sum": {"$cond": [{"$gte": ["$score", 50]}, 1, 0]}},
            "safe":       {"$sum": {"$cond": [{"$lt":  ["$score", 25]}, 1, 0]}},
        }},
    ]
    rows = await db["scans"].aggregate(pipeline).to_list(1)
    if not rows:
        return {"total": 0, "phishing_caught": 0, "safe": 0, "avg_score": 0.0}
    r = rows[0]
    return {
        "total":           r["total"],
        "phishing_caught": r["phishing"],
        "safe":            r["safe"],
        "avg_score":       round(r["avg_score"], 1),
    }


# ── GET /api/scans/{id} ────────────────────────────────────────────────────────

@router.get("/scans/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id:      str,
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    try:
        doc = await db["scans"].find_one({"_id": ObjectId(scan_id)})
    except Exception:
        doc = None

    if not doc or doc["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=404, detail="Scan not found")

    return document_to_response(doc)


# ── DELETE /api/scans/{id} ────────────────────────────────────────────────────

@router.delete("/scans/{scan_id}", status_code=204)
async def delete_scan(
    scan_id:      str,
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    try:
        doc = await db["scans"].find_one(
            {"_id": ObjectId(scan_id)},
            {"user_id": 1},
        )
    except Exception:
        doc = None

    if not doc or doc["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=404, detail="Scan not found")

    await db["scans"].delete_one({"_id": ObjectId(scan_id)})
    await db["users"].update_one(
        {"_id": current_user["_id"]},
        {"$inc": {"scan_count": -1}},
    )


# ── GET /api/scans/{id}/report  (PDF download) ───────────────────────────────

@router.get("/scans/{scan_id}/report")
async def download_report(
    scan_id:      str,
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    try:
        doc = await db["scans"].find_one({"_id": ObjectId(scan_id)})
    except Exception:
        doc = None

    if not doc or doc["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=404, detail="Scan not found")

    loop     = asyncio.get_event_loop()
    pdf_path = await loop.run_in_executor(None, generate_report_to_tempfile, doc)

    def iter_and_delete():
        try:
            with open(pdf_path, "rb") as f:
                yield from f
        finally:
            try:
                os.remove(pdf_path)
                os.rmdir(os.path.dirname(pdf_path))
            except Exception:
                pass

    filename = f"phishguard_report_{scan_id[:8]}.pdf"
    return StreamingResponse(
        iter_and_delete(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── POST /api/scans/{id}/rescan ───────────────────────────────────────────────

@router.post("/scans/{scan_id}/rescan")
async def rescan(
    scan_id:      str,
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    try:
        doc = await db["scans"].find_one({"_id": ObjectId(scan_id)}, {"url": 1, "user_id": 1})
    except Exception:
        doc = None

    if not doc or doc["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=404, detail="Scan not found")

    url    = doc["url"]
    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _run_predict, url)

    new_doc = result_to_document(result, str(current_user["_id"]))
    await db["scans"].update_one(
        {"_id": ObjectId(scan_id)},
        {"$set": {k: v for k, v in new_doc.items() if k != "user_id"}},
    )
    updated = await db["scans"].find_one({"_id": ObjectId(scan_id)})
    await cache_scan(url, document_to_response(updated))
    return document_to_response(updated)


# ── POST /api/scan/bulk ───────────────────────────────────────────────────────

@router.post("/scan/bulk")
async def bulk_scan(
    body:         BulkScanRequest,
    current_user: dict = Depends(get_current_user),
    db            = Depends(get_db),
):
    user_id = str(current_user["_id"])
    urls    = list(dict.fromkeys(u.strip() for u in body.urls))[:10]  # dedupe

    await check_scan_rate_limit(user_id)

    loop    = asyncio.get_event_loop()
    tasks   = [loop.run_in_executor(None, _run_predict, url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output     = []
    scan_count = 0
    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            output.append({"url": url, "error": str(result)})
            continue
        doc = result_to_document(result, user_id)
        ins = await db["scans"].insert_one(doc)
        await cache_scan(url, document_to_response({**doc, "_id": ins.inserted_id}))
        output.append({
            "id":         str(ins.inserted_id),
            "url":        url,
            "score":      result.risk_score,
            "risk_level": result.risk_level,
            "verdict":    result.verdict,
        })
        scan_count += 1

    if scan_count:
        await db["users"].update_one(
            {"_id": current_user["_id"]},
            {"$inc": {"scan_count": scan_count}},
        )

    return output