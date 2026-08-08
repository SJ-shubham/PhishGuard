import os
import tempfile
from src.predictor import PredictionResult
from src.report import generate_report


def build_result_from_doc(doc: dict) -> PredictionResult:
    """Reconstruct a PredictionResult from a MongoDB scan document."""
    score = doc["score"]
    return PredictionResult(
        url            = doc["url"],
        risk_score     = score,
        phishing_prob  = doc["ml_probability"],
        legitimate_prob= round(1.0 - doc["ml_probability"], 6),
        risk_level     = doc["risk_level"],
        verdict        = doc["verdict"],
        is_phishing    = score >= 50,
        features       = doc.get("features", {}),
        score_breakdown= doc.get("score_breakdown", {}),
        heuristic_flags= doc.get("heuristic_flags", {}),
        shap_explanation=None,   # SHAP PNG not regenerated; data stored separately
        elapsed_sec    = doc.get("elapsed_time", 0.0),
    )


def generate_report_to_tempfile(doc: dict) -> str:
    """
    Reconstruct PredictionResult from DB doc, generate PDF into a temp
    directory, and return the absolute path to the PDF file.
    Caller is responsible for deleting the file after streaming.
    """
    result   = build_result_from_doc(doc)
    tmp_dir  = tempfile.mkdtemp()
    pdf_path = generate_report(result, output_dir=tmp_dir, shap_image=None)
    return pdf_path
