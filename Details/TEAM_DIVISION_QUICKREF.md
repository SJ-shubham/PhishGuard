# 4-Member Team Division - Quick Reference

---

# 📊 TEAM BREAKDOWN TABLE

| Aspect | Member 1: Frontend | Member 2: Backend | Member 3: ML | Member 4: Docs |
|--------|------------------|------------------|------------|----------------|
| **Contribution %** | 30% | 35% | 30% | 5% |
| **Role Title** | Frontend Developer | Backend Architect | ML Engineer | Data/Doc Lead |
| **Tech Stack** | React, Vite, Tailwind | FastAPI, MongoDB, Redis | XGBoost, SHAP | Markdown, Python |
| **Estimated Hours** | 60-80 | 80-100 | 70-90 | 20-30 |
| **Lines of Code** | 2,000-3,000 | 3,000-4,000 | 2,500-3,500 | 500-1,000 |

---

# 🎯 MEMBER 1: FRONTEND DEVELOPMENT (30%)

## What You Own
- **React UI** - All user-facing pages and components
- **State Management** - Authentication context, token handling
- **Real-time Updates** - SSE integration for progress streaming
- **Styling** - Tailwind CSS design system
- **API Integration** - Axios HTTP client with JWT interceptors

## Key Deliverables
| Deliverable | Description | Lines of Code |
|-------------|---|---|
| **Dashboard** | Main URL input page, latest result display | 400-500 |
| **History** | Paginated scan history with filters | 350-400 |
| **Scan Detail** | Full result breakdown, heuristics, SHAP | 400-500 |
| **Bulk Scan** | Batch URL analysis (max 10) | 250-300 |
| **Auth Pages** | Login, Register, Profile | 300-350 |
| **Components** | ScoreGauge, RiskBadge, ScanProgress, ResultCard | 400-500 |
| **API Client** | Axios setup with interceptors | 100-150 |
| **Auth Context** | JWT token management | 150-200 |
| **Styling** | Tailwind + responsive design | 200-300 |

**Total: ~2,500-3,300 lines**

## Key Files to Create/Modify
```
frontend/
├── src/pages/
│   ├── Dashboard.jsx
│   ├── History.jsx
│   ├── ScanDetail.jsx
│   ├── BulkScan.jsx
│   ├── Login.jsx
│   ├── Register.jsx
│   └── Profile.jsx
├── src/components/
│   ├── ScoreGauge.jsx
│   ├── RiskBadge.jsx
│   ├── ScanProgress.jsx
│   ├── ResultCard.jsx
│   ├── Navbar.jsx
│   ├── ProtectedRoute.jsx
│   └── Modal.jsx
├── src/context/
│   └── AuthContext.jsx
├── src/api/
│   └── client.js
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Success Criteria
- ✅ All pages responsive (desktop + mobile)
- ✅ JWT authentication working
- ✅ Real-time SSE progress updates
- ✅ Smooth animations + good UX
- ✅ Error handling with user feedback
- ✅ Dark/light mode (optional)

## Integration with Others
- **Calls Member 2's APIs**: `/auth/*`, `/api/scan*`, `/api/scans*`
- **Uses Member 3's results**: Display SHAP, score breakdown, heuristics

---

# 🚀 MEMBER 2: BACKEND & ARCHITECTURE (35%)

## What You Own
- **FastAPI Application** - Core web framework, routing, middleware
- **Database Layer** - MongoDB schema, indexes, queries
- **Caching Layer** - Redis for results, tokens, rate limiting
- **Authentication System** - JWT tokens, password hashing, token refresh
- **API Endpoints** - All scan, auth, history routes
- **Business Logic** - Coordinate ML pipeline with storage
- **Error Handling** - Graceful degradation, logging
- **SSE Streaming** - Real-time progress to frontend

## Key Deliverables
| Deliverable | Description | Lines of Code |
|---|---|---|
| **FastAPI Setup** | App initialization, lifespan, CORS | 100-150 |
| **Auth Routes** | Register, login, logout, refresh, delete | 300-400 |
| **Scan Routes** | Single scan (SSE), batch, history, detail | 400-500 |
| **Report Route** | PDF generation + download | 150-200 |
| **Database Layer** | MongoDB connection, indexes, queries | 200-300 |
| **Redis Client** | Caching, rate limiting, blacklist | 150-200 |
| **Middleware** | JWT auth guard, rate limiter | 200-250 |
| **Services** | Auth, scan, report services | 300-400 |
| **Error Handling** | Exception middleware, graceful fallback | 150-200 |
| **Configuration** | Settings from environment variables | 100-150 |

**Total: ~2,800-3,700 lines**

## Key Files to Create/Modify
```
backend/
├── main.py
├── config.py
├── database.py
├── redis_client.py
├── models/
│   ├── user.py
│   └── scan.py
├── services/
│   ├── auth_service.py
│   ├── scan_service.py
│   └── report_service.py
├── routes/
│   ├── auth.py
│   ├── scans.py
│   └── public.py
├── middleware/
│   ├── auth_guard.py
│   └── rate_limiter.py
└── requirements.txt
```

## Success Criteria
- ✅ All routes working with proper auth checks
- ✅ MongoDB indexes for fast queries
- ✅ Redis caching reduces repeated scans to <100ms
- ✅ Rate limiting (10 scans/min/user)
- ✅ SSE streaming with real-time progress
- ✅ Error handling + logging
- ✅ Graceful degradation (Redis/DB failures don't crash)

## Integration with Others
- **Calls Member 3's code**: Import `predict()` function
- **Provides APIs to Member 1**: All endpoints
- **Uses Member 4's data**: Preprocessed dataset

---

# 🧠 MEMBER 3: ML + ML PIPELINE (30%)

## What You Own
- **Feature Extraction** - 21 URL features + 28 content features
- **ML Model Training** - XGBoost setup, hyperparameter tuning, evaluation
- **Heuristic Checks** - 9 security checks (brand, DNS, SSL, WHOIS, TLD, IP, keywords, punycode)
- **Parallel Execution** - ThreadPoolExecutor for concurrent checks
- **Score Fusion** - Combine ML + heuristics into 0-100 risk score
- **Trust Calibration** - Dynamic ML weight adjustment (key innovation!)
- **SHAP Explainability** - Feature attribution, waterfall plots
- **PDF Report Generation** - Deterministic reports with ReportLab

## Key Deliverables
| Deliverable | Description | Lines of Code |
|---|---|---|
| **URL Features (21)** | Static feature extraction | 300-400 |
| **Content Features (28)** | Dynamic feature extraction (HTTP GET) | 400-500 |
| **Brand Impersonation** | Levenshtein + homoglyph detection | 150-200 |
| **DNS Check** | Socket DNS resolution | 100-150 |
| **SSL Check** | Certificate validation | 100-150 |
| **WHOIS Check** | Domain age lookup | 100-150 |
| **Path Analysis** | TLD, IP, keywords, punycode | 200-250 |
| **Parallel Heuristics** | ThreadPoolExecutor orchestration | 100-150 |
| **Trust Calibration** | Dynamic ML weight formula | 100-150 |
| **Score Fusion** | 11 signals + normalization | 150-200 |
| **SHAP Explainer** | TreeExplainer + visualizations | 150-200 |
| **PDF Report** | ReportLab + Platypus | 250-350 |
| **Model Training** | XGBoost training + evaluation | 200-250 |
| **Predictor** | Main prediction orchestrator | 200-250 |

**Total: ~2,500-3,500 lines**

## Key Files to Create/Modify
```
src/
├── predictor.py
├── fusion.py
├── explainer.py
├── report.py
├── features/
│   ├── url_features.py
│   └── content_features.py
├── heuristics/
│   ├── brand.py
│   ├── dns_ssl.py
│   ├── whois_age.py
│   └── path_analysis.py
├── train.py
└── test_predict.py

models/
├── phishguard_model.pkl
├── feature_list.pkl
├── eval_report.txt
└── plots/
```

## Success Criteria
- ✅ 49 features extracted correctly
- ✅ Model achieves ~100% accuracy on test set
- ✅ 9 heuristic checks working + parallel execution
- ✅ Trust calibration reduces false positives
- ✅ Score fusion produces 0-100 risk scores
- ✅ SHAP explanations generated per prediction
- ✅ PDF reports generated on-demand
- ✅ Prediction time: 5-7 seconds per scan

## Integration with Others
- **Provides to Member 2**: `predict(url)` function callable from backend
- **Uses Member 4's data**: Preprocessed dataset for training

---

# 📚 MEMBER 4: DOCUMENTATION + DATA (5% - Lighter)

## What You Own
- **Dataset Preparation** - Download, validate, preprocess
- **Project Documentation** - Comprehensive guides and references
- **API Documentation** - Endpoint reference with examples
- **Architecture Diagrams** - System design visualizations
- **Deployment Guide** - Production setup instructions
- **Feature Dictionary** - Explanations of all 49 features
- **Security Guide** - Best practices and considerations
- **Contributing Guide** - How to contribute code
- **FAQ & Troubleshooting** - Common questions answered

## Key Deliverables
| Deliverable | Description | Effort |
|---|---|---|
| **Data Preprocessing** | Clean, validate dataset | 2-3 hours |
| **EDA Script** | Generate visualizations | 2-3 hours |
| **README.md** | Main project overview | 2-3 hours |
| **ARCHITECTURE.md** | System design + diagrams | 2-3 hours |
| **API_DOCUMENTATION.md** | Detailed API reference | 2-3 hours |
| **FEATURE_ENGINEERING.md** | 49 features dictionary | 2-3 hours |
| **MODEL_TRAINING.md** | Training process guide | 1-2 hours |
| **DEPLOYMENT.md** | Production setup guide | 2-3 hours |
| **SECURITY.md** | Security considerations | 1-2 hours |
| **CONTRIBUTING.md** | Development guidelines | 1-2 hours |
| **FAQ.md** | Common questions | 1-2 hours |
| **Docker & Config** | dockerfile, docker-compose, .env | 2-3 hours |

**Total: 20-30 hours**

## Key Files to Create/Modify
```
/
├── README.md
├── ARCHITECTURE.md
├── API_DOCUMENTATION.md
├── FEATURE_ENGINEERING.md
├── MODEL_TRAINING.md
├── DEPLOYMENT.md
├── SECURITY.md
├── CONTRIBUTING.md
├── TESTING.md
├── FAQ.md
├── LICENSE
├── .env.example
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
│
dataset/
├── PhiUSIIL_Phishing_URL_Dataset.csv
├── preprocessing.py
├── eda.py
├── class_distribution.png
├── feature_distributions.png
└── correlation_heatmap.png
```

## Success Criteria
- ✅ Dataset cleaned and validated
- ✅ 10+ comprehensive documentation files
- ✅ All APIs documented with examples
- ✅ Deployment guide works end-to-end
- ✅ Architecture diagrams clear + accurate
- ✅ FAQ answers common questions
- ✅ Contributing guide helps new developers
- ✅ Code is well-commented

## Integration with Others
- **Reviews all code** for documentation completeness
- **Ensures consistency** across team documentation
- **Validates data** used by Member 3

---

# 📅 TIMELINE & MILESTONES

## Week 1: Setup & Planning
| Member | Task | Deadline |
|--------|------|----------|
| M4 | Download & preprocess dataset | Fri |
| M3 | Feature engineering plan | Fri |
| M2 | Backend architecture design | Fri |
| M1 | UI/UX mockups | Fri |

## Weeks 2-3: Core Development
| Member | Task | Deadline |
|--------|------|----------|
| M1 | Dashboard, History, Detail pages | End week 2 |
| M2 | Auth routes + database layer | End week 2 |
| M3 | Feature extraction + model training | End week 2 |
| M4 | Begin documentation | Ongoing |

## Weeks 4-5: Heuristics & Integration
| Member | Task | Deadline |
|--------|------|----------|
| M1 | Bulk scan, Profile pages | End week 4 |
| M2 | Scan routes + SSE streaming | End week 4 |
| M3 | Heuristics + score fusion | End week 4 |
| M4 | API documentation | End week 4 |

## Weeks 6-7: Polish & Testing
| Member | Task | Deadline |
|--------|------|----------|
| M1 | Responsive design, animations | End week 6 |
| M2 | Error handling, rate limiting | End week 6 |
| M3 | SHAP + PDF reports | End week 6 |
| M4 | Deployment guide + finalize docs | End week 6 |

---

# 🤝 COMMUNICATION PROTOCOL

## Daily Standup (10 min, async)
Slack message in #standup:
```
✅ Completed yesterday: ...
🔄 Working on today: ...
🚧 Blocked by: ... (if any)
```

## Weekly Sync (1 hour, Tuesday 2 PM)
Zoom call to discuss:
- Progress on deliverables
- Integration issues
- Timeline adjustments
- Team blockers

## Code Review Process
- All PRs require 1 review from another member
- Focus on: security, performance, code style
- Approval needed before merge
- Rebase on main before merging

## Documentation Updates
- Member 4 updates TEAM_DIVISION.md weekly
- All code should have docstrings
- Architecture diagrams updated if design changes

---

# 📋 VIVA PREPARATION BY MEMBER

## Member 1 (Frontend) - Your Viva Topics
- **React Architecture**: Component hierarchy, state management
- **Authentication Flow**: JWT tokens, login/logout, token refresh
- **Real-time Updates**: SSE integration, EventSource
- **Responsive Design**: Tailwind CSS, mobile optimization
- **API Integration**: Axios interceptors, error handling
- **Demo**: Show Dashboard → scan → History → Detail flow

## Member 2 (Backend) - Your Viva Topics
- **FastAPI Framework**: Why async? Middleware? Lifespan?
- **Database Design**: MongoDB schema, indexes, query optimization
- **Caching Strategy**: Redis for results, rate limiting, token blacklist
- **Authentication**: JWT HS256, password hashing (bcrypt)
- **Concurrency**: How handle 1000s concurrent requests?
- **Error Handling**: Graceful degradation, logging
- **Demo**: Show API endpoints working, explain database flow

## Member 3 (ML) - Your Viva Topics
- **49 Features**: Why these? How extracted? Predictive power?
- **XGBoost Model**: Why choose it? Hyperparameters? Performance?
- **9 Heuristics**: Each check explained, penalties, why concurrent?
- **Trust Calibration**: Formula, why needed, examples
- **Score Fusion**: How combine 11 signals? Normalization?
- **SHAP Explainability**: How works? Why important?
- **Pipeline**: Full prediction flow, timing breakdown
- **Demo**: Show model training, run prediction on sample URL

## Member 4 (Documentation) - Your Viva Topics
- **Dataset**: What is it? How big? Class distribution?
- **Data Preprocessing**: What cleaning? Why important?
- **Project Overview**: Architecture at high level
- **Feature Dictionary**: All 49 features explained
- **Deployment**: How get system running in production?
- **API Reference**: How use the API?
- **Demo**: Show README guides, deployment guide, architecture diagrams

---

# 🎯 SUCCESS CHECKLIST FOR TEAM

Before viva submission, ensure:

### All Members
- ✅ Code is well-commented and documented
- ✅ No console.log / debug print statements left
- ✅ README updated and comprehensive
- ✅ Architecture diagram included
- ✅ All features complete and tested

### Member 1 (Frontend)
- ✅ All pages responsive (desktop + mobile)
- ✅ Authentication working end-to-end
- ✅ Real-time SSE updates display correctly
- ✅ Error states handled with user feedback
- ✅ Animations smooth and performant

### Member 2 (Backend)
- ✅ All API endpoints working
- ✅ Database indexes created
- ✅ Rate limiting functional
- ✅ JWT token refresh working
- ✅ Redis caching reduces repeated scans

### Member 3 (ML)
- ✅ Model trained and saved
- ✅ Features extracted for 49 dimensions
- ✅ All 9 heuristics working
- ✅ SHAP explanations generated
- ✅ PDF reports generated on-demand
- ✅ Prediction time < 7 seconds

### Member 4 (Documentation)
- ✅ Dataset preprocessed and validated
- ✅ 10+ documentation files completed
- ✅ All APIs documented
- ✅ Architecture diagrams clear
- ✅ Deployment guide tested
- ✅ FAQ addresses common questions

---

# 📞 WHO DOES WHAT - QUICK REFERENCE

**Frontend Issue?** → Contact **Member 1**
**Backend/API Issue?** → Contact **Member 2**
**ML/Model Issue?** → Contact **Member 3**
**Data/Documentation Issue?** → Contact **Member 4**

---

**Good luck building PhishGuard together! 🚀**

