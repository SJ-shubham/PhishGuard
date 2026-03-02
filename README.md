# PhishGuard

A phishing URL detection system combining an XGBoost machine learning model with a multi-layer heuristic engine. Given any URL, PhishGuard produces a 0–100 risk score, a risk level verdict, SHAP-based feature attribution, and a structured PDF report — all without any external AI API calls.

---

## Architecture

```
URL Input
   │
   ├─► Feature Extraction (49 features)
   │       ├─ URL features     (length, special chars, TLD prob, entropy …)
   │       └─ Content features (page structure, forms, external refs …)
   │
   ├─► XGBoost Model  →  P(phishing)   [0.0 – 1.0]
   │
   ├─► Heuristic Engine (9 checks, concurrent)
   │       ├─ Brand impersonation  (homoglyph + typosquat, Levenshtein)
   │       ├─ DNS resolution
   │       ├─ SSL / HTTPS validity
   │       ├─ WHOIS domain age
   │       ├─ TLD reputation
   │       ├─ IP-based domain
   │       ├─ IP embedded in subdomain
   │       ├─ Phishing keyword scan (50+ keywords)
   │       └─ Punycode / IDN detection
   │
   ├─► Trust Calibration
   │       trust_factor = 1.0 − (n_clean_signals / 6) × 0.6
   │       (reduces ML weight when all network signals are clean)
   │
   ├─► Score Fusion  →  final_score = raw / 150 × 100
   │
   ├─► SHAP Explanation  (waterfall + heatmap PNGs)
   │
   └─► PDF Report  →  outputs/reports/<url>_<timestamp>.pdf
```

---

## Risk Levels

| Score   | Level    | Meaning                    |
|---------|----------|----------------------------|
| 0 – 25  | Low      | Safe to visit              |
| 25 – 50 | Medium   | Proceed with caution       |
| 50 – 75 | High     | Likely phishing            |
| 75+     | Critical | Do not visit               |

---

## Score Fusion (signal weights)

| Signal                | Max Points |
|-----------------------|-----------|
| ML base (calibrated)  | 60        |
| Brand impersonation   | 30        |
| IP-based URL          | 30        |
| IP in subdomain       | 25        |
| Punycode / IDN        | 20        |
| Suspicious TLD        | 20        |
| Domain age            | 20        |
| Content indicators    | 20        |
| SSL failure           | 15        |
| DNS failure           | 15        |
| Keyword signals       | 15        |
| **RAW_MAX**           | **150**   |

---

## Model Performance

Trained on [PhiUSIIL Phishing URL Dataset](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset) — 235,795 URLs (47,159 test set).

| Metric       | Score  |
|--------------|--------|
| Accuracy     | 100.0% |
| Precision    | 1.0000 |
| Recall       | 1.0000 |
| F1 Score     | 1.0000 |
| AUC-ROC      | 1.0000 |
| CV F1 (mean) | 0.9999 |

---

## Verified Test Results

| URL                                          | Expected   | Score | Level    |
|----------------------------------------------|------------|-------|----------|
| https://www.google.com                       | Legitimate | 15.9  | Low      |
| https://www.github.com                       | Legitimate | 2.9   | Low      |
| https://www.wikipedia.org                    | Legitimate | 15.9  | Low      |
| https://www.kaggle.com                       | Legitimate | 15.9  | Low      |
| https://www.geeksforgeeks.org                | Legitimate | 15.0  | Low      |
| http://paypa1-secure-login.tk/verify         | Phishing   | 82.0  | Critical |
| http://192.168.1.1/admin/login               | Phishing   | 87.0  | Critical |
| http://g00gle-verify.xyz/update              | Phishing   | 75.0  | Critical |
| http://192.168.0.1.secure-login-update.com   | Phishing   | 85.3  | Critical |
| http://xn--google-7hd.com                   | Phishing   | 68.0  | High     |

---

## Project Structure

```
PhishGuard/
├── src/
│   ├── predictor.py          # Main prediction pipeline
│   ├── fusion.py             # Score fusion + trust calibration
│   ├── explainer.py          # SHAP waterfall + heatmap plots
│   ├── report.py             # Deterministic PDF report engine
│   ├── features/
│   │   ├── url_features.py   # 49 URL/content feature extractors
│   │   └── content_features.py
│   └── heuristics/
│       ├── brand.py          # Brand impersonation (homoglyph + typosquat)
│       ├── dns_ssl.py        # DNS + SSL/HTTPS checks
│       ├── whois_age.py      # Domain age via WHOIS
│       └── path_analysis.py  # TLD, path, IP-subdomain, keywords, punycode
│
├── models/
│   ├── phishguard_model.pkl  # Trained XGBoost model
│   ├── dynamic_model.pkl     # Calibrated probability model
│   ├── feature_list.pkl      # Feature column order
│   ├── eval_report.txt       # Model evaluation metrics
│   └── plots/                # Confusion matrix, feature importances
│
├── train.py                  # Model training script
├── test_predict.py           # CLI analyzer + batch tester
├── main.py                   # Entry point (to be expanded)
├── requirements.txt
└── .gitignore
```

---

## Installation

```bash
git clone https://github.com/<your-username>/PhishGuard.git
cd PhishGuard

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

> **Dataset**: Download [PhiUSIIL_Phishing_URL_Dataset.csv](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset) and place it in `dataset/`.
> **Pre-trained models** are included in `models/` — no retraining required.

---

## Usage

### Analyze a single URL
```bash
python -X utf8 test_predict.py "https://example.com"
```

### Run full test batch (10 URLs)
```bash
python -X utf8 test_predict.py --batch
```

Each analysis produces:
- Terminal output with score breakdown, heuristic signals, ML features, and SHAP attribution
- SHAP plots saved to `outputs/shap/`
- PDF report saved to `outputs/reports/`

### Retrain the model
```bash
python train.py
```

---

## PDF Report Sections

Each analysis automatically generates a structured PDF with 7 sections:

1. **Header** — Report ID, URL, timestamp
2. **Risk Summary** — Score meter, verdict badge, ML probabilities, trust factor
3. **Score Breakdown** — Contribution table for all 11 signals
4. **Heuristic Findings** — DNS, SSL, HTTPS, Brand, Domain Age, TLD, IP Subdomain, Keywords, Punycode, Path
5. **SHAP Attribution** — Top risk and legitimate features with bar visualization + embedded waterfall plot
6. **Recommendations** — Flag-driven security advice (homoglyph warning, TLD alert, etc.)
7. **Technical Appendix** — All 49 ML feature values

---

## Key Design Decisions

### Trust Calibration (replaces hardcoded whitelist)
Instead of a whitelist of "trusted" domains, the system measures how many heuristic signals are clean (SSL OK, DNS OK, old domain, clean TLD, no IP, no brand hit). The ML weight is reduced proportionally:

```
trust_factor = 1.0 − (n_clean_signals / 6) × 0.6
```

With all 6 signals clean → trust_factor = 0.40 → ML contributes at 40% weight.
This is why `google.com` scores 15.9 (Low) even though the raw ML output is high, and why `paypa1-secure-login.tk` scores 82.0 (Critical) regardless.

### Concurrent Heuristics
All 9 heuristic checks run in parallel via `ThreadPoolExecutor(max_workers=9)`, keeping response time under ~6 seconds even with DNS/SSL/WHOIS lookups.

### Homoglyph Detection
`paypa1` → normalizes to `paypal` via digit-to-letter mapping (1→l, 0→o, 3→e, …). If normalized form matches a brand but raw form does not, it's flagged as a homoglyph attack (distance = 0).

---

## Phases Completed

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Dataset preparation + EDA | Done |
| 2 | Feature engineering (49 features) | Done |
| 3 | XGBoost model training + evaluation | Done |
| 4 | Heuristic engine (brand, DNS, SSL, WHOIS, TLD, path, IP, keywords, punycode) | Done |
| 5 | Score fusion + trust calibration + SHAP explanations | Done |
| 6 | Deterministic PDF report engine | Done |
| 7 | FastAPI backend | Pending |
| 8 | Next.js frontend | Pending |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ML Model | XGBoost |
| Explainability | SHAP (TreeExplainer) |
| Network Heuristics | dnspython, requests, python-whois, ssl |
| Brand Matching | python-Levenshtein + custom homoglyph map |
| PDF Reports | ReportLab (Platypus) |
| Backend (planned) | FastAPI + Uvicorn |
| Frontend (planned) | Next.js |
