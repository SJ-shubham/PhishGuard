# PhishGuard - 4 Member Team Visual Summary

```
╔════════════════════════════════════════════════════════════════════════════╗
║                      PHISHGUARD PROJECT - 4 MEMBERS                       ║
╚════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────┬──────────────────────────┬──────────────────────┐
│   MEMBER 1: FRONTEND     │   MEMBER 2: BACKEND      │   MEMBER 3: ML       │
│   React + Vite           │   FastAPI + MongoDB      │   XGBoost + SHAP     │
│   30% Contribution       │   35% Contribution       │   30% Contribution   │
│   60-80 hours            │   80-100 hours           │   70-90 hours        │
│   2000-3000 LOC          │   3000-4000 LOC          │   2500-3500 LOC      │
└──────────────────────────┴──────────────────────────┴──────────────────────┘
                            │
                            ▼
                ┌───────────────────────────┐
                │  MEMBER 4: DOCUMENTATION  │
                │  Data Prep + Guides       │
                │  5% Contribution (Lighter)│
                │  20-30 hours              │
                │  500-1000 LOC             │
                └───────────────────────────┘

════════════════════════════════════════════════════════════════════════════

FRONT-END (MEMBER 1)
│
├─ Pages/
│  ├─ Dashboard.jsx          ← URL input, latest result
│  ├─ History.jsx            ← Paginated scan history
│  ├─ ScanDetail.jsx         ← Full result breakdown
│  ├─ BulkScan.jsx           ← Batch analysis (10 URLs)
│  ├─ Login.jsx              ← Authentication
│  ├─ Register.jsx           ← Sign up
│  └─ Profile.jsx            ← User settings
│
├─ Components/
│  ├─ ScoreGauge.jsx         ← Circular gauge (0-100)
│  ├─ RiskBadge.jsx          ← Risk level badge
│  ├─ ScanProgress.jsx       ← Progress bar
│  ├─ ResultCard.jsx         ← Quick result view
│  ├─ Navbar.jsx             ← Navigation
│  └─ ProtectedRoute.jsx     ← Auth guard
│
├─ Context/
│  └─ AuthContext.jsx        ← JWT token management
│
├─ API/
│  └─ client.js              ← Axios with interceptors
│
└─ Styling/
   └─ Tailwind CSS           ← Responsive design

════════════════════════════════════════════════════════════════════════════

BACKEND (MEMBER 2)
│
├─ main.py                  ← FastAPI app setup
├─ config.py                ← Environment settings
├─ database.py              ← MongoDB connection
├─ redis_client.py          ← Redis async client
│
├─ Models/
│  ├─ user.py               ← User schema
│  └─ scan.py               ← Scan schema
│
├─ Services/
│  ├─ auth_service.py       ← JWT, password hashing
│  ├─ scan_service.py       ← Cache, persistence
│  └─ report_service.py     ← PDF generation
│
├─ Routes/
│  ├─ auth.py               ← /auth/register, /login, /logout
│  ├─ scans.py              ← /api/scan, /api/scans/*, /api/bulk
│  └─ public.py             ← /public/scan (no auth)
│
└─ Middleware/
   ├─ auth_guard.py         ← JWT validation
   └─ rate_limiter.py       ← 10 requests/min enforcement

════════════════════════════════════════════════════════════════════════════

ML PIPELINE (MEMBER 3)
│
├─ predictor.py             ← Main orchestrator
├─ fusion.py                ← Score fusion + trust calibration
├─ explainer.py             ← SHAP explanations
├─ report.py                ← PDF report generation
├─ train.py                 ← Model training
├─ test_predict.py          ← CLI interface
│
├─ Features/
│  ├─ url_features.py       ← 21 static features
│  └─ content_features.py   ← 28 dynamic features
│
├─ Heuristics/
│  ├─ brand.py              ← Levenshtein + homoglyph
│  ├─ dns_ssl.py            ← DNS + SSL checks
│  ├─ whois_age.py          ← Domain age (WHOIS)
│  └─ path_analysis.py      ← TLD, IP, keywords, punycode
│
└─ Models/
   ├─ phishguard_model.pkl  ← Trained XGBoost
   ├─ feature_list.pkl      ← Feature columns
   ├─ eval_report.txt       ← Metrics
   └─ plots/                ← Confusion matrix, feature importance

════════════════════════════════════════════════════════════════════════════

DOCUMENTATION (MEMBER 4)
│
├─ README.md                ← Project overview
├─ ARCHITECTURE.md          ← System design + diagrams
├─ API_DOCUMENTATION.md     ← Endpoint reference
├─ FEATURE_ENGINEERING.md   ← 49 features dictionary
├─ MODEL_TRAINING.md        ← Training process
├─ DEPLOYMENT.md            ← Production setup
├─ SECURITY.md              ← Security considerations
├─ CONTRIBUTING.md          ← Dev guidelines
├─ FAQ.md                   ← Common questions
│
├─ Dataset/
│  ├─ PhiUSIIL_Dataset.csv  ← Original 235K URLs
│  ├─ preprocessing.py      ← Data cleaning
│  ├─ eda.py                ← Exploratory analysis
│  ├─ class_distribution.png     ← Visualization
│  └─ feature_distributions.png  ← Visualization
│
└─ Deployment/
   ├─ docker-compose.yml    ← Docker setup
   ├─ Dockerfile.backend    ← Backend container
   ├─ Dockerfile.frontend   ← Frontend container
   └─ .env.example          ← Environment template

════════════════════════════════════════════════════════════════════════════

DATA FLOW: URL TO RISK SCORE
────────────────────────────

   USER (Browser)
   │
   ▼
[MEMBER 1: Frontend]
   Dashboard page
   │ POST /api/scan (with JWT token)
   ▼
[MEMBER 2: Backend]
   FastAPI receives request
   ├─ JWT validation (auth guard)
   ├─ Rate limit check (10/min)
   ├─ Cache lookup (Redis)
   │  → Cache hit? Return cached result
   │  → Cache miss? Continue...
   ▼
[MEMBER 3: ML Engine]
   ├─ Extract 49 features (url + content)
   ├─ Run XGBoost model
   ├─ Run 9 heuristics (parallel)
   ├─ Calculate trust calibration
   ├─ Fuse scores (11 signals)
   ├─ Generate SHAP explanation
   └─ Generate PDF report
   │
   ▼
[MEMBER 2: Backend]
   ├─ Save to MongoDB
   ├─ Cache in Redis
   ├─ Send SSE progress events
   │
   ▼
[MEMBER 1: Frontend]
   Display ScoreGauge, breakdown, SHAP charts
   │
   ▼
   USER sees result + can download PDF

════════════════════════════════════════════════════════════════════════════

CONTRIBUTION BREAKDOWN

Member 1 (Frontend):        ███████████████░░░░░░░░░░░░░ 30%
Member 2 (Backend):          ████████████████░░░░░░░░░░░░ 35%
Member 3 (ML):             ███████████████░░░░░░░░░░░░░ 30%
Member 4 (Docs):           █░░░░░░░░░░░░░░░░░░░░░░░░░░░  5%

════════════════════════════════════════════════════════════════════════════

KEY METRICS

                Frontend    Backend      ML         Docs       Total
Hours           60-80       80-100       70-90      20-30      230-300
LOC             2-3K        3-4K         2.5-3.5K   0.5-1K     8-11.5K
Files           20+         15+          15+        12+        60+
Complexity      Medium      High         High       Low        High

════════════════════════════════════════════════════════════════════════════

INTEGRATION POINTS & DEPENDENCIES

Frontend (M1) ←─────────────────→ Backend (M2)
    │                                │
    │                                ▼
    │                          ML Engine (M3)
    │                                │
    └────────────────────────────────┘
    
    All use Data from Member 4

════════════════════════════════════════════════════════════════════════════

VIVA PREPARATION BY MEMBER

M1 Viva Topics:
  • React component architecture
  • JWT authentication flow
  • SSE real-time updates
  • Responsive design (Tailwind)
  • API integration (Axios)

M2 Viva Topics:
  • FastAPI + async operations
  • MongoDB schema & indexes
  • Redis caching strategy
  • Rate limiting system
  • Error handling (graceful degradation)

M3 Viva Topics:
  • 49 features explanation
  • XGBoost model architecture
  • 9 heuristic checks (parallel)
  • Trust calibration (innovation)
  • Score fusion algorithm
  • SHAP explainability
  • Full ML pipeline flow

M4 Viva Topics:
  • Dataset preparation & EDA
  • Project architecture overview
  • Feature engineering dictionary
  • Deployment procedure
  • API reference documentation
  • Security considerations

════════════════════════════════════════════════════════════════════════════

SUCCESS CRITERIA CHECKLIST

Frontend (M1):
  ✅ All pages responsive
  ✅ JWT auth working
  ✅ SSE progress updates
  ✅ Error handling
  ✅ Smooth animations

Backend (M2):
  ✅ All routes working
  ✅ Database indexes created
  ✅ Rate limiting functional
  ✅ Token refresh working
  ✅ Redis caching effective

ML (M3):
  ✅ Model trained (100% test accuracy)
  ✅ 49 features extracted
  ✅ 9 heuristics working
  ✅ SHAP explanations generated
  ✅ PDF reports generated
  ✅ Prediction time < 7s

Docs (M4):
  ✅ Dataset preprocessed
  ✅ 10+ documentation files
  ✅ All APIs documented
  ✅ Architecture diagrams clear
  ✅ Deployment guide works

════════════════════════════════════════════════════════════════════════════

TIMELINE

Week 1:     Setup & Planning
Week 2-3:   Core Development
Week 4-5:   Heuristics & Integration
Week 6-7:   Polish & Testing
Week 8:     Viva Preparation

════════════════════════════════════════════════════════════════════════════

QUICK CONTACT

Issue with Frontend?        → Contact Member 1
Issue with Backend API?     → Contact Member 2
Issue with ML/Model?        → Contact Member 3
Issue with Docs/Data?       → Contact Member 4

════════════════════════════════════════════════════════════════════════════
```

---

# 📋 Reference: File Ownership

## Member 1 (Frontend) Owns:
- `frontend/` directory entirely
- React components, pages, styles
- Vite configuration
- package.json (frontend)

## Member 2 (Backend) Owns:
- `backend/` directory entirely
- FastAPI setup (main.py, routes)
- Database models
- Middleware and services
- Configuration files

## Member 3 (ML) Owns:
- `src/` directory (features, heuristics, fusion, explainer)
- `train.py` (model training)
- `test_predict.py` (CLI interface)
- `models/` (trained model + artifacts)

## Member 4 (Documentation) Owns:
- All `.md` documentation files
- `dataset/` directory (preprocessing)
- Deployment/Docker files
- `.env.example` and configuration examples

---

# 📞 Communication Channels

## Daily
- Slack #standup (async updates)
- Share blockers immediately

## Weekly
- **Team Sync**: Tuesday 2 PM (1 hour)
- Review progress, adjust timeline

## Code Review
- All PRs need 1 review from team
- Approval before merge to main

## Emergency
- Direct message for urgent issues
- Rotate on-call for production issues

---

**You have everything you need to divide and conquer! 🚀**

Questions? Refer to:
1. **TEAM_DIVISION_4_MEMBERS.md** (Detailed)
2. **TEAM_DIVISION_QUICKREF.md** (Quick Reference)
3. This visual summary (Big Picture)

