# PhishGuard - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Core Components](#core-components)
5. [Machine Learning Pipeline](#machine-learning-pipeline)
6. [Backend Architecture](#backend-architecture)
7. [Frontend Architecture](#frontend-architecture)
8. [Data Flow](#data-flow)
9. [Security Features](#security-features)
10. [Deployment & Configuration](#deployment--configuration)

---

## Project Overview

**PhishGuard** is a sophisticated real-time phishing URL detection system that combines machine learning, heuristic analysis, and modern web technologies to identify and classify potentially malicious URLs. The system provides:

- **Real-time URL scanning** with risk scores (0-100)
- **Multi-layer detection** combining XGBoost ML model + 9 concurrent heuristic checks
- **SHAP-based explainability** showing which features contributed to the detection
- **Detailed PDF reports** for each analysis
- **Full-stack web application** with user authentication and scan history
- **RESTful API** with Server-Sent Events (SSE) for real-time progress updates

### Key Metrics
- **Dataset**: PhiUSIIL Phishing URL Dataset (235,795 URLs)
- **Model Performance**: 100% accuracy, F1=1.0000, AUC-ROC=1.0000
- **Features Extracted**: 49 URL and content features
- **Heuristic Checks**: 9 concurrent network/security checks
- **Risk Levels**: Low (0-25), Medium (25-50), High (50-75), Critical (75-100)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / BROWSER                          │
│                      (HTTP/HTTPS Requests)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REACT FRONTEND (Port 5173)                 │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │  Dashboard   │   History    │ Scan Detail  │  Bulk Scan   │ │
│  │ (URL input)  │(filter/sort) │(full result) │ (batch scan) │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
│  Components: ScoreGauge, RiskBadge, ScanProgress, ResultCard   │
└─────────────────────────────────────────────────────────────────┘
                              │ REST API / SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND (Port 8000)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Middleware: JWT Auth | Rate Limiter | CORS             │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Auth Routes  │ Scan Routes  │Public Routes │  Services    │ │
│  │ /auth/*      │ /api/scan*   │ /public/*    │(auth/scan/   │ │
│  │              │              │              │ report)      │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
   ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
   │   MongoDB    │    │    Redis     │    │   ML Engine      │
   │              │    │              │    │   (src/)         │
   │ • users      │    │ • URL cache  │    │ • Feature Extract│
   │ • scans      │    │ • JWT tokens │    │ • XGBoost Model  │
   │              │    │ • Rate limit │    │ • Heuristics     │
   └──────────────┘    └──────────────┘    │ • SHAP Explain   │
                                           │ • PDF Reports    │
                                           └──────────────────┘
```

### Component Interaction Flow

1. **User Input** → React Dashboard accepts URL
2. **Authentication** → JWT validation via middleware
3. **Rate Limiting** → Redis checks 10 scans/min/user limit
4. **Cache Check** → Redis lookup for previous scan results
5. **ML Processing** → If cache miss, run prediction pipeline:
   - Extract 49 features (URL + content)
   - Run XGBoost model → P(phishing)
   - Execute 9 heuristic checks concurrently
   - Apply trust calibration
   - Fuse scores → final 0-100 risk score
   - Generate SHAP explanations
6. **Persistence** → Save to MongoDB
7. **Caching** → Store in Redis (TTL: 1 hour)
8. **Response** → Stream results via SSE to frontend
9. **Visualization** → Render score, signals, SHAP charts
10. **PDF Generation** → On-demand report download

---

## Technology Stack

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | FastAPI | 0.115.0+ | Async REST API with automatic docs |
| ASGI Server | Uvicorn | 0.34.0+ | Production-grade async server |
| ML Model | XGBoost | 3.0.0+ | Gradient boosting classifier |
| Explainability | SHAP | 0.50.0+ | Feature attribution & visualization |
| Data Processing | NumPy, Pandas | 2.2.0+, 3.0.0+ | Numerical computing & data manipulation |
| Database | MongoDB (Motor) | 3.6.0+ | Async NoSQL document storage |
| Caching | Redis (aioredis) | 5.0.0+ | In-memory cache & rate limiting |
| Authentication | python-jose, bcrypt | 3.3.0+, 4.1.0+ | JWT tokens & password hashing |
| PDF Generation | ReportLab | 4.2.0+ | Structured PDF reports |
| Network Analysis | requests, dnspython | 2.32.0+ | HTTP requests & DNS lookups |
| Web Scraping | BeautifulSoup4 | 4.12.0+ | HTML parsing for content features |
| Domain Analysis | tldextract, python-whois | 5.1.0+, 0.9.0+ | TLD extraction & WHOIS lookups |
| String Matching | python-Levenshtein | 0.25.0+ | Brand impersonation detection |

### Frontend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | React 18 | Component-based UI library |
| Build Tool | Vite 8 | Fast build tool & dev server |
| Routing | React Router v6 | Client-side routing |
| HTTP Client | Axios | API requests with interceptors |
| Styling | Tailwind CSS | Utility-first CSS framework |
| State Management | React Context API | Global auth state |

### DevOps & Tools
- **Environment**: Python 3.x with venv
- **Package Manager**: pip
- **Git**: Version control
- **Configuration**: .env files for secrets
- **Architecture Visualization**: Matplotlib

---

## Core Components

### 1. Machine Learning Engine (`src/`)

#### 1.1 Predictor (`src/predictor.py`)
The main prediction orchestrator that:
- Loads trained XGBoost model and feature list on import
- Extracts 49 features from URL
- Runs parallel heuristic checks (ThreadPoolExecutor with 9 workers)
- Computes SHAP explanations
- Fuses ML probability + heuristic signals
- Returns comprehensive `PredictionResult` dataclass

**Key Function**:
```python
def predict(url: str) -> PredictionResult
```

**PredictionResult includes**:
- `risk_score`: 0-100 final score
- `phishing_prob`, `legitimate_prob`: Raw ML outputs
- `risk_level`: Low/Medium/High/Critical
- `verdict`: Human-readable recommendation
- `features`: All 49 extracted features
- `score_breakdown`: Per-signal contribution
- `heuristic_flags`: Raw heuristic outputs
- `shap_explanation`: Feature attribution
- `elapsed_sec`: Processing time

#### 1.2 Feature Extraction

##### URL Features (`src/features/url_features.py`) - 21 features
Static features computed without network access:
- **Length metrics**: `URLLength`, `DomainLength`, `TLDLength`
- **Domain analysis**: `IsDomainIP`, `TLDLegitimateProb`, `NoOfSubDomain`
- **Character statistics**: `NoOfLettersInURL`, `LetterRatioInURL`, `NoOfDegitsInURL`, `DegitRatioInURL`
- **Special characters**: `NoOfEqualsInURL`, `NoOfQMarkInURL`, `NoOfAmpersandInURL`, `NoOfOtherSpecialCharsInURL`
- **Obfuscation**: `HasObfuscation`, `NoOfObfuscatedChar`, `ObfuscationRatio`
- **Security**: `IsHTTPS`
- **Statistical**: `URLCharProb`, `CharContinuationRate`

##### Content Features (`src/features/content_features.py`) - 28 features
Requires fetching and parsing the webpage:
- **HTML structure**: `LineOfCode`, `LargestLineLength`, `HasTitle`, `HasFavicon`
- **Text matching**: `DomainTitleMatchScore`, `URLTitleMatchScore`
- **Metadata**: `HasDescription`, `Robots`, `IsResponsive`
- **Redirects**: `NoOfURLRedirect`, `NoOfSelfRedirect`
- **User interaction**: `HasSubmitButton`, `HasPasswordField`, `HasHiddenFields`
- **Forms**: `HasExternalFormSubmit`
- **Security indicators**: `NoOfPopup`, `NoOfiFrame`
- **Branding**: `HasSocialNet`, `HasCopyrightInfo`
- **Financial keywords**: `Bank`, `Pay`, `Crypto`
- **Resources**: `NoOfImage`, `NoOfCSS`, `NoOfJS`
- **References**: `NoOfSelfRef`, `NoOfEmptyRef`, `NoOfExternalRef`

**Note**: If page fetch fails (timeout, error), content features default to safe values to prevent false positives.

#### 1.3 Heuristic Engine (`src/heuristics/`)

All checks run concurrently via `ThreadPoolExecutor` for maximum performance (~6 seconds typical).

##### Brand Impersonation (`brand.py`)
- **Method**: Levenshtein edit distance + homoglyph normalization
- **Brands**: Google, PayPal, Amazon, Microsoft, Apple, Facebook, Netflix, eBay, Twitter, Instagram, LinkedIn, Yahoo, WhatsApp, etc.
- **Homoglyphs**: Digit-to-letter mapping (1→l, 0→o, 3→e, 5→s, 4→a, 8→b)
- **Threshold**: edit_distance ≤ 2 triggers impersonation flag
- **Penalty**: +30 points

**Example**:
- `paypa1.com` → normalizes to `paypal` → matched as PayPal impersonation

##### DNS & SSL (`dns_ssl.py`)
**DNS Check**:
- Resolves domain via `socket.gethostbyname()`
- Timeout: 5 seconds
- Penalty if fails: +15 points

**SSL Check**:
- Validates SSL certificate for HTTPS URLs
- Checks expiration date, valid hostname
- Timeout: 8 seconds
- Penalty if fails: +15 points

##### WHOIS Domain Age (`whois_age.py`)
- Queries domain registration date
- Flags domains < 180 days old
- Timeout: 10 seconds
- Penalty: +20 points for new domains

##### Path Analysis (`path_analysis.py`)
**TLD Reputation**:
- Suspicious TLDs: `.tk`, `.ml`, `.ga`, `.cf`, `.gq`, `.xyz`, `.club`, `.pw`, `.cc`, etc.
- Penalty: +20 points

**IP in Subdomain**:
- Regex pattern: `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b`
- Example: `192.168.0.1.evil.com`
- Penalty: +25 points

**Phishing Keywords** (50+ keywords):
- Security: login, signin, verify, authenticate, secure, account, suspended, confirm
- Actions: update, validate, restore, billing, payment, credential
- Urgency: urgent, immediately, expire, limited, action-required
- Banking: bank, paypal, ebay, amazon, apple, microsoft
- Penalty: +15 points (scaled by keyword count)

**Punycode/IDN**:
- Detects `xn--` prefixes (internationalized domain names)
- Used for homograph attacks (e.g., `xn--google-7hd.com`)
- Penalty: +20 points

#### 1.4 Score Fusion (`src/fusion.py`)

**Trust Calibration**:
Replaces hardcoded whitelists with dynamic trust calculation:

```python
n_clean = count of clean signals (0-6):
  - SSL valid & HTTPS
  - DNS resolves
  - Domain age > 180 days
  - Clean TLD
  - No IP in domain/subdomain
  - No brand impersonation

trust_factor = 1.0 - (n_clean / 6) * 0.6  # range: 0.4 to 1.0
```

**Example**:
- `google.com`: All 6 signals clean → trust_factor = 0.4 → ML weight reduced to 40%
- `paypa1-secure.tk`: All signals bad → trust_factor = 1.0 → full ML weight

**Score Components** (raw scores, normalized to 0-100):
| Signal | Max Points | Conditions |
|--------|------------|------------|
| ML base (calibrated) | 60 | `ml_prob * 60 * trust_factor` |
| Brand impersonation | 30 | Homoglyph/typosquat detected |
| IP-based URL | 30 | Registered domain is IP address |
| IP in subdomain | 25 | IP embedded in subdomain |
| Punycode/IDN | 20 | xn-- prefix found |
| Suspicious TLD | 20 | Domain uses risky TLD |
| Domain age | 20 | Domain < 180 days old |
| Content indicators | 20 | Password field + external form |
| Keyword signals | 15 | Phishing keywords present |
| SSL failure | 15 | Invalid/expired certificate |
| DNS failure | 15 | Domain doesn't resolve |
| **RAW_MAX** | **150** | Total possible raw score |

**Final normalization**:
```python
raw_score = sum(all_components)
final_score = min(raw_score / 150 * 100, 100.0)  # 0-100
```

#### 1.5 SHAP Explainability (`src/explainer.py`)
- Uses `shap.TreeExplainer` for XGBoost model
- Computes log-odds contributions for each feature
- Generates:
  - **Waterfall plot**: Visual breakdown of prediction
  - **Heatmap plot**: Feature values visualization
  - **Top risk features**: Features pushing toward phishing
  - **Top safe features**: Features pushing toward legitimate
- Saved as PNG images in `outputs/shap/`

#### 1.6 PDF Report Generator (`src/report.py`)
Uses ReportLab's Platypus framework to generate structured reports with 7 sections:

1. **Header**: Report ID, URL, timestamp
2. **Risk Summary**:
   - Circular score gauge with color coding
   - Risk level badge
   - ML probabilities
   - Trust factor explanation
3. **Score Breakdown**: Contribution table for all 11 signals
4. **Heuristic Findings**: Details for all checks (DNS, SSL, WHOIS, brand, etc.)
5. **SHAP Attribution**:
   - Bar charts for top risk/safe features
   - Embedded waterfall plot image
6. **Recommendations**: Context-aware security advice based on detected flags
7. **Technical Appendix**: All 49 ML feature values in table format

**Output**: `outputs/reports/{url}_{timestamp}.pdf`

---

### 2. Model Training (`train.py`)

**Pipeline**:
1. Load PhiUSIIL dataset (235,795 rows)
2. Drop leaky/non-predictive features:
   - `FILENAME`, `URL`, `Domain`, `TLD`, `Title` (identifiers)
   - `URLSimilarityIndex` (all legitimate = 100.0, std=0)
3. Split 80/20 stratified train/test
4. Train XGBoost with hyperparameters:
   - `n_estimators=300`
   - `max_depth=7`
   - `learning_rate=0.1`
   - `subsample=0.8`
   - `colsample_bytree=0.8`
   - `min_child_weight=3`
   - Regularization: `gamma=0.1`, `reg_alpha=0.05`, `reg_lambda=1.0`
5. Evaluate on test set + 5-fold CV
6. Generate plots:
   - Confusion matrix
   - Feature importances (top 20)
   - Score distribution histogram
7. Save:
   - `models/phishguard_model.pkl`
   - `models/feature_list.pkl`
   - `models/eval_report.txt`
   - `models/plots/`

**Performance**:
```
Accuracy  : 1.0000 (100.00%)
Precision : 1.0000
Recall    : 1.0000
F1 Score  : 1.0000
AUC-ROC   : 1.0000
CV F1     : 0.9999 ± 0.0000
```

---

### 3. Backend Architecture (`backend/`)

#### 3.1 Configuration (`config.py`)
Uses Pydantic Settings for environment-based configuration:
```python
class Settings(BaseSettings):
    MONGODB_URL: str
    DATABASE_NAME: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REDIS_URL: str
    ALLOWED_ORIGINS: str  # CSV list
```

Loads from `.env` file, supports environment variables.

#### 3.2 Database (`database.py`)
- **Driver**: Motor (async MongoDB driver for asyncio)
- **Connection**: Lazy initialization on startup
- **Collections**:
  - `users`: User accounts
  - `scans`: Scan history and results
- **Indexes**: Created on startup for query optimization
  - `users.email` (unique)
  - `scans.user_id`
  - `scans.timestamp`
  - `scans.score`

#### 3.3 Redis Client (`redis_client.py`)
- **Driver**: aioredis (async Redis client)
- **Use cases**:
  - URL result caching (TTL: 1 hour)
  - JWT token blacklist (TTL: token expiration)
  - Rate limiting counters (TTL: 60 seconds)
- **Graceful degradation**: If Redis is unavailable, system continues without caching

#### 3.4 Models (`backend/models/`)

**User Model** (`user.py`):
```python
{
  "_id": ObjectId,
  "name": str,
  "email": str (unique),
  "password_hash": str (bcrypt),
  "created_at": datetime,
  "scan_count": int
}
```

**Scan Model** (`scan.py`):
```python
{
  "_id": ObjectId,
  "user_id": str,
  "url": str,
  "timestamp": datetime,
  "score": float (0-100),
  "risk_level": str (Low/Medium/High/Critical),
  "verdict": str,
  "ml_probability": float (0-1),
  "trust_factor": float (0.4-1.0),
  "elapsed_time": float (seconds),
  "score_breakdown": {
    "ml_base": float,
    "brand_impersonation": float,
    "ip_based_url": float,
    # ... all signal contributions
  },
  "heuristic_flags": {
    "dns_resolves": bool,
    "ssl_valid": bool,
    "domain_age_days": int,
    # ... all heuristic outputs
  },
  "features": {
    "URLLength": int,
    "IsHTTPS": int,
    # ... all 49 features
  },
  "shap_values": {
    "base_value": float,
    "prediction_value": float,
    "top_risk": [{feature, value}],
    "top_safe": [{feature, value}]
  }
}
```

#### 3.5 Middleware

**Authentication Guard** (`middleware/auth_guard.py`):
- Validates JWT tokens from `Authorization: Bearer <token>` header
- Decodes payload and verifies signature
- Checks Redis blacklist for logged-out tokens
- Injects `current_user` into route dependencies
- Returns 401 if token invalid/expired

**Rate Limiter** (`middleware/rate_limiter.py`):
- Key: `ratelimit:scan:{user_id}`
- Limit: 10 scans per minute per user
- Uses Redis INCR + EXPIRE
- Returns 429 Too Many Requests if exceeded

#### 3.6 Routes

**Auth Routes** (`routes/auth.py`) - `/auth/*`:
- `POST /register`: Create account (bcrypt password hashing)
- `POST /login`: Issue access + refresh JWT tokens
- `POST /refresh`: Refresh access token
- `POST /logout`: Blacklist token in Redis
- `GET /me`: Get current user profile
- `PUT /change-password`: Update password
- `DELETE /delete-account`: Delete user + all scans

**Scan Routes** (`routes/scans.py`) - `/api/*`:
- `POST /scan`:
  - Accepts `{url: string}`
  - Returns SSE stream with progress events
  - Events: `cached`, `progress` (step updates), `done` (final result)
  - Checks rate limit → cache → ML pipeline → MongoDB → Redis → SSE stream

- `GET /scans`:
  - Paginated scan history
  - Query params: `page`, `limit`, `risk_level`, `sort_by`, `order`, `search`
  - Returns: `{items, total, page, pages}`

- `GET /scans/stats`:
  - Aggregation pipeline for user statistics
  - Returns: `{total, phishing_caught, safe, avg_score}`

- `GET /scans/{id}`: Fetch single scan details

- `DELETE /scans/{id}`: Delete scan from history

- `GET /scans/{id}/report`:
  - Generates PDF report on-demand
  - Streams PDF as downloadable file
  - Cleans up temp file after streaming

- `POST /scans/{id}/rescan`:
  - Re-run analysis for existing scan
  - Updates MongoDB record
  - Invalidates cache

- `POST /scan/bulk`:
  - Accepts `{urls: [string]}`
  - Max 10 URLs per request
  - Runs all predictions concurrently via `asyncio.gather()`
  - Returns: `[{id, url, score, risk_level, verdict} | {url, error}]`

**Public Routes** (`routes/public.py`) - `/public/*`:
- `POST /public/scan`: Anonymous scanning without authentication
- No rate limiting (relies on IP-based throttling at reverse proxy level)
- Results not saved to MongoDB
- Still uses Redis caching

#### 3.7 Services

**Auth Service** (`services/auth_service.py`):
- `hash_password(password)`: Bcrypt hashing
- `verify_password(plain, hashed)`: Bcrypt verification
- `create_access_token(data, expires_delta)`: JWT encoding
- `create_refresh_token(user_id)`: Longer-lived refresh token
- `decode_token(token)`: JWT decoding with expiration check

**Scan Service** (`services/scan_service.py`):
- `get_cached_scan(url)`: Redis cache lookup with SHA256 key
- `cache_scan(url, data)`: Store result in Redis with TTL
- `result_to_document(result, user_id)`: Convert PredictionResult → MongoDB doc
- `document_to_response(doc)`: Convert MongoDB doc → API response

**Report Service** (`services/report_service.py`):
- `generate_report_to_tempfile(doc)`:
  - Takes MongoDB scan document
  - Recreates PredictionResult structure
  - Generates PDF using src/report.py
  - Saves to temp directory
  - Returns temp file path for streaming

#### 3.8 FastAPI Application (`main.py`)

**Startup Lifespan**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_indexes()  # MongoDB indexes
    redis_ok = await redis_ping()  # Health check
    print(f"MongoDB connected. Redis {'connected' if redis_ok else 'unavailable'}")
    yield
    # Shutdown cleanup (none required)
```

**CORS Configuration**:
- Allowed origins from environment variable (e.g., `http://localhost:5173`)
- Credentials: True
- Methods: All
- Headers: All

**Health Check**:
- `GET /health`: Returns MongoDB/Redis connection status

---

### 4. Frontend Architecture (`frontend/`)

#### 4.1 Build Configuration

**Vite Config** (`vite.config.js`):
```javascript
{
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/auth': 'http://localhost:8000',
      '/public': 'http://localhost:8000'
    }
  }
}
```
Proxy forwards API requests to backend during development.

**package.json**:
- `axios`: HTTP client with request/response interceptors
- `react-router-dom`: Client-side routing
- `tailwindcss`: Utility-first CSS
- ESLint + PostCSS for code quality

#### 4.2 Authentication Context (`context/AuthContext.jsx`)

Global state management for authentication:
```javascript
AuthContext provides:
  - user: Current user object or null
  - loading: Boolean loading state
  - login(email, password): Returns {access, refresh} tokens
  - logout(): Blacklists token, clears storage
  - refreshToken(): Silent token refresh
```

**Axios Interceptors**:
- Request: Attach `Authorization: Bearer ${accessToken}` header
- Response: On 401, attempt token refresh → retry original request
- If refresh fails, logout and redirect to login

**Token Storage**: LocalStorage for access/refresh tokens

#### 4.3 Routing (`App.jsx`)

```
/                 → Dashboard (protected)
/login            → Login page (redirects if authenticated)
/register         → Register page
/history          → Scan history with filters (protected)
/scan/:id         → Detailed scan result (protected)
/bulk             → Bulk scan interface (protected)
/profile          → User profile management (protected)
```

**Protected Route HOC**:
```javascript
<Protected>
  {loading ? <Spinner /> : user ? children : <Navigate to="/login" />}
</Protected>
```

#### 4.4 Pages

**Dashboard** (`pages/Dashboard.jsx`):
- URL input form with validation
- Real-time scan progress via EventSource (SSE)
- Displays latest scan results with `ResultCard`
- Shows recent scan statistics

**History** (`pages/History.jsx`):
- Paginated table of past scans
- Filters: Risk level dropdown
- Search: URL text search
- Sort: By timestamp or score, asc/desc
- Actions: View details, Delete
- Responsive grid layout

**Scan Detail** (`pages/ScanDetail.jsx`):
- Full result breakdown:
  - Score gauge with color coding
  - Risk badge and verdict
  - ML probability meters
  - Trust factor explanation
- Score breakdown table (all 11 signals)
- Heuristic findings cards:
  - DNS status
  - SSL/HTTPS status
  - Brand impersonation (if detected)
  - Domain age
  - TLD reputation
  - Path flags
  - IP in subdomain
  - Keywords found
  - Punycode detection
- SHAP attribution:
  - Top risk features with bar charts
  - Top safe features with bar charts
  - Base value vs final prediction value
- Actions:
  - Download PDF report
  - Rescan URL
  - Delete scan

**Bulk Scan** (`pages/BulkScan.jsx`):
- Textarea input for multiple URLs (one per line)
- Max 10 URLs per batch
- Progress bar with counter
- Results table with individual scores
- Export results as CSV

**Profile** (`pages/Profile.jsx`):
- Display user info (name, email, join date)
- Show scan count
- Change password form
- Delete account with confirmation modal

#### 4.5 Components

**ScoreGauge** (`components/ScoreGauge.jsx`):
- SVG circular gauge (0-100 range)
- Color zones:
  - 0-25: Green (#22c55e)
  - 25-50: Yellow (#eab308)
  - 50-75: Orange (#f97316)
  - 75-100: Red (#ef4444)
- Animated arc drawing
- Center text shows score value

**RiskBadge** (`components/RiskBadge.jsx`):
- Pill-shaped badge with risk level
- Color mapping:
  - Low: Green
  - Medium: Yellow
  - High: Orange
  - Critical: Red
- Variant: `sm`, `md`, `lg`

**ScanProgress** (`components/ScanProgress.jsx`):
- Progress bar with animated stripes
- Current step indicator
- Step labels:
  1. DNS resolution
  2. SSL validation
  3. Brand impersonation
  4. WHOIS lookup
  5. Keyword scanning
  6. ML inference + SHAP

**ResultCard** (`components/ResultCard.jsx`):
- Card layout for scan result
- Sections:
  - Header: URL with favicon, timestamp
  - Score gauge + risk badge
  - Quick stats: ML prob, trust factor, elapsed time
  - Action buttons: View details, Download PDF, Rescan

**Navbar** (`components/Navbar.jsx`):
- Logo + brand name
- Navigation links: Dashboard, History, Bulk Scan, Profile
- User dropdown: Logout
- Responsive hamburger menu for mobile

#### 4.6 API Client (`api/client.js`)

Axios instance with:
- Base URL: `/` (uses Vite proxy)
- Content-Type: application/json
- Request interceptor: Attach JWT token
- Response interceptor: Handle 401 with token refresh

---

## Data Flow

### Complete Scan Request Flow (End-to-End)

```
1.  User submits URL via Dashboard input field
    ↓
2.  React: POST /api/scan with {url: "..."} + JWT token in Authorization header
    ↓
3.  FastAPI: JWT middleware validates token → extracts user_id
    ↓
4.  Rate Limiter: Check Redis counter for user_id
    - Key: ratelimit:scan:{user_id}
    - INCR + EXPIRE (60s)
    - If count > 10: return 429 Too Many Requests
    ↓
5.  Scan Service: Check Redis cache for URL
    - Key: scan:cache:{sha256(url)}
    - Hit? → return cached result, still save to MongoDB history
    ↓
6.  Cache Miss: Run predict(url) in thread executor
    ↓
7.  Feature Extraction:
    - extract_url_features(url) → 21 static features
    - extract_content_features(url) → 28 content features (HTTP GET)
    ↓
8.  XGBoost Model: predict_proba(features) → [P(phish), P(legit)]
    ↓
9.  SHAP Explainer: TreeExplainer.shap_values(features) → log-odds contributions
    ↓
10. Heuristic Engine: ThreadPoolExecutor runs 9 checks concurrently:
    - check_brand_impersonation(url)
    - check_dns(url)
    - check_ssl(url)
    - check_domain_age(url)
    - check_path(url)
    - check_tld(url)
    - check_ip_subdomain(url)
    - check_keywords(url)
    - check_punycode(url)
    ↓
11. Trust Calibration:
    - Count clean signals: ssl_ok, dns_ok, old_domain, clean_tld, no_ip, no_brand
    - trust_factor = 1.0 - (n_clean / 6) * 0.6
    ↓
12. Score Fusion:
    - ml_base = P(phish) * 60 * trust_factor
    - raw_score = ml_base + brand_penalty + ip_penalty + tld_penalty + ... (11 signals)
    - final_score = min(raw_score / 150 * 100, 100.0)
    ↓
13. PredictionResult assembled with:
    - risk_score, risk_level, verdict
    - phishing_prob, legitimate_prob
    - features (all 49)
    - score_breakdown (per-signal)
    - heuristic_flags (raw outputs)
    - shap_explanation (top risk/safe features)
    - elapsed_sec
    ↓
14. Scan Service: Convert PredictionResult → MongoDB document
    ↓
15. MongoDB: Insert into scans collection
    ↓
16. MongoDB: Update users.scan_count += 1
    ↓
17. Redis: Cache result with TTL=3600s
    ↓
18. SSE Stream: Emit events to frontend
    - event: progress, data: {step: "dns", message: "Checking DNS..."}
    - event: progress, data: {step: "ssl", message: "Validating SSL..."}
    - ...
    - event: done, data: {id, url, score, risk_level, verdict, ...}
    ↓
19. React: EventSource receives "done" event
    ↓
20. React: Render ResultCard with:
    - ScoreGauge showing final_score
    - RiskBadge with risk_level
    - Score breakdown table
    - Heuristic findings cards
    - SHAP attribution charts
    ↓
21. User clicks "Download PDF"
    ↓
22. React: GET /api/scans/{id}/report
    ↓
23. FastAPI: Retrieve scan document from MongoDB
    ↓
24. Report Service: Generate PDF using ReportLab
    - Rebuild PredictionResult from document
    - src/report.py generates PDF with 7 sections
    - Save to temp directory
    ↓
25. FastAPI: Stream PDF file with Content-Disposition: attachment
    ↓
26. React: Browser triggers download
    ↓
27. FastAPI: Delete temp file after streaming completes
```

---

## Security Features

### 1. Authentication & Authorization
- **JWT Tokens**:
  - Access token: 60 minutes expiry
  - Refresh token: 30 days expiry
  - Signed with HS256 algorithm
- **Password Security**:
  - Bcrypt hashing with automatic salt
  - Cost factor: 12 rounds (default)
- **Token Blacklist**: Redis-based revocation on logout
- **Auto-refresh**: Frontend automatically renews expired tokens

### 2. Rate Limiting
- **Scan endpoint**: 10 requests/minute/user
- **Bulk scan**: 1 request/minute/user (implicit via scan limit)
- **Redis-backed counters** with sliding window
- **429 status code** with retry-after header

### 3. Input Validation
- **Pydantic models**: Automatic request validation
- **URL sanitization**: Strip whitespace, validate format
- **SQL injection**: N/A (NoSQL database)
- **XSS prevention**: React escapes by default, no dangerouslySetInnerHTML

### 4. Network Security
- **CORS**: Restricted to allowed origins only
- **HTTPS**: Enforced in production (Nginx/reverse proxy)
- **JWT signing**: Cryptographic signature verification
- **Secure headers**:
  - Content-Security-Policy
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff

### 5. Data Privacy
- **Password hashing**: Never store plaintext passwords
- **User isolation**: Users can only access their own scans
- **Token encryption**: JWT payload base64-encoded
- **Cache keys**: SHA256 hashed URLs for privacy

### 6. Error Handling
- **Graceful degradation**: Redis failures don't crash system
- **Timeout protection**: Network checks have max timeout (5-10s)
- **Exception isolation**: Heuristic check failures don't block pipeline
- **Generic error messages**: Don't leak internal details to users

---

## Deployment & Configuration

### Environment Variables (`.env`)

```bash
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=phishguard

# JWT
JWT_SECRET_KEY=<randomly-generated-secret-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Redis
REDIS_URL=redis://localhost:6379

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/<username>/PhishGuard.git
cd PhishGuard

# 2. Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Environment configuration
cp .env.example .env
# Edit .env with your configuration

# 4. Start MongoDB
# Docker: docker run -d -p 27017:27017 mongo:latest
# Or use MongoDB Atlas cloud service

# 5. Start Redis
# Docker: docker run -d -p 6379:6379 redis:latest
# Or use Redis Cloud

# 6. Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 7. Frontend setup (new terminal)
cd frontend
npm install
npm run dev  # Starts on http://localhost:5173

# 8. Access application
# Open browser: http://localhost:5173
```

### Production Deployment

**Backend**:
```bash
# Use production ASGI server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or with Gunicorn
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend**:
```bash
npm run build  # Creates dist/ folder
# Serve with Nginx, Apache, or CDN
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name phishguard.example.com;

    # Frontend
    location / {
        root /var/www/phishguard/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /auth {
        proxy_pass http://localhost:8000;
    }

    location /public {
        proxy_pass http://localhost:8000;
    }
}
```

---

## Testing & Validation

### Command-Line Testing

```bash
# Single URL analysis
python -X utf8 test_predict.py "https://example.com"

# Interactive mode
python -X utf8 test_predict.py

# Batch test (10 preset URLs)
python -X utf8 test_predict.py --batch
```

### Expected Test Results

| URL | Expected | Actual Score | Risk Level |
|-----|----------|-------------|-----------|
| https://www.google.com | Legitimate | 15.9 | Low |
| https://www.github.com | Legitimate | 2.9 | Low |
| https://www.wikipedia.org | Legitimate | 15.9 | Low |
| http://paypa1-secure-login.tk/verify | Phishing | 82.0 | Critical |
| http://192.168.1.1/admin/login | Phishing | 87.0 | Critical |
| http://g00gle-verify.xyz/update | Phishing | 75.0 | Critical |
| http://192.168.0.1.secure-login-update.com | Phishing | 85.3 | Critical |
| http://xn--google-7hd.com | Phishing | 68.0 | High |

---

## Performance Characteristics

### Timing Breakdown (typical)
- **Feature extraction**: ~1-2 seconds (includes HTTP GET)
- **ML inference**: <0.1 seconds
- **SHAP computation**: ~0.5 seconds
- **Heuristic checks** (parallel): ~3-5 seconds
  - DNS: 0.5-1s
  - SSL: 1-2s
  - WHOIS: 2-5s
  - Others: <0.5s each
- **Score fusion**: <0.01 seconds
- **Total**: ~5-7 seconds per scan

### Optimization Strategies
1. **Concurrent heuristics**: ThreadPoolExecutor with 9 workers
2. **Redis caching**: 1-hour TTL reduces repeated scans to <100ms
3. **Async I/O**: FastAPI + Motor + aioredis for non-blocking operations
4. **Bulk scanning**: Parallel execution via asyncio.gather()
5. **SSE streaming**: Real-time progress updates improve perceived performance

---

## Future Enhancements (Phases 7-8)

### Phase 7: Advanced Features
- [ ] Real-time URL monitoring service
- [ ] Browser extension for instant URL checking
- [ ] Email phishing detection (parse URLs from email body)
- [ ] Scheduled rescans for flagged domains
- [ ] Machine learning model retraining pipeline
- [ ] A/B testing for heuristic weight tuning

### Phase 8: Enterprise Features
- [ ] Multi-tenancy support
- [ ] Team collaboration (shared scan history)
- [ ] API key management for external integrations
- [ ] Webhook notifications for high-risk detections
- [ ] Custom brand impersonation lists
- [ ] Export audit logs for compliance
- [ ] SSO integration (SAML, OAuth2)

---

## Key Innovations

1. **Trust Calibration**: Dynamic ML weight adjustment replaces static whitelists
2. **Homoglyph Detection**: Digit-to-letter normalization catches advanced typosquatting
3. **Concurrent Heuristics**: 9 network checks in parallel for fast response
4. **SHAP Integration**: Transparent ML explanations for every prediction
5. **SSE Streaming**: Real-time progress updates for better UX
6. **Deterministic PDF**: Full reproducible reports without external AI APIs
7. **Graceful Degradation**: Redis failures don't break core functionality

---

## Conclusion

PhishGuard is a production-ready, full-stack phishing detection system combining:
- **State-of-the-art ML** (XGBoost with perfect test metrics)
- **Robust heuristics** (9 concurrent security checks)
- **Explainable AI** (SHAP feature attribution)
- **Modern web stack** (FastAPI + React + MongoDB + Redis)
- **Enterprise features** (JWT auth, rate limiting, caching, PDF reports)

The system achieves high accuracy while remaining transparent, fast, and user-friendly. All components are modular, well-documented, and designed for scalability.
