# PhishGuard - 4-Member Team Division & Responsibilities

---

# PROJECT DIVISION OVERVIEW

```
┌────────────────────────────────────────────────────────────┐
│            PHISHGUARD PROJECT (4 Members)                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ MEMBER 1          MEMBER 2          MEMBER 3  MEMBER 4    │
│ Frontend          Backend &         ML & Model Documentation
│ (React+Vite)      Architecture      Pipeline  Data Prep
│                   (FastAPI)         (XGBoost) (Lighter)
│                                                            │
│ 30%               35%               30%       5%          │
│ Contribution      Contribution      Contribution Contribution
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

# MEMBER 1: FRONTEND DEVELOPMENT (React + Vite)

## Responsibility: 30% | Files: frontend/

### Overview
Build the entire user-facing web application with React, Tailwind CSS, and modern UX patterns.

### Deliverables

#### 1. **Authentication System** (Pages + Context)
```
frontend/
├── context/
│   └── AuthContext.jsx          # JWT token management, login/logout
├── pages/
│   ├── Login.jsx                # Email + password form
│   ├── Register.jsx             # Sign-up form
│   └── Profile.jsx              # User settings, change password, delete account
└── components/
    └── ProtectedRoute.jsx       # Higher-order component for auth check
```

**Responsibilities:**
- ✅ JWT token storage (localStorage)
- ✅ Login/logout flows
- ✅ Password validation
- ✅ User profile management
- ✅ Protected routes (redirect to login if not authenticated)

**Key Functions:**
```javascript
// AuthContext provides:
const { user, loading, login, logout, refreshToken } = useAuth()

// Axios interceptor: attach JWT to requests
// Auto-refresh on 401 response
```

#### 2. **Dashboard Page** (Main URL Input)
```
frontend/pages/Dashboard.jsx
```

**Features:**
- URL input field with validation
- Real-time scan progress (SSE events)
- Latest scan result display
- Recent scans statistics
- Animated progress bar

**UI Components Needed:**
- `<URLInput />` - validates URL format
- `<ScanProgress />` - progress bar with step labels
- `<ResultCard />` - displays latest scan result
- `<ScoreGauge />` - circular gauge (0-100)
- `<RiskBadge />` - colored badge (Low/Medium/High/Critical)

**Example Flow:**
```
User types URL → Clicks "Scan"
↓
POST /api/scan with JWT token
↓
EventSource opens (SSE stream)
↓
Receive events:
  - "progress": {step: "dns", message: "Checking DNS..."}
  - "progress": {step: "ssl", message: "Validating SSL..."}
  - "progress": {step: "brand", message: "Brand check..."}
  - "done": {score: 82, risk_level: "Critical", ...}
↓
Display result with ScoreGauge, breakdown table, heuristics
```

#### 3. **History Page** (Scan History with Filters)
```
frontend/pages/History.jsx
```

**Features:**
- Paginated table of past scans
- Filters: Risk level dropdown (Low/Medium/High/Critical)
- Search: URL text search
- Sort: by timestamp (asc/desc) or score (asc/desc)
- Actions: View details, Delete scan

**API Calls:**
```
GET /api/scans?page=1&limit=10&risk_level=High&sort_by=timestamp&order=desc&search=google
→ Returns: {items: [{id, url, score, risk_level, timestamp}], total, pages}
```

**UI:**
- Responsive table/grid layout
- Filter sidebar (desktop) or dropdown (mobile)
- Pagination controls
- Loading states

#### 4. **Scan Detail Page** (Full Analysis View)
```
frontend/pages/ScanDetail.jsx
```

**Sections:**
1. **Risk Summary** - Score gauge, verdict, ML probabilities
2. **Score Breakdown** - Table of all 11 signals + contributions
3. **Heuristic Findings** - Cards for each check result
4. **SHAP Attribution** - Top risk/safe features + charts
5. **Actions** - Download PDF, Rescan, Delete

**API Calls:**
```
GET /api/scans/{id}
→ Returns full scan document with all details

GET /api/scans/{id}/report
→ Download PDF file

POST /api/scans/{id}/rescan
→ Re-run analysis, update MongoDB

DELETE /api/scans/{id}
→ Remove scan from history
```

**Collapsible Heuristics Cards:**
```
├─ DNS Status: ✅ Resolves to 192.168.1.1
├─ SSL/HTTPS: ✅ Valid certificate
├─ Brand Check: ❌ Possible PayPal impersonation
├─ Domain Age: ✅ 15 years old
├─ TLD Reputation: ❌ Suspicious (.tk)
├─ IP Analysis: ✅ No IP in domain
├─ Keywords: ⚠️ Found: ["login", "verify", "secure"]
└─ Punycode: ✅ No punycode detected
```

#### 5. **Bulk Scan Page** (Batch Analysis)
```
frontend/pages/BulkScan.jsx
```

**Features:**
- Textarea for multiple URLs (one per line)
- Max 10 URLs per batch
- Progress counter
- Results table with individual scores
- Export results as CSV

**Example:**
```
Input:
google.com
github.com
paypa1-secure-login.tk

After scan:
| URL | Score | Risk Level | Status |
|-----|-------|-----------|--------|
| google.com | 15.9 | Low | ✅ |
| github.com | 2.9 | Low | ✅ |
| paypa1... | 82.0 | Critical | 🚨 |

Export CSV button
```

#### 6. **Reusable Components**

```
frontend/components/
├── ScoreGauge.jsx
│   └── SVG circular gauge (0-100, color zones)
│
├── RiskBadge.jsx
│   └── Colored pill badge (Low/Medium/High/Critical)
│
├── ScanProgress.jsx
│   └── Progress bar with animated stripes
│
├── ResultCard.jsx
│   └── Card layout for scan result (quick view)
│
├── Navbar.jsx
│   └── Logo, nav links, user dropdown
│
├── LoadingSpinner.jsx
│   └── Loading animation
│
└── Modal.jsx
    └── Confirmation dialogs (delete, confirm)
```

**ScoreGauge Example:**
```javascript
<ScoreGauge score={82} max={100}>
  → SVG arc from 0° to 360° based on score
  → Color zones:
    • 0-25: Green (#22c55e)
    • 25-50: Yellow (#eab308)
    • 50-75: Orange (#f97316)
    • 75-100: Red (#ef4444)
```

#### 7. **API Client & State Management**

```
frontend/
├── api/
│   └── client.js
│       └── Axios instance with:
│           • Base URL configuration
│           • Request interceptor: add JWT token
│           • Response interceptor: handle 401 (refresh token)
│
└── context/
    └── AuthContext.jsx
        └── Global auth state (user, tokens, loading)
```

### Tech Stack
- **React 18** - Component framework
- **Vite 8** - Build tool + dev server
- **React Router v6** - Client-side routing
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Styling
- **React Context API** - State management

### File Structure
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── History.jsx
│   │   ├── ScanDetail.jsx
│   │   ├── BulkScan.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── Profile.jsx
│   ├── components/
│   │   ├── ScoreGauge.jsx
│   │   ├── RiskBadge.jsx
│   │   ├── ScanProgress.jsx
│   │   ├── ResultCard.jsx
│   │   ├── Navbar.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── Modal.jsx
│   │   └── ProtectedRoute.jsx
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── api/
│   │   └── client.js
│   ├── App.jsx
│   ├── index.css
│   └── main.jsx
├── vite.config.js
├── tailwind.config.js
├── package.json
└── README.md
```

### Dependencies
```json
{
  "react": "^18.0.0",
  "react-dom": "^18.0.0",
  "react-router-dom": "^6.0.0",
  "axios": "^1.4.0",
  "tailwindcss": "^3.0.0"
}
```

### Key Metrics
- **Contribution**: 30%
- **Estimated Hours**: 60-80 hours
- **Lines of Code**: ~2,000-3,000
- **Complexity**: Medium (UI/UX, state management)

### Integration Points
- **With Member 2 (Backend)**: API endpoints (/auth/*, /api/scan*, /api/scans*)
- **With Member 3 (ML)**: Display SHAP results, score breakdown

---

# MEMBER 2: BACKEND & OVERALL ARCHITECTURE (FastAPI + MongoDB + Redis)

## Responsibility: 35% | Files: backend/, main.py, config files

### Overview
Build the entire backend API, database schema, caching layer, authentication, and business logic.

### Deliverables

#### 1. **Core FastAPI Application**
```
backend/
├── main.py                  # FastAPI app setup, lifespan, routes mounting
├── config.py               # Settings from environment variables
├── database.py             # MongoDB connection
├── redis_client.py         # Redis async client
└── requirements.txt        # Dependencies
```

**main.py:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()      # Create MongoDB indexes
    await redis_health()  # Check Redis connection
    print("✅ Backend ready")
    yield
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(CORSMiddleware, ...)

# Mount routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(scan_router, prefix="/api", tags=["scans"])
app.include_router(public_router, prefix="/public", tags=["public"])

# Health check
@app.get("/health")
async def health():
    return {"mongodb": "ok", "redis": redis_ok}
```

#### 2. **Authentication System**

```
backend/
├── models/
│   └── user.py              # User schema
├── services/
│   └── auth_service.py      # JWT, password hashing
└── routes/
    └── auth.py              # Auth endpoints
```

**User Model (MongoDB):**
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

**Auth Routes:**
```python
POST /auth/register
  Body: {email, password, name}
  Response: {user_id, message}

POST /auth/login
  Body: {email, password}
  Response: {access_token, refresh_token, user: {name, email}}

POST /auth/refresh
  Headers: Authorization: Bearer {refresh_token}
  Response: {access_token}

POST /auth/logout
  Headers: Authorization: Bearer {access_token}
  Response: {message}  # Blacklist token in Redis

GET /auth/me
  Headers: Authorization: Bearer {access_token}
  Response: {user}

PUT /auth/change-password
  Headers: Authorization: Bearer {access_token}
  Body: {old_password, new_password}
  Response: {message}

DELETE /auth/delete-account
  Headers: Authorization: Bearer {access_token}
  Response: {message}  # Delete user + all scans
```

**Auth Service:**
```python
def hash_password(password: str) -> str:
    # bcrypt with cost=12
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(user_id: str, expires_delta: timedelta = 60 min) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + expires_delta,
        "type": "access"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### 3. **Middleware**

```
backend/middleware/
├── auth_guard.py            # JWT validation
└── rate_limiter.py          # Rate limiting
```

**Auth Guard:**
```python
async def get_current_user(request: Request) -> str:
    """Dependency: extract user_id from JWT."""
    
    # Get token from header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token")
    
    token = auth_header.split(" ")[1]
    
    # Check blacklist
    if await redis.get(f"blacklist:{token}"):
        raise HTTPException(status_code=401, detail="Token revoked")
    
    # Decode token
    payload = decode_token(token)
    user_id = payload.get("sub")
    
    return user_id
```

**Rate Limiter:**
```python
async def rate_limit_check(request: Request, user_id: str, limit=10, window=60):
    """Limit to 10 requests per minute per user."""
    
    key = f"ratelimit:scan:{user_id}"
    count = await redis.incr(key)
    
    if count == 1:
        await redis.expire(key, window)  # Set TTL
    
    if count > limit:
        raise HTTPException(status_code=429, detail="Too many requests")
```

#### 4. **Scan Routes (Core Logic)**

```
backend/routes/scans.py
```

**Main Endpoints:**

```python
POST /api/scan
  Headers: Authorization: Bearer {token}
  Body: {url: string}
  Response: Server-Sent Events (SSE) stream
  
  Flow:
    1. Validate JWT (auth_guard)
    2. Check rate limit (10/min)
    3. Check Redis cache (SHA256(url))
      → If HIT: return cached result
      → If MISS: run ML pipeline
    4. Call predict(url) in thread executor (don't block async)
    5. Stream progress events (dns, ssl, brand, whois, keywords, ml)
    6. Save to MongoDB
    7. Cache in Redis (TTL: 1 hour)
    8. Send "done" event with full result
```

**Example SSE Stream:**
```python
@app.post("/api/scan")
async def scan_url(request: ScanRequest, current_user = Depends(get_current_user)):
    """Scan URL with SSE progress updates."""
    
    # Rate limit check
    await rate_limit_check(request, current_user)
    
    # Cache check
    cached = await get_cached_scan(request.url)
    if cached:
        yield f"event: cached\ndata: {json.dumps(cached.dict())}\n\n"
        return
    
    async def event_generator():
        # Run prediction in thread executor (don't block)
        result = await asyncio.to_thread(predict, request.url)
        
        # Yield progress events
        yield f"event: progress\ndata: {json.dumps({'step': 'dns', 'message': 'DNS check...'})}\n\n"
        # ... more progress events
        
        # Save to MongoDB
        doc = result_to_document(result, current_user)
        await scans_collection.insert_one(doc)
        
        # Cache in Redis
        await cache_scan(request.url, result, ttl=3600)
        
        # Yield final result
        yield f"event: done\ndata: {json.dumps(result.dict())}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


GET /api/scans
  Headers: Authorization: Bearer {token}
  Query: page=1, limit=10, risk_level=High, sort_by=timestamp, order=desc, search=google
  Response: {items, total, page, pages}
  
  Implementation:
    1. Build MongoDB filter (risk_level, search)
    2. Sort by field and order
    3. Paginate (skip, limit)
    4. Aggregate user_id to user stats
    

GET /api/scans/{id}
  Headers: Authorization: Bearer {token}
  Response: Full scan document
  

GET /api/scans/{id}/report
  Headers: Authorization: Bearer {token}
  Response: PDF file (streaming)
  
  Implementation:
    1. Fetch scan from MongoDB
    2. Call report_service.generate_report_to_tempfile(doc)
    3. Stream PDF with Content-Disposition: attachment
    4. Delete temp file after streaming


POST /api/scans/{id}/rescan
  Headers: Authorization: Bearer {token}
  Body: {} (no body)
  Response: Updated scan result
  
  Implementation:
    1. Fetch original scan
    2. Call predict(url) again
    3. Update document in MongoDB
    4. Invalidate cache
    5. Return new result


DELETE /api/scans/{id}
  Headers: Authorization: Bearer {token}
  Response: {message}
  
  Implementation:
    1. Delete from MongoDB
    2. Update user.scan_count -= 1


GET /api/scans/stats
  Headers: Authorization: Bearer {token}
  Response: {total, phishing_caught, safe, avg_score}
  
  Implementation:
    1. MongoDB aggregation pipeline
    2. Filter by user_id, group by risk_level
    3. Calculate statistics


POST /api/scan/bulk
  Headers: Authorization: Bearer {token}
  Body: {urls: [string...]}  # Max 10
  Response: [{id, url, score, risk_level, verdict}, ...]
  
  Implementation:
    1. Validate max 10 URLs
    2. Run all predictions concurrently: asyncio.gather(*)
    3. Save all to MongoDB
    4. Return results
```

#### 5. **Scan Model & Services**

```
backend/
├── models/
│   └── scan.py              # Scan document schema
├── services/
│   ├── scan_service.py      # Cache, persistence
│   ├── report_service.py    # PDF generation
│   └── auth_service.py      # Auth helpers
```

**Scan Model (MongoDB):**
```python
{
    "_id": ObjectId,
    "user_id": str,
    "url": str,
    "timestamp": datetime,
    
    # Results
    "score": float (0-100),
    "risk_level": str,
    "verdict": str,
    "ml_probability": float,
    "legitimate_probability": float,
    "trust_factor": float,
    "elapsed_time": float,
    
    # Breakdown
    "score_breakdown": {signal_name: points, ...},
    "heuristic_flags": {check_name: result, ...},
    "features": {feature_name: value, ...},
    
    # Explanation
    "shap_explanation": {
        "base_value": float,
        "prediction_value": float,
        "top_risk_features": [...],
        "top_safe_features": [...]
    }
}
```

**Scan Service:**
```python
async def get_cached_scan(url: str) -> Optional[dict]:
    """Lookup scan in Redis by SHA256(url)."""
    key = f"scan:cache:{hashlib.sha256(url.encode()).hexdigest()}"
    cached = await redis.get(key)
    return json.loads(cached) if cached else None

async def cache_scan(url: str, result: PredictionResult, ttl: int = 3600):
    """Store result in Redis with TTL."""
    key = f"scan:cache:{hashlib.sha256(url.encode()).hexdigest()}"
    await redis.setex(key, ttl, result.json())

def result_to_document(result: PredictionResult, user_id: str) -> dict:
    """Convert PredictionResult to MongoDB document."""
    return {
        "user_id": user_id,
        "url": result.url,
        "timestamp": datetime.utcnow(),
        "score": result.risk_score,
        "risk_level": result.risk_level,
        "verdict": result.verdict,
        "ml_probability": result.phishing_prob,
        "legitimate_probability": result.legitimate_prob,
        "trust_factor": result.trust_factor,
        "elapsed_time": result.elapsed_sec,
        "score_breakdown": result.score_breakdown,
        "heuristic_flags": result.heuristic_flags,
        "features": result.features,
        "shap_explanation": {
            "base_value": result.shap_explanation.base_value,
            "prediction_value": result.shap_explanation.prediction_value,
            "top_risk_features": result.shap_explanation.top_risk_features,
            "top_safe_features": result.shap_explanation.top_safe_features
        }
    }
```

**Report Service:**
```python
async def generate_report_to_tempfile(scan_doc: dict) -> str:
    """Generate PDF report, save to temp file."""
    
    # Rebuild PredictionResult from document
    result = document_to_prediction_result(scan_doc)
    
    # Generate PDF using src/report.py
    pdf_path = f"/tmp/report_{scan_doc['_id']}_{int(time.time())}.pdf"
    generate_pdf_report(result, output_path=pdf_path)
    
    return pdf_path
```

#### 6. **Database Setup**

```
backend/database.py
```

```python
from motor.motor_asyncio import AsyncClient, AsyncDatabase

_mongo_client: AsyncClient = None
_mongo_db: AsyncDatabase = None

async def init_db():
    """Initialize MongoDB connection and create indexes."""
    global _mongo_client, _mongo_db
    
    _mongo_client = AsyncClient(settings.MONGODB_URL)
    _mongo_db = _mongo_client[settings.DATABASE_NAME]
    
    # Create indexes
    await _mongo_db.users.create_index("email", unique=True)
    await _mongo_db.scans.create_index("user_id")
    await _mongo_db.scans.create_index("timestamp")
    await _mongo_db.scans.create_index("score")

def get_db() -> AsyncDatabase:
    return _mongo_db

# Collections
users_collection = get_db()["users"]
scans_collection = get_db()["scans"]
```

#### 7. **Redis Client Setup**

```
backend/redis_client.py
```

```python
import aioredis

_redis = None

async def init_redis():
    """Initialize Redis connection."""
    global _redis
    _redis = await aioredis.create_redis_pool(settings.REDIS_URL)

async def get_redis() -> aioredis.Redis:
    return _redis

async def redis_ping():
    """Health check for Redis."""
    try:
        await redis.ping()
        return True
    except:
        return False
```

### File Structure
```
backend/
├── main.py
├── config.py
├── database.py
├── redis_client.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── scan.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── scan_service.py
│   └── report_service.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── scans.py
│   └── public.py
├── middleware/
│   ├── __init__.py
│   ├── auth_guard.py
│   └── rate_limiter.py
└── requirements.txt
```

### Tech Stack
- **FastAPI** - Async web framework
- **Uvicorn** - ASGI server
- **Motor** - Async MongoDB driver
- **aioredis** - Async Redis client
- **python-jose** - JWT tokens
- **bcrypt** - Password hashing
- **Pydantic** - Data validation

### Key Metrics
- **Contribution**: 35%
- **Estimated Hours**: 80-100 hours
- **Lines of Code**: ~3,000-4,000
- **Complexity**: High (async, concurrency, caching, error handling)

### Integration Points
- **With Member 1 (Frontend)**: Provide API endpoints, SSE streaming
- **With Member 3 (ML)**: Call `predict()` function, handle results
- **With Member 4 (Data)**: Use preprocessed dataset

---

# MEMBER 3: ML & ML PIPELINE + HEURISTICS (XGBoost + SHAP)

## Responsibility: 30% | Files: src/, train.py, models/

### Overview
Implement the complete ML pipeline: feature extraction, model training, heuristic checks, score fusion, SHAP explanations, and PDF report generation.

### Deliverables

#### 1. **Feature Extraction (49 features)**

```
src/features/
├── __init__.py
├── url_features.py          # 21 URL-level features
└── content_features.py      # 28 content-level features
```

**URL Features (21):**
```python
def extract_url_features(url: str) -> dict:
    """Extract 21 static URL features."""
    
    parsed = urlparse(url)
    
    features = {
        'URLLength': len(url),
        'DomainLength': len(parsed.netloc),
        'TLDLength': len(get_tld(parsed.netloc)),
        'IsHTTPS': 1 if parsed.scheme == 'https' else 0,
        'IsDomainIP': 1 if is_ip_address(parsed.netloc) else 0,
        'NoOfSubDomain': parsed.netloc.count('.'),
        'HasObfuscation': 1 if '%' in url else 0,
        'NoOfObfuscatedChar': url.count('%') // 3,  # %XX triplets
        'ObfuscationRatio': (url.count('%') // 3) / len(url) if len(url) > 0 else 0,
        
        # Character distribution
        'NoOfLettersInURL': sum(1 for c in url if c.isalpha()),
        'LetterRatioInURL': sum(1 for c in url if c.isalpha()) / len(url) if url else 0,
        'NoOfDegitsInURL': sum(1 for c in url if c.isdigit()),
        'DegitRatioInURL': sum(1 for c in url if c.isdigit()) / len(url) if url else 0,
        
        # Special characters
        'NoOfEqualsInURL': url.count('='),
        'NoOfQMarkInURL': url.count('?'),
        'NoOfAmpersandInURL': url.count('&'),
        'NoOfOtherSpecialCharsInURL': sum(1 for c in url if c in '@!#$%^*()[]{}'),
        'SpacialCharRatioInURL': sum(1 for c in url if c in '@!#$%^*()[]{}') / len(url) if url else 0,
        
        # Statistical
        'CharContinuationRate': calculate_char_continuation_rate(url),
        'URLCharProb': calculate_entropy(url),
        'TLDLegitimateProb': get_tld_legitimacy_score(get_tld(url))
    }
    
    return features
```

**Content Features (28):**
```python
def extract_content_features(url: str, timeout: int = 10) -> dict:
    """Extract 28 content-level features (requires page fetch)."""
    
    features = {}
    
    try:
        # HTTP GET
        response = requests.get(url, timeout=timeout, verify=False)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # HTML structure
        features['LineOfCode'] = len(html.split('\n'))
        features['LargestLineLength'] = max(len(line) for line in html.split('\n'))
        features['HasTitle'] = 1 if soup.find('title') else 0
        features['HasFavicon'] = 1 if soup.find('link', rel='icon') else 0
        features['HasDescription'] = 1 if soup.find('meta', {'name': 'description'}) else 0
        features['Robots'] = 1 if 'robots' in html.lower() else 0
        
        # Text matching
        title_text = soup.find('title').get_text().lower() if soup.find('title') else ''
        domain_text = extract_domain(url).lower()
        url_text = url.lower()
        features['DomainTitleMatchScore'] = calculate_similarity(domain_text, title_text)
        features['URLTitleMatchScore'] = calculate_similarity(url_text, title_text)
        
        # Responsiveness
        features['IsResponsive'] = 1 if '@media' in html else 0
        
        # Redirects
        features['NoOfURLRedirect'] = response.history.__len__()
        features['NoOfSelfRedirect'] = sum(1 for r in response.history if extract_domain(r.url) == extract_domain(url))
        
        # User interaction (CRITICAL for phishing)
        forms = soup.find_all('form')
        features['HasSubmitButton'] = 1 if soup.find('button', type='submit') or soup.find('input', type='submit') else 0
        features['HasPasswordField'] = 1 if soup.find('input', type='password') else 0
        features['HasHiddenFields'] = 1 if soup.find('input', type='hidden') else 0
        
        # External form submission (HUGE phishing indicator!)
        features['HasExternalFormSubmit'] = 1 if any(
            f.get('action', '').startswith('http') and extract_domain(f.get('action', '')) != extract_domain(url)
            for f in forms
        ) else 0
        
        # Security features
        features['NoOfPopup'] = len(re.findall(r'popup|alert|window\.open', html, re.I))
        features['NoOfiFrame'] = len(soup.find_all('iframe'))
        
        # Branding
        features['HasSocialNet'] = 1 if any(domain in html for domain in ['facebook', 'twitter', 'linkedin']) else 0
        features['HasCopyrightInfo'] = 1 if '©' in html or 'copyright' in html.lower() else 0
        
        # Keywords
        features['Bank'] = 1 if 'bank' in html.lower() else 0
        features['Pay'] = 1 if 'pay' in html.lower() else 0
        features['Crypto'] = 1 if 'crypto' in html.lower() or 'bitcoin' in html.lower() else 0
        
        # Resources
        features['NoOfImage'] = len(soup.find_all('img'))
        features['NoOfCSS'] = len(soup.find_all('link', rel='stylesheet'))
        features['NoOfJS'] = len(soup.find_all('script'))
        
        # External references
        all_links = soup.find_all('a', href=True)
        domain_url = extract_domain(url)
        features['NoOfSelfRef'] = sum(1 for link in all_links if extract_domain(link['href']) == domain_url or link['href'].startswith('/'))
        features['NoOfEmptyRef'] = sum(1 for link in all_links if link['href'] in ['', '#'])
        features['NoOfExternalRef'] = sum(1 for link in all_links if extract_domain(link['href']) not in [domain_url, ''])
        
        return features
    
    except (requests.Timeout, requests.RequestException):
        # Network error: return safe defaults (prevent false positives)
        return {key: 0 for key in CONTENT_FEATURE_NAMES}
    
    except Exception:
        return {key: 0 for key in CONTENT_FEATURE_NAMES}
```

#### 2. **Heuristic Engine (9 Checks)**

```
src/heuristics/
├── __init__.py
├── brand.py                 # Brand impersonation
├── dns_ssl.py               # DNS + SSL checks
├── whois_age.py             # Domain age
└── path_analysis.py         # TLD, IP, keywords, punycode
```

**Brand Impersonation:**
```python
from Levenshtein import distance

def check_brand_impersonation(url: str) -> dict:
    """Detect brand impersonation via Levenshtein distance."""
    
    BRANDS = ['google', 'paypal', 'amazon', 'microsoft', 'apple', 'facebook', ...]
    HOMOGLYPH_MAP = {'0': 'o', '1': 'l', '3': 'e', '5': 's', '4': 'a', '8': 'b'}
    
    domain = extract_domain(url)
    domain_lower = domain.lower()
    
    # Homoglyph normalization
    normalized = domain_lower
    for digit, letter in HOMOGLYPH_MAP.items():
        normalized = normalized.replace(digit, letter)
    
    # Check against brands
    for brand in BRANDS:
        # Raw distance
        ed = distance(domain_lower, brand)
        if ed <= 2:
            return {
                'is_brand_impersonation': True,
                'brand': brand,
                'impersonation_type': 'typosquat',
                'distance': ed,
                'penalty_points': 30
            }
        
        # Normalized distance
        ned = distance(normalized, brand)
        if ned == 0:
            return {
                'is_brand_impersonation': True,
                'brand': brand,
                'impersonation_type': 'homoglyph',
                'distance': 0,
                'penalty_points': 30
            }
    
    return {'is_brand_impersonation': False, 'penalty_points': 0}
```

**DNS + SSL:**
```python
import socket, ssl

def check_dns(url: str, timeout: int = 5) -> dict:
    """Verify DNS resolution."""
    try:
        domain = extract_domain(url)
        ip = socket.gethostbyname(domain)
        return {'dns_resolves': True, 'ip_address': ip, 'penalty_points': 0}
    except socket.gaierror:
        return {'dns_resolves': False, 'penalty_points': 15}
    except socket.timeout:
        return {'dns_resolves': False, 'penalty_points': 15}

def check_ssl(url: str, timeout: int = 8) -> dict:
    """Validate SSL certificate."""
    try:
        domain = extract_domain(url)
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                return {'ssl_valid': True, 'certificate': cert, 'penalty_points': 0}
    except (ssl.SSLError, socket.error, socket.timeout):
        return {'ssl_valid': False, 'penalty_points': 15}
```

**WHOIS Domain Age:**
```python
import whois
from datetime import datetime, timedelta

def check_domain_age(url: str, timeout: int = 10) -> dict:
    """Check domain registration age."""
    try:
        domain = extract_domain(url)
        whois_data = whois.whois(domain)
        creation_date = whois_data.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        age_days = (datetime.now() - creation_date).days
        is_new = age_days < 180
        
        return {
            'creation_date': creation_date,
            'age_days': age_days,
            'is_new_domain': is_new,
            'penalty_points': 20 if is_new else 0
        }
    except Exception:
        return {'age_days': None, 'penalty_points': 0}
```

**Path Analysis:**
```python
import re
from tldextract import extract as tld_extract

def check_suspicious_tld(url: str) -> dict:
    """Flag risky TLDs."""
    SUSPICIOUS_TLDS = {'.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.club', '.pw', ...}
    domain = extract_domain(url)
    tld = '.' + tld_extract(domain).suffix
    
    return {
        'suspicious_tld': tld in SUSPICIOUS_TLDS,
        'tld': tld,
        'penalty_points': 20 if tld in SUSPICIOUS_TLDS else 0
    }

def check_ip_based_domain(url: str) -> dict:
    """Check if domain is IP address."""
    domain = extract_domain(url)
    try:
        import ipaddress
        ipaddress.ip_address(domain)
        return {'is_ip_domain': True, 'penalty_points': 30}
    except:
        return {'is_ip_domain': False, 'penalty_points': 0}

def check_ip_subdomain(url: str) -> dict:
    """Detect IP in subdomain."""
    domain = extract_domain(url)
    pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    has_ip = bool(re.search(pattern, domain))
    return {
        'ip_in_subdomain': has_ip,
        'penalty_points': 25 if has_ip else 0
    }

def check_phishing_keywords(url: str) -> dict:
    """Scan for phishing keywords."""
    KEYWORDS = {'login', 'signin', 'verify', 'authenticate', 'secure', 'account', ..., 'urgent', ...}
    found = [kw for kw in KEYWORDS if kw in url.lower()]
    penalty = min(len(found) * 3, 15)
    return {
        'has_phishing_keywords': len(found) > 0,
        'keywords_found': found,
        'keyword_count': len(found),
        'penalty_points': penalty
    }

def check_punycode(url: str) -> dict:
    """Detect Punycode/IDN (xn--)."""
    domain = extract_domain(url)
    has_punycode = 'xn--' in domain
    return {
        'has_punycode': has_punycode,
        'penalty_points': 20 if has_punycode else 0
    }
```

#### 3. **Parallel Heuristics Execution**

```
src/predictor.py (partial)
```

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_heuristics_parallel(url: str, timeout_total: int = 6) -> dict:
    """Run 9 heuristic checks in parallel."""
    
    tasks = {
        'brand': check_brand_impersonation,
        'dns': check_dns,
        'ssl': check_ssl,
        'whois': check_domain_age,
        'tld': check_suspicious_tld,
        'ip_domain': check_ip_based_domain,
        'ip_subdomain': check_ip_subdomain,
        'keywords': check_phishing_keywords,
        'punycode': check_punycode,
    }
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=9) as executor:
        futures = {
            executor.submit(func, url): name 
            for name, func in tasks.items()
        }
        
        for future in as_completed(futures, timeout=timeout_total):
            check_name = futures[future]
            try:
                results[check_name] = future.result()
            except Exception as e:
                results[check_name] = {'penalty_points': 0}  # Graceful fallback
    
    return results
```

#### 4. **Score Fusion & Trust Calibration**

```
src/fusion.py
```

```python
def calculate_trust_factor(
    heuristic_results: dict,
    url: str  # needed for HTTPS check
) -> tuple[float, int]:
    """Calculate dynamic trust factor (0.4-1.0)."""
    
    clean_signals = 0
    
    # Signal 1: SSL + HTTPS
    if (heuristic_results['ssl'].get('ssl_valid', False) and
        url.lower().startswith('https://')):
        clean_signals += 1
    
    # Signal 2: DNS resolves
    if heuristic_results['dns'].get('dns_resolves', False):
        clean_signals += 1
    
    # Signal 3: Old domain
    if (heuristic_results['whois'].get('age_days', 0) and
        heuristic_results['whois']['age_days'] > 180):
        clean_signals += 1
    
    # Signal 4: Legitimate TLD
    if not heuristic_results['tld'].get('suspicious_tld', False):
        clean_signals += 1
    
    # Signal 5: No IP
    if (not heuristic_results['ip_domain'].get('is_ip_domain', False) and
        not heuristic_results['ip_subdomain'].get('ip_in_subdomain', False)):
        clean_signals += 1
    
    # Signal 6: No brand impersonation
    if not heuristic_results['brand'].get('is_brand_impersonation', False):
        clean_signals += 1
    
    trust_factor = 1.0 - (clean_signals / 6) * 0.6  # Range: 0.4 to 1.0
    
    return trust_factor, clean_signals


def fuse(
    ml_prob: float,
    trust_factor: float,
    heuristic_results: dict,
    content_features: dict
) -> dict:
    """Fuse ML + heuristics into 0-100 risk score."""
    
    raw_score = 0.0
    score_breakdown = {}
    
    # 11 signals
    ml_base = ml_prob * 60 * trust_factor
    raw_score += ml_base
    score_breakdown['ml_base'] = ml_base
    
    for signal_name in ['brand', 'ip_domain', 'ip_subdomain', 'punycode', 'tld', 'whois', 'keywords', 'ssl', 'dns']:
        penalty = heuristic_results[signal_name].get('penalty_points', 0)
        raw_score += penalty
        score_breakdown[signal_name] = penalty
    
    # Content indicator (password + external form)
    content_penalty = (
        content_features.get('HasPasswordField', 0) * 10 +
        content_features.get('HasExternalFormSubmit', 0) * 10
    )
    raw_score += content_penalty
    score_breakdown['content_indicators'] = content_penalty
    
    # Normalize to 0-100
    final_score = min(raw_score / 150 * 100, 100.0)
    
    return {
        'raw_score': raw_score,
        'final_score': final_score,
        'score_breakdown': score_breakdown,
        'trust_factor': trust_factor
    }
```

#### 5. **SHAP Explainability**

```
src/explainer.py
```

```python
import shap
import matplotlib.pyplot as plt

def explain(model, feature_vector: np.ndarray) -> dict:
    """Generate SHAP explanation."""
    
    # TreeExplainer for XGBoost
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(feature_vector)
    
    # Get base value + prediction
    base_value = explainer.expected_value
    prediction = model.predict_proba([feature_vector])[0][0]  # P(phishing)
    
    # Top risk features (pushing toward phishing)
    risk_indices = np.argsort(shap_values[0])[-5:]  # Top 5
    top_risk = [
        {
            'feature': FEATURE_NAMES[i],
            'value': feature_vector[0][i],
            'shap': shap_values[0][i]
        }
        for i in risk_indices[::-1]
    ]
    
    # Top safe features (pushing toward legitimate)
    safe_indices = np.argsort(shap_values[0])[:5]  # Bottom 5
    top_safe = [
        {
            'feature': FEATURE_NAMES[i],
            'value': feature_vector[0][i],
            'shap': shap_values[0][i]
        }
        for i in safe_indices
    ]
    
    # Generate visualizations
    generate_waterfall_plot(explainer, shap_values, feature_vector)
    generate_heatmap_plot(shap_values, feature_vector)
    
    return {
        'base_value': float(base_value),
        'prediction_value': float(prediction),
        'top_risk_features': top_risk,
        'top_safe_features': top_safe
    }
```

#### 6. **PDF Report Generation**

```
src/report.py
```

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(result: PredictionResult, output_path: str):
    """Generate deterministic PDF report."""
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    
    # 1. Header
    elements.append(Paragraph(f"<b>PhishGuard Report</b>", getSampleStyleSheet()['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"URL: {result.url}", getSampleStyleSheet()['Normal']))
    elements.append(Paragraph(f"Timestamp: {datetime.now()}",styles['Normal']))
    
    # 2. Risk Summary (with gauge image)
    elements.append(PageBreak())
    elements.append(Paragraph("<b>Risk Summary</b>", styles['Heading2']))
    summary_table = Table([
        ['Score', str(int(result.risk_score))],
        ['Risk Level', result.risk_level],
        ['Verdict', result.verdict],
        ['ML Confidence', f"{result.phishing_prob:.2%}"],
        ['Trust Factor', f"{result.trust_factor:.2f}"]
    ])
    elements.append(summary_table)
    
    # 3. Score Breakdown Table
    elements.append(PageBreak())
    elements.append(Paragraph("<b>Score Breakdown</b>", styles['Heading2']))
    breakdown_rows = [['Signal', 'Points']]
    for signal, points in result.score_breakdown.items():
        breakdown_rows.append([signal, f"{points:.1f}"])
    breakdown_table = Table(breakdown_rows)
    elements.append(breakdown_table)
    
    # 4. Heuristic Findings
    elements.append(PageBreak())
    elements.append(Paragraph("<b>Heuristic Findings</b>", styles['Heading2']))
    for check_name, result_data in result.heuristic_flags.items():
        elements.append(Paragraph(f"<b>{check_name}:</b> {result_data}", styles['Normal']))
    
    # 5. SHAP Attribution
    elements.append(PageBreak())
    elements.append(Paragraph("<b>SHAP Feature Attribution</b>", styles['Heading2']))
    elements.append(Paragraph(f"Base Value: {result.shap_explanation.base_value:.4f}", styles['Normal']))
    elements.append(Paragraph(f"Prediction Value: {result.shap_explanation.prediction_value:.4f}", styles['Normal']))
    
    # Top risk features
    elements.append(Paragraph("<b>Top Risk Features:</b>", styles['Heading3']))
    for feat in result.shap_explanation.top_risk_features:
        elements.append(Paragraph(f"• {feat['feature']}: {feat['value']} (SHAP: {feat['shap']})", styles['Normal']))
    
    # Top safe features
    elements.append(Paragraph("<b>Top Safe Features:</b>", styles['Heading3']))
    for feat in result.shap_explanation.top_safe_features:
        elements.append(Paragraph(f"• {feat['feature']}: {feat['value']} (SHAP: {feat['shap']})", styles['Normal']))
    
    # 6. Recommendations
    elements.append(PageBreak())
    elements.append(Paragraph("<b>Recommendations</b>", styles['Heading2']))
    recommendations = get_recommendations(result.heuristic_flags)
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", styles['Normal']))
    
    # 7. Technical Appendix
    elements.append(PageBreak())
    elements.append(Paragraph("<b>Technical Appendix - All 49 Features</b>", styles['Heading2']))
    feature_rows = [['Feature', 'Value']]
    for feat_name, feat_val in result.features.items():
        feature_rows.append([feat_name, str(feat_val)])
    feature_table = Table(feature_rows)
    elements.append(feature_table)
    
    # Build PDF
    doc.build(elements)
```

#### 7. **Model Training**

```
train.py
```

```python
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from xgboost import XGBClassifier
import joblib

# Load and prepare data
df = pd.read_csv("dataset/PhiUSIIL_Phishing_URL_Dataset.csv")
df = df.drop(columns=DROP_COLS)
X, y = df.drop(columns=['label']), df['label']

# Train/test split (80/20 stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Train XGBoost
model = XGBClassifier(
    n_estimators=300,
    max_depth=7,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.05,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall: {recall_score(y_test, y_pred):.4f}")
print(f"F1: {f1_score(y_test, y_pred):.4f}")
print(f"AUC: {roc_auc_score(y_test, y_pred_proba[:, 0]):.4f}")

# Cross-validation
cv_scores = cross_val_score(model, X_train, y_train, cv=StratifiedKFold(5), scoring='f1')
print(f"CV F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Save
joblib.dump(model, "models/phishguard_model.pkl")
joblib.dump(X.columns.tolist(), "models/feature_list.pkl")
```

### File Structure
```
src/
├── __init__.py
├── predictor.py             # Main prediction orchestrator
├── fusion.py                # Score fusion + trust calibration
├── explainer.py             # SHAP explanations
├── report.py                # PDF report generation
├── features/
│   ├── __init__.py
│   ├── url_features.py      # 21 URL features
│   └── content_features.py  # 28 content features
├── heuristics/
│   ├── __init__.py
│   ├── brand.py             # Brand impersonation
│   ├── dns_ssl.py           # DNS + SSL checks
│   ├── whois_age.py         # Domain age
│   └── path_analysis.py     # TLD, IP, keywords, punycode
│
├── train.py                 # Model training script
├── test_predict.py          # CLI test interface
├── main.py                  # Entry point
└── models/
    ├── phishguard_model.pkl # Trained XGBoost
    ├── feature_list.pkl     # Feature column order
    ├── eval_report.txt      # Evaluation metrics
    └── plots/
        ├── confusion_matrix.png
        ├── feature_importance.png
        └── score_distribution.png
```

### Key Metrics
- **Contribution**: 30%
- **Estimated Hours**: 70-90 hours
- **Lines of Code**: ~2,500-3,500
- **Complexity**: High (ML, statistics, parallel processing)

### Integration Points
- **With Member 2 (Backend)**: Provide `predict()` function that backend calls
- **With Member 4 (Data)**: Use preprocessed dataset for training

---

# MEMBER 4: DOCUMENTATION + DATA PREPROCESSING (Lighter Contribution)

## Responsibility: 5% | Files: dataset/, documentation, README files

### Overview
Handle data collection, preprocessing, cleaning, and comprehensive project documentation. This is the **lighter contribution** member.

### Deliverables

#### 1. **Data Collection & Preprocessing**

```
dataset/
├── PhiUSIIL_Phishing_URL_Dataset.csv  # Original dataset (download)
├── preprocessing.py                   # Data cleaning script
└── eda.py                             # Exploratory data analysis
```

**Responsibilities:**
- Download PhiUSIIL dataset from UCI ML Repository
- Load and explore dataset (shape, missing values, class distribution)
- Data cleaning:
  - Remove duplicates
  - Handle missing values
  - Verify data types
- Feature engineering validation:
  - Ensure all 49 features are present
  - Check for NaN/Inf values
  - Statistical summary
- Exploratory Data Analysis (EDA):
  - Visualize class distribution (phishing vs legitimate)
  - Feature distributions
  - Correlation analysis
  - Identify outliers

**preprocessing.py:**
```python
import pandas as pd
import numpy as np

# Load
df = pd.read_csv("dataset/PhiUSIIL_Phishing_URL_Dataset.csv")

# Clean
df = df.drop_duplicates()  # Remove duplicates
df = df.dropna(subset=['label'])  # Remove rows with missing label
df = df.fillna(0)  # Fill missing values with 0 (safe default)

# Verify
print(f"Dataset shape: {df.shape}")
print(f"Duplicates: {df.duplicated().sum()}")
print(f"Missing values:\n{df.isnull().sum()}")
print(f"Class distribution:\n{df['label'].value_counts()}")

# Feature validation
REQUIRED_FEATURES = [...]  # 49 features
for feat in REQUIRED_FEATURES:
    assert feat in df.columns, f"Missing feature: {feat}"
    assert not np.isnan(df[feat]).any() or df[feat].dtype == 'object'

# Save cleaned
df.to_csv("dataset/PhiUSIIL_Phishing_URL_Dataset_clean.csv", index=False)
print("✅ Data preprocessing complete")
```

**eda.py:**
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Load
df = pd.read_csv("dataset/PhiUSIIL_Phishing_URL_Dataset_clean.csv")

# 1. Class distribution
plt.figure(figsize=(8, 5))
df['label'].value_counts().plot(kind='bar')
plt.title("Class Distribution: Phishing vs Legitimate")
plt.savefig("dataset/class_distribution.png")

# 2. Feature distributions
fig, axes = plt.subplots(7, 7, figsize=(20, 20))
features = df.columns[:-1]  # 49 features
for idx, feat in enumerate(features):
    ax = axes[idx // 7, idx % 7]
    df[feat].hist(bins=50, ax=ax)
    ax.set_title(feat)
plt.tight_layout()
plt.savefig("dataset/feature_distributions.png")

# 3. Correlation heatmap (top 20 features)
corr = df.corr()
top_corr = corr.nlargest(20, 'label')
sns.heatmap(top_corr, cmap='coolwarm')
plt.savefig("dataset/correlation_heatmap.png")

# 4. Outliers
for feat in df.columns[:-1]:
    Q1 = df[feat].quantile(0.25)
    Q3 = df[feat].quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df[feat] < Q1 - 1.5*IQR) | (df[feat] > Q3 + 1.5*IQR)).sum()
    if outliers > 0:
        print(f"{feat}: {outliers} outliers")

print("✅ EDA complete")
```

#### 2. **Project Documentation**

```
/
├── README.md                           # Main project overview
├── ARCHITECTURE.md                     # System architecture
├── API_DOCUMENTATION.md                # Endpoint documentation
├── FEATURE_ENGINEERING.md              # Feature dictionary
├── MODEL_TRAINING.md                   # Training pipeline
├── DEPLOYMENT.md                       # Deployment guide
├── SECURITY.md                         # Security considerations
├── CONTRIBUTING.md                     # How to contribute
├── TESTING.md                          # Test procedures
└── FAQ.md                              # Frequently asked questions
```

#### 3. **README.md** (Main Project Overview)

Document:
- Project description
- Key features
- Quick start
- Installation steps
- Usage examples
- Model performance
- Tech stack
- Contributing
- License

See existing README.md as template.

#### 4. **ARCHITECTURE.md** (System Design)

Document:
- High-level architecture diagram
- Component descriptions
- Data flow
- Module dependencies
- Design patterns used
- Scalability considerations

#### 5. **API_DOCUMENTATION.md** (Endpoint Reference)

Document:
- All API endpoints
- Request/response formats
- Authentication
- Error codes
- Example requests/responses
- Rate limiting

Example:
```markdown
## POST /api/scan

Scan a single URL for phishing risk.

**Authentication**: Required (Bearer JWT token)

**Request**:
```json
{
  "url": "https://example.com"
}
```

**Response** (Server-Sent Events stream):
```
event: progress
data: {"step": "dns", "message": "Checking DNS..."}

event: progress
data: {"step": "ssl", "message": "Validating SSL..."}

event: done
data: {"url": "...", "score": 82, "risk_level": "Critical", ...}
```

**Error Codes**:
- 401: Unauthorized (invalid JWT)
- 429: Too many requests (rate limit exceeded)
- 500: Internal server error
```

#### 6. **FEATURE_ENGINEERING.md** (Feature Dictionary)

Document all 49 features:
```markdown
# Feature Engineering Dictionary

## URL-Level Features (21)

### 1. URLLength
- **Type**: Numeric
- **Range**: 0-2000
- **Meaning**: Total length of URL string
- **Example**: "https://www.google.com" = 23 characters
- **Phishing Indicator**: Longer URLs (>100 chars) often contain phishing indicators

### 2. DomainLength
- **Type**: Numeric
- **Range**: 0-255
- **Meaning**: Length of domain part (netloc)
- **Example**: "google.com" = 10 characters

... (for all 49 features)
```

#### 7. **MODEL_TRAINING.md** (Training Guide)

Document:
- Dataset preparation
- Feature engineering
- Model selection
- Hyperparameter tuning
- Training procedure
- Evaluation metrics
- Performance results

#### 8. **DEPLOYMENT.md** (Production Guide)

Document:
- Development setup
- Production setup
- Docker containerization
- Nginx configuration
- MongoDB setup
- Redis setup
- Environment variables
- Monitoring
- Troubleshooting

#### 9. **SECURITY.md** (Security Considerations)

Document:
- Authentication (JWT)
- Password hashing (bcrypt)
- CORS policy
- Rate limiting
- SQL injection prevention
- HTTPS requirement
- Token refresh mechanism
- Best practices

#### 10. **TESTING.md** (Test Procedures)

Document:
- Unit tests
- Integration tests
- Load testing
- Test URLs
- Expected results
- How to run tests

#### 11. **CONTRIBUTING.md** (Development Guide)

Document:
- Fork and clone
- Branch naming
- Code style
- Commit message format
- Pull request process
- Code review guidelines

#### 12. **FAQ.md** (Frequently Asked Questions)

Document:
- Common questions
- Troubleshooting
- Performance tips
- Scaling advice

### Documentation Details to Include

#### 1. **System Architecture Diagram**
```
[ASCII Diagram]
User → React Frontend → FastAPI Backend → MongoDB/Redis → ML Engine
```

#### 2. **Data Flow Diagram**
```
URL Input → Feature Extraction → ML Model → Heuristics → Score Fusion → Output
```

#### 3. **Entity Relationship Diagram (ER Diagram)**
```
Users ←→ Scans
  ↓
 MongoDB collections
```

#### 4. **Deployment Diagram**
```
Frontend → Nginx → FastAPI → MongoDB
           ↓
          Redis
```

### File Structure

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
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── dataset/
    ├── PhiUSIIL_Phishing_URL_Dataset.csv
    ├── preprocessing.py
    ├── eda.py
    ├── class_distribution.png
    ├── feature_distributions.png
    └── correlation_heatmap.png
```

### Deliverables Checklist

- ✅ Dataset downloaded and validated
- ✅ Data preprocessing script
- ✅ EDA visualizations
- ✅ README.md (comprehensive)
- ✅ API documentation
- ✅ Architecture documentation
- ✅ Feature dictionary
- ✅ Deployment guide
- ✅ Security documentation
- ✅ Contributing guide
- ✅ FAQ document
- ✅ Example .env file
- ✅ Docker configuration files
- ✅ Code comments and docstrings

### Key Metrics
- **Contribution**: 5% (lighter workload)
- **Estimated Hours**: 20-30 hours
- **Deliverables**: 12+ documentation files + 1 preprocessing script
- **Complexity**: Low-Medium (documentation, data handling)

### Integration Points
- **With Member 3 (ML)**: Know dataset structure, validate features
- **With all members**: Keep documentation updated as code evolves

---

# TEAM INTEGRATION & DEPENDENCIES

## Timeline & Phases

### Phase 1: Setup (Week 1)
- **Member 4**: Download & preprocess dataset
- **Member 3**: Begin feature engineering on clean data
- **Member 2**: Set up FastAPI skeleton + database
- **Member 1**: Set up React project

### Phase 2: Core Development (Weeks 2-4)
- **Member 3**: Complete feature extraction, train model, implement heuristics
- **Member 2**: Implement authentication, database models, basic routes
- **Member 1**: Build Dashboard, History, Detail pages
- **Member 4**: Begin documentation

### Phase 3: Integration (Weeks 5-6)
- **Member 2**: Integrate ML pipeline with backend routes
- **Member 1**: Connect frontend to backend APIs, implement SSE
- **Member 3**: SHAP explanations, PDF reports
- **Member 4**: Finalize documentation, deployment guide

### Phase 4: Testing & Deployment (Week 7+)
- **All Members**: Testing, bug fixes
- **Member 2**: Deploy backend (Docker, Nginx)
- **Member 1**: Deploy frontend (Vite build)
- **Member 4**: Final documentation, README polish

## Communication Protocol

### Daily Standup (15 min)
- What did you complete?
- What are you working on?
- Any blockers?

### Weekly Sync (1 hour)
- Review progress
- Adjust timeline if needed
- Discuss integration points

### Code Review Process
- All PRs require review from at least 1 other member
- Focus on security, performance, and documentation

## Success Metrics

| Member | Deliverable | Status |
|--------|-------------|--------|
| Member 1 (Frontend) | React pages, components, API integration | ✅ |
| Member 2 (Backend) | FastAPI routes, DB models, middleware | ✅ |
| Member 3 (ML) | ML pipeline, heuristics, SHAP, PDF | ✅ |
| Member 4 (Docs) | Documentation, dataset, preprocessing | ✅ |

---

# VIVA PRESENTATION BY ROLE

## Member 1 (Frontend)
- Explain React component architecture
- Demo Dashboard → History → Detail flow
- Discuss SSE integration for real-time updates
- Show responsive design
- Explain authentication context

## Member 2 (Backend)
- Explain FastAPI design + async operations
- Demo API endpoints + data models
- Discuss middleware (JWT, rate limiting)
- Explain database indexes + Redis caching
- Show error handling + graceful degradation

## Member 3 (ML)
- Explain 49 features + why they matter
- Demo model training pipeline
- Explain 9 heuristic checks + parallel execution
- Discuss trust calibration innovation
- Show SHAP explainability
- Explain score fusion algorithm

## Member 4 (Documentation)
- Explain dataset preparation
- Show EDA visualizations
- Discuss key insights from data
- Present architecture diagrams
- Show deployment guide
- Explain project structure

---

This division ensures:
✅ **Clear ownership** - each member has defined areas
✅ **Balanced workload** - 30%, 35%, 30%, 5%
✅ **High dependency** - members must communicate/integrate
✅ **Viva readiness** - each can explain their part deeply
✅ **Professional structure** - mirrors real team projects

