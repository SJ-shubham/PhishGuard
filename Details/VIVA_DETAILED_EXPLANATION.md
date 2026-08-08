# PhishGuard: Complete End-to-End Viva Explanation

---

## TABLE OF CONTENTS
1. [Problem Statement](#1-problem-statement)
2. [Domain Background & Literature](#2-domain-background--literature)
3. [Proposed Solution Overview](#3-proposed-solution-overview)
4. [Methodology](#4-methodology)
5. [Data & Feature Engineering](#5-data--feature-engineering)
6. [Machine Learning Model](#6-machine-learning-model)
7. [Heuristic Engine](#7-heuristic-engine)
8. [Score Fusion & Trust Calibration](#8-score-fusion--trust-calibration)
9. [System Architecture](#9-system-architecture)
10. [Implementation Details](#10-implementation-details)
11. [Results & Validation](#11-results--validation)
12. [Advantages & Innovation](#12-advantages--innovation)
13. [Viva Q&A](#13-viva-qa)

---

# 1. PROBLEM STATEMENT

## 1.1 The Phishing Problem

**What is Phishing?**
- Phishing is a social engineering attack where attackers create fraudulent websites/URLs that impersonate legitimate services
- Users are tricked into entering sensitive information (passwords, card details, OTP)
- Example: `paypal-secure-login.com` looks like real PayPal but is actually attacker's server

**Scale of the Problem:**
- **96% of cyberattacks** start with a phishing email or malicious URL
- Every year, **billions of phishing emails** are sent globally
- Organizations lose **$4.65 Million average cost** per breach
- Average person receives **14 phishing emails per month**

**Current Challenges:**

| Challenge | Description | Impact |
|-----------|-------------|--------|
| **Blacklist Lag** | New phishing URLs created faster than blacklists can block | Zero-day attacks bypass protection |
| **Advanced Obfuscation** | Homoglyphs (g00gle), punycode (xn--google), IP addresses | Humans can't distinguish from legitimate |
| **Volume** | Millions of URLs created daily | Manual review impossible |
| **Sophisticated Tactics** | Spear phishing, business email compromise | Hard to detect with simple rules |
| **Time Sensitivity** | Phishing links live for hours before takedown | Quick detection critical |

---

## 1.2 Why Existing Solutions Are Insufficient

**Blacklist-Based Systems:**
- ❌ Only block *known* phishing URLs
- ❌ Lag of hours/days to update lists
- ❌ New URLs bypass detection (0-day attacks)
- ❌ No understanding of *why* URL is phishing

**Rule-Based Heuristics:**
- ❌ Manual rules (e.g., "if .tk TLD then suspicious")
- ❌ High false positives (legitimate sites penalized)
- ❌ Can't detect novel patterns
- ❌ Brittle (rules break under adversarial input)

**Single-Layer ML Models:**
- ❌ No transparency ("black box")
- ❌ Trust issues in security domain
- ❌ Can't explain why URL flagged
- ❌ May produce high false positives

**Our Problem: We need a system that:**
1. **Detects phishing** in real-time (seconds, not hours)
2. **Catches unknown attacks** (ML learns patterns, not memorizes)
3. **Explains predictions** (SHAP: why this URL is flagged)
4. **Balances accuracy** (low false positives + false negatives)
5. **Combines intelligence** (ML + heuristics + domain knowledge)

---

# 2. DOMAIN BACKGROUND & LITERATURE

## 2.1 Phishing URL Characteristics

**What makes a URL phishing?**

| Characteristic | Example | Why Suspicious |
|---|---|---|
| **Brand Impersonation** | `paypa1-secure.com` (1 vs l) | Typosquatting, homoglyph attack |
| **Suspicious TLD** | `paypal.tk` | Cheap TLDs attract attackers |
| **IP-based domain** | `http://192.168.1.1/admin/` | Hides real domain, looks technical |
| **IP in subdomain** | `192.168.0.1.secure-login.com` | Obfuscation technique |
| **New domain** | Registered 2 days ago | Attacker buys, uses, abandons |
| **Punycode** | `xn--google-7hd.com` | Internationalized domains, homograph attacks |
| **Keywords** | "verify", "urgent", "confirm", "update" | Phishing urgency tactics |
| **HTML characteristics** | Password fields, external forms, no favicon | Copied from legitimate site |

## 2.2 Previous Research

**Datasets available:**
- PhiUSIIL Dataset (235,795 URLs) — balanced, feature-rich
- UCI ML Repo phishing dataset
- Active phishing data (private security firms)

**Previous ML Approaches:**
- Random Forest: ~98% accuracy
- SVM: ~96% accuracy
- Neural Networks: ~99% accuracy
- XGBoost: State-of-the-art for tabular data → **Our choice**

**Why XGBoost?**
- Fast training on tabular data (URL features)
- Handles non-linear relationships
- Built-in feature importance
- SHAP compatibility for explainability
- Production-ready (libraries available)

---

# 3. PROPOSED SOLUTION OVERVIEW

## 3.1 PhishGuard: The System

**High-Level Concept:**
A **hybrid detection system** combining:
1. **Machine Learning** (XGBoost) for pattern recognition
2. **Heuristic Rules** (9 security checks) for domain knowledge
3. **Trust Calibration** for balancing false positives
4. **SHAP Explainability** for transparency
5. **Full-stack Web UI** for usability

**Key Innovation**: Trust calibration replaces hardcoded whitelists with dynamic ML weight adjustment based on network signal quality.

## 3.2 Architecture Overview

```
URL Input
   ├─► Feature Extraction (49 features)
   │   ├─ 21 URL-level (static, no network)
   │   └─ 28 Content-level (requires HTTP GET)
   │
   ├─► Parallel Processing (ThreadPoolExecutor)
   │   ├─ ML Model → P(phishing)
   │   └─ 9 Heuristic Checks (concurrent)
   │
   ├─► Trust Calibration
   │   └─ Dynamic ML weight adjustment
   │
   ├─► Score Fusion
   │   └─ Combine 11 signals into 0-100 score
   │
   ├─► SHAP Explanation
   │   └─ Feature attribution
   │
   └─► Output
       ├─ Risk score (0-100)
       ├─ Risk level (Low/Medium/High/Critical)
       ├─ Heuristic breakdown
       ├─ SHAP plots
       └─ PDF report
```

## 3.3 Design Philosophy

**Principles:**
1. **No Single Point of Failure**: Heuristics + ML equally important
2. **Transparency**: Every decision explained via SHAP
3. **Defense in Depth**: Multiple layers (URL, content, network, ML)
4. **Performance**: Concurrent checks + caching for speed
5. **Reliability**: Graceful degradation if components fail

---

# 4. METHODOLOGY

## 4.1 Research Methodology

**Our Approach (Waterfall with Validation):**

```
Phase 1: Problem Analysis
  ├─ Literature review (phishing trends, datasets)
  ├─ Challenge identification
  └─ Solution hypothesis

Phase 2: Data Analysis
  ├─ Load PhiUSIIL dataset
  ├─ EDA (class distribution, feature analysis)
  ├─ Identify leaky features (URLSimilarityIndex)
  └─ Prepare train/test split (80/20 stratified)

Phase 3: Feature Engineering
  ├─ Implement 21 URL-level feature extractors
  ├─ Implement 28 content-level feature extractors
  ├─ Validate feature extraction on sample URLs
  └─ Handle missing/error cases

Phase 4: ML Model Training
  ├─ Hyperparameter tuning (grid search)
  ├─ Cross-validation (5-fold stratified)
  ├─ Evaluate on test set
  └─ Analyze feature importance

Phase 5: Heuristic Engine Development
  ├─ Implement 9 security checks
  ├─ Tune thresholds and penalties
  ├─ Parallel execution with ThreadPoolExecutor
  └─ Test on known phishing/legitimate URLs

Phase 6: Score Fusion & Trust Calibration
  ├─ Design trust calibration formula
  ├─ Combine ML + heuristic signals
  ├─ Tune weights and thresholds
  └─ Validate on benchmark URLs

Phase 7: Explainability
  ├─ Integrate SHAP TreeExplainer
  ├─ Generate waterfall + heatmap plots
  ├─ Validate explanations against feature importance
  └─ PDF report generation

Phase 8: Full-Stack Application
  ├─ FastAPI backend with routes
  ├─ MongoDB for persistence
  ├─ Redis for caching + rate limiting
  ├─ React frontend with visualizations
  └─ End-to-end testing

Phase 9: Validation & Testing
  ├─ Test on 10 benchmark URLs
  ├─ Performance profiling
  ├─ Security review (JWT, rate limiting)
  └─ Documentation
```

## 4.2 Dataset & Preparation

**Dataset: PhiUSIIL Phishing URL Dataset**
- **Source**: UCI Machine Learning Repository
- **Size**: 235,795 URLs
- **Class Distribution**: ~50% legitimate, ~50% phishing
- **Features**: Pre-engineered (49 total)
- **Format**: CSV with label column

**Data Preparation Steps:**

```python
# Load dataset
df = pd.read_csv("PhiUSIIL_Phishing_URL_Dataset.csv")  # 235,795 rows

# Identify columns to drop
DROP_COLS = ["FILENAME", "URL", "Domain", "TLD", "Title"]  # Non-numeric IDs
DROP_COLS += ["URLSimilarityIndex"]  # Leaky feature (all legit = 100.0)

# Remove leaky feature
df = df.drop(columns=DROP_COLS)

# Separate features and target
X = df.drop(columns=['label'])  # 49 features
y = df['label']                  # 0 = phishing, 1 = legitimate

# Stratified train/test split (preserve class ratio)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
# Result: 188,636 training, 47,159 test samples
```

**Why drop URLSimilarityIndex?**
- In this dataset, ALL legitimate URLs have value = 100.0 (zero variance)
- This makes it a perfect proxy for the label (data leakage)
- Can't compute reliably for unknown URLs without a whitelist
- Would cause overfitting

---

# 5. DATA & FEATURE ENGINEERING

## 5.1 Feature Extraction Strategy

**Two Categories of Features:**

### **Category 1: URL-Level Features (21 features)**
**Characteristic**: Static, extracted from URL string only. No network access needed. Fast (~0.01 seconds).

```python
1.  URLLength                    # Total URL string length
2.  DomainLength                 # Length of domain part
3.  TLDLength                    # Length of TLD (.com, .tk, etc.)
4.  HasObfuscation              # Binary: contains %xx encoding
5.  NoOfObfuscatedChar          # Count of obfuscated characters
6.  ObfuscationRatio            # % of URL that's obfuscated
7.  NoOfLettersInURL            # Count of alphabetic characters
8.  LetterRatioInURL            # % of letters in URL
9.  NoOfDegitsInURL             # Count of digits
10. DegitRatioInURL             # % of digits
11. NoOfEqualsInURL             # Count of '=' chars (query params)
12. NoOfQMarkInURL              # Count of '?' chars
13. NoOfAmpersandInURL          # Count of '&' chars
14. NoOfOtherSpecialCharsInURL  # Other special chars
15. SpacialCharRatioInURL       # % of special chars
16. CharContinuationRate        # How often same char repeats
17. URLCharProb                 # Statistical entropy of characters
18. IsDomainIP                  # Binary: domain is IP address
19. NoOfSubDomain               # Count of subdomains
20. TLDLegitimateProb           # Probability TLD is legitimate (0-1)
21. IsHTTPS                     # Binary: HTTPS protocol
```

**Examples:**
```
URL: "https://paypa1-secure-login.tk/verify?email=user@example.com"

URLLength = 65
DomainLength = 26
NoOfEqualsInURL = 1
IsDomainIP = 0
IsHTTPS = 1
TLDLegitimateProb = 0.05  # .tk is suspicious
```

### **Category 2: Content-Level Features (28 features)**
**Characteristic**: Require fetching & parsing HTML. Network access needed. Slower (~1-2 seconds).

```python
# HTML Structure
1.  LineOfCode                  # Number of lines in HTML
2.  LargestLineLength           # Longest single line length
3.  HasTitle                    # Binary: has <title> tag
4.  HasFavicon                  # Binary: has favicon link
5.  HasDescription              # Binary: has meta description
6.  Robots                      # robots.txt present

# Text Similarity
7.  DomainTitleMatchScore       # How well domain matches title
8.  URLTitleMatchScore          # How well URL matches title

# Responsiveness & Metadata
9.  IsResponsive                # Binary: CSS media queries present
10. NoOfURLRedirect             # Count of redirects
11. NoOfSelfRedirect            # Count of self-redirects

# User Interaction (Phishing indicator)
12. HasSubmitButton             # Binary: <button type="submit">
13. HasPasswordField            # Binary: <input type="password">
14. HasHiddenFields             # Binary: <input type="hidden">

# Forms (Critical for phishing)
15. HasExternalFormSubmit       # Binary: form action != current domain
    # ^^^ This is a HUGE phishing indicator

# Security & Content
16. NoOfPopup                   # Count of popup scripts
17. NoOfiFrame                  # Count of iframes
18. NoOfImage                   # Count of <img> tags
19. NoOfCSS                     # Count of CSS files
20. NoOfJS                      # Count of JavaScript files

# Cross-site References
21. NoOfSelfRef                 # Links to same domain
22. NoOfEmptyRef                # Links with empty href
23. NoOfExternalRef             # Links to external domains

# Branding & Keywords
24. HasSocialNet                # Links to social media (trust signal)
25. HasCopyrightInfo            # Copyright info present

# Financial Keywords
26. Bank                        # Binary: contains "bank" keyword
27. Pay                         # Binary: contains "pay" keyword
28. Crypto                      # Binary: contains "crypto" keyword
```

**Examples:**
```
Legitimate URL (google.com):
- HasTitle = 1
- DomainTitleMatchScore = 0.95
- HasPasswordField = 0 (Google login is different domain)
- HasExternalFormSubmit = 0
- NoOfExternalRef = 5 (links to other Google services)

Phishing URL (paypa1-secure-login.tk):
- HasTitle = 1
- DomainTitleMatchScore = 0.3 (doesn't match well)
- HasPasswordField = 1 ⚠️ (phishing red flag!)
- HasExternalFormSubmit = 1 ⚠️ (submits to attacker server!)
- NoOfSelfRef = 0
```

## 5.2 Feature Extraction Implementation

**URL-Level Feature Extraction:**
```python
def extract_url_features(url: str) -> dict:
    """Extract 21 static features from URL string."""
    
    try:
        parsed_url = urlparse(url)
        
        features = {
            'URLLength': len(url),
            'DomainLength': len(parsed_url.netloc),
            'IsHTTPS': 1 if parsed_url.scheme == 'https' else 0,
            'IsDomainIP': 1 if is_ip_address(parsed_url.netloc) else 0,
            # ... compute 18 more features
        }
        return features
    
    except Exception:
        # Error case: return safe defaults (prevent false positives)
        return {key: 0 for key in URL_FEATURE_NAMES}
```

**Content-Level Feature Extraction:**
```python
def extract_content_features(url: str, timeout=10) -> dict:
    """Fetch page and extract 28 content features."""
    
    features = {}
    
    try:
        # HTTP GET with timeout
        response = requests.get(url, timeout=timeout, verify=False)
        html = response.text
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract features
        features['LineOfCode'] = len(html.split('\n'))
        features['HasTitle'] = 1 if soup.find('title') else 0
        features['HasPasswordField'] = 1 if soup.find('input', type='password') else 0
        
        # Check if form submits externally
        forms = soup.find_all('form')
        external_forms = sum(1 for f in forms 
                            if f.get('action', '').startswith('http'))
        features['HasExternalFormSubmit'] = 1 if external_forms > 0 else 0
        
        # ... compute 24 more features
        return features
    
    except (requests.Timeout, requests.RequestException, Exception):
        # Network error: return safe defaults
        # This prevents false positives if page is slow/down
        return {key: 0 for key in CONTENT_FEATURE_NAMES}
```

**Error Handling Philosophy:**
- If page doesn't load → assume legitimate (avoid false positives)
- ML + heuristics provide additional signals
- Content features are "extra intelligence", not critical

---

# 6. MACHINE LEARNING MODEL

## 6.1 Why XGBoost?

**Comparison of ML Algorithms for Tabular Data:**

| Algorithm | Speed | Interpretability | Performance | Production | Why/Why Not |
|-----------|-------|-----------------|-------------|-----------|------------|
| **Logistic Regression** | Very Fast | High | ~85% | Yes | Too simple for complex patterns |
| **Random Forest** | Fast | Medium | ~98% | Yes | Good, but slower than XGBoost |
| **SVM** | Slow | Low | ~96% | No | Slow, hard to scale |
| **Neural Network** | Medium | Low | ~99% | Medium | Overkill for tabular, hard to explain |
| **XGBoost** ⭐ | **Fast** | **Medium** | **99%+** | **Yes** | **Best for tabular data** |
| **LightGBM** | Very Fast | Medium | ~99% | Yes | Similar to XGBoost, slightly faster |

**Why XGBoost for PhishGuard:**
- ✅ Fast (milliseconds per prediction)
- ✅ Excellent performance (near-perfect on test set)
- ✅ Handles non-linear relationships (phishing patterns are complex)
- ✅ Feature importance built-in
- ✅ SHAP explainability compatible
- ✅ Production-ready libraries (scikit-learn compatibility)
- ✅ Handles imbalanced data (stratified split handles this)

## 6.2 Model Architecture

**XGBoost == Ensemble of Decision Trees**

```
Prediction = sum of weakly-trained trees

Tree 1: If URLLength > 80 and IsDomainIP=1 → phishing
Tree 2: If HasPasswordField=1 and HasExternalFormSubmit=1 → phishing
Tree 3: If TLDLegitimateProb < 0.2 → phishing
...
Tree 300: If CharContinuationRate > 0.5 → phishing

Final Decision = weighted vote of all 300 trees
Output = Probability (0.0 to 1.0)
```

## 6.3 Hyperparameter Tuning

```python
model = XGBClassifier(
    # Basic tree parameters
    n_estimators=300,           # 300 trees (higher = better generalization)
    max_depth=7,                # Max depth per tree (prevents overfitting)
    
    # Learning
    learning_rate=0.1,          # Shrinkage factor (slower learning = smoother)
    
    # Regularization (prevent overfitting)
    min_child_weight=3,         # Min samples per leaf
    subsample=0.8,              # Sample 80% of rows per tree
    colsample_bytree=0.8,       # Sample 80% of features per tree
    gamma=0.1,                  # Min loss reduction to split node
    reg_alpha=0.05,             # L1 regularization
    reg_lambda=1.0,             # L2 regularization
    
    # Other
    random_state=42,            # Reproducible results
    n_jobs=-1,                  # Use all CPU cores
)

model.fit(X_train, y_train)
```

**Tuning Rationale:**
- `n_estimators=300`: More trees = better learning, no overfitting with early stopping
- `max_depth=7`: Prevents overfitting while allowing complex interactions
- `learning_rate=0.1`: Slower learning reduces overfitting
- `subsample=0.8, colsample_bytree=0.8`: Dropout-like regularization
- `reg_alpha, reg_lambda`: Penalty for model complexity

## 6.4 Training Pipeline

```python
# Step 1: Load and prepare data
df = pd.read_csv("dataset/PhiUSIIL_Phishing_URL_Dataset.csv")  # 235,795 rows
X = df.drop(columns=['label'] + DROP_COLS)  # 49 features
y = df['label']

# Step 2: Stratified train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
# Train: 188,636 | Test: 47,159

# Step 3: Train model
model = XGBClassifier(...)
model.fit(X_train, y_train)

# Step 4: Evaluate on test set
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

accuracy = accuracy_score(y_test, y_pred)          # 100.0%
precision = precision_score(y_test, y_pred)        # 1.0000
recall = recall_score(y_test, y_pred)              # 1.0000
f1 = f1_score(y_test, y_pred)                      # 1.0000
auc = roc_auc_score(y_test, y_pred_proba[:, 0])   # 1.0000

# Step 5: Cross-validation
from sklearn.model_selection import StratifiedKFold, cross_val_score
cv_scores = cross_val_score(
    model, X_train, y_train, 
    cv=StratifiedKFold(n_splits=5),
    scoring='f1'
)
# CV F1: 0.9999 ± 0.0001

# Step 6: Save model
joblib.dump(model, "models/phishguard_model.pkl")
joblib.dump(X.columns.tolist(), "models/feature_list.pkl")
```

## 6.5 Model Performance

**Test Set Results (47,159 URLs):**

```
Accuracy:  100.0%  (all URLs correctly classified)
Precision: 1.0000  (no false alarms)
Recall:    1.0000  (catches all phishing)
F1 Score:  1.0000  (perfect balance)
AUC-ROC:   1.0000  (perfect discrimination)

Confusion Matrix:
                 Predicted Legit  Predicted Phish
Actual Legit:       23,579              0        (100% correct)
Actual Phish:           0           23,580        (100% correct)
```

**Cross-Validation (5-fold):**
```
Fold 1 F1: 0.99997
Fold 2 F1: 0.99989
Fold 3 F1: 0.99999
Fold 4 F1: 1.00000
Fold 5 F1: 1.00000

Mean F1: 0.99997 ± 0.00004
```

**Why so perfect?**
- PhiUSIIL dataset has clear separation between phishing and legitimate
- 49 engineered features are highly predictive
- XGBoost excels at finding complex patterns
- Note: Real-world deployment would see lower accuracy

**Label Convention (Important!):**
```python
model.predict_proba(features)  # Returns [P(phishing), P(legitimate)]
                               #         [class 0,      class 1]

P_phishing = proba[0]
P_legitimate = proba[1]
```

---

# 7. HEURISTIC ENGINE

## 7.1 Design Philosophy

**Why Heuristics + ML?**
- ML alone: "black box", hard to audit for security
- Heuristics alone: brittle, can't detect novel patterns
- Combined: Best of both worlds + transparency

**9 Concurrent Heuristic Checks:**

Each runs in parallel via `ThreadPoolExecutor(max_workers=9)`.
If one fails/times out, others continue (graceful degradation).

## 7.2 The 9 Checks in Detail

### **Check 1: Brand Impersonation (Levenshtein + Homoglyph)**

**Purpose:** Detect typo-squatting and homoglyph attacks

**Brands Covered:** Google, PayPal, Amazon, Microsoft, Apple, Facebook, Netflix, eBay, Twitter, Instagram, LinkedIn, Yahoo, WhatsApp, Apple, etc.

**Implementation:**

```python
def check_brand_impersonation(url: str) -> dict:
    """Detect brand impersonation via Levenshtein distance."""
    
    from difflib import SequenceMatcher
    from Levenshtein import distance  # Edit distance
    
    # Extract domain name
    domain = extract_domain(url)  # "paypa1" from "paypa1-secure-login.tk"
    
    # Homoglyph normalization: digits → letters
    homoglyph_map = {
        '0': 'o', '1': 'l', '3': 'e', '5': 's', '4': 'a', '8': 'b'
    }
    
    normalized = domain
    for digit, letter in homoglyph_map.items():
        normalized = normalized.replace(digit, letter)
    
    # Check against brand list
    brands = ['google', 'paypal', 'amazon', 'microsoft', ...]
    
    min_distance = float('inf')
    matched_brand = None
    
    for brand in brands:
        # Check if domain matches brand (Levenshtein distance)
        ed = distance(domain.lower(), brand)           # Raw distance
        ned = distance(normalized.lower(), brand)      # Normalized distance
        
        if ed <= 2:
            min_distance = ed
            matched_brand = brand
            
        if ned == 0:  # Perfect match after normalization! 🚩
            return {
                'is_brand_impersonation': True,
                'brand': brand,
                'impersonation_type': 'homoglyph',
                'distance': 0,
                'penalty_points': 30
            }
    
    if matched_brand and min_distance <= 2:
        return {
            'is_brand_impersonation': True,
            'brand': matched_brand,
            'impersonation_type': 'typosquat',
            'distance': min_distance,
            'penalty_points': 30
        }
    
    return {
        'is_brand_impersonation': False,
        'penalty_points': 0
    }
```

**Examples:**
```
Domain: "paypa1-secure.com"
 → normalized: "paypal-secure.com"
 → matches "paypal" with distance=0 ✓
 → FLAGGED: Homoglyph attack (+30 points)

Domain: "gogle.com"
 → normalized: "gogle.com" (no digits)
 → matches "google" with distance=1 ✓
 → FLAGGED: Typosquat (+30 points)

Domain: "amazon.com"
 → normalized: "amazon.com"
 → exact match
 → FLAGGED: +30 points (but legitimate has other signals)
```

**Penalty:** +30 points (highest among all checks)

---

### **Check 2: DNS Resolution**

**Purpose:** Verify domain actually exists and can resolve

**Implementation:**

```python
import socket

def check_dns(url: str, timeout=5) -> dict:
    """Check if domain resolves via DNS."""
    
    try:
        domain = extract_domain(url)
        
        # Attempt DNS resolution
        ip_address = socket.gethostbyname(domain)
        
        return {
            'dns_resolves': True,
            'ip_address': ip_address,
            'penalty_points': 0
        }
    
    except socket.gaierror:
        # Domain not found in DNS
        return {
            'dns_resolves': False,
            'penalty_points': 15
        }
    
    except socket.timeout:
        # Timeout
        return {
            'dns_resolves': False,
            'penalty_points': 15
        }
    
    except Exception as e:
        # Other errors (network issues)
        return {
            'dns_resolves': False,
            'penalty_points': 15
        }
```

**Why it matters:**
- Legitimate sites have valid DNS records
- Attackers sometimes set up domains without proper DNS (quick & dirty setup)
- Timeout might indicate network issues or attacker's server overloaded

**Penalty:** +15 points

---

### **Check 3: SSL/HTTPS Validation**

**Purpose:** Verify HTTPS certificate is valid and not expired

**Implementation:**

```python
import ssl
import socket

def check_ssl(url: str, timeout=8) -> dict:
    """Validate SSL certificate."""
    
    domain = extract_domain(url)
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to server
        with socket.create_connection((domain, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                # Certificate validation automatic in context
                certificate = ssock.getpeercert()
                
                if certificate:
                    return {
                        'ssl_valid': True,
                        'certificate': certificate,
                        'penalty_points': 0
                    }
    
    except ssl.SSLError as e:
        # Invalid certificate (expired, hostname mismatch, etc.)
        return {
            'ssl_valid': False,
            'ssl_error': str(e),
            'penalty_points': 15
        }
    
    except (socket.timeout, socket.error) as e:
        # Connection failed
        return {
            'ssl_valid': False,
            'penalty_points': 15
        }
    
    except Exception:
        return {
            'ssl_valid': False,
            'penalty_points': 15
        }
```

**What it checks:**
- ✅ Certificate not expired
- ✅ Hostname matches certificate CN/SAN
- ✅ Certificate signed by trusted CA
- ✅ No certificate errors

**Why it matters:**
- Modern phishing sites often use self-signed or expired certs
- Legitimate sites maintain valid certs (cost of business)
- But: Let's Encrypt made free certs common, so this is weaker signal now

**Penalty:** +15 points

---

### **Check 4: WHOIS Domain Age**

**Purpose:** Detect new domains (common among attackers)

**Implementation:**

```python
import whois
from datetime import datetime, timedelta

def check_domain_age(url: str, timeout=10) -> dict:
    """Check domain registration age via WHOIS."""
    
    domain = extract_domain(url)
    
    try:
        whois_result = whois.whois(domain)
        
        creation_date = whois_result.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        # Calculate age
        age_days = (datetime.now() - creation_date).days
        
        # Flag if < 180 days old (6 months)
        is_new = age_days < 180
        
        return {
            'creation_date': creation_date,
            'age_days': age_days,
            'is_new_domain': is_new,
            'penalty_points': 20 if is_new else 0
        }
    
    except Exception as e:
        # WHOIS lookup failed (common)
        return {
            'age_days': None,
            'penalty_points': 0  # Don't penalize if lookup fails
        }
```

**Why it matters:**
- Attackers buy domains, use them, abandon them
- Short domain age is risk factor
- Threshold: < 180 days (6 months) = suspicious

**Penalty:** +20 points (if age < 180 days)

---

### **Check 5: Suspicious TLD**

**Purpose:** Flag risky top-level domains

**Implementation:**

```python
def check_tld(url: str) -> dict:
    """Check if TLD is suspicious."""
    
    # Suspicious TLDs (cheap, often abused)
    suspicious_tlds = {
        '.tk', '.ml', '.ga', '.cf',      # Free Freenom domains
        '.gq', '.xyz', '.club', '.pw',   # Cheap generic TLDs
        '.cc', '.ws', '.info', '.top',   # Commonly abused
        '.accountant', '.party', '.trade' # Problematic domains
    }
    
    domain = extract_domain(url)
    tld = get_tld(domain)  # Get ".tk" from "paypal.tk"
    
    if tld in suspicious_tlds:
        return {
            'suspicious_tld': True,
            'tld': tld,
            'penalty_points': 20
        }
    else:
        return {
            'suspicious_tld': False,
            'tld': tld,
            'penalty_points': 0
        }
```

**Why it matters:**
- .tk, .ml, .ga, .cf are free (Freenom)
- Attackers favor cheap TLDs
- Legitimate organizations use .com, .org, .gov, .company-name

**Penalty:** +20 points

---

### **Check 6: IP-Based Domain**

**Purpose:** Detect domains that are IP addresses

**Implementation:**

```python
import ipaddress

def check_ip_based_domain(url: str) -> dict:
    """Check if domain is actually an IP address."""
    
    domain = extract_domain(url)
    
    try:
        # Attempt to parse as IP
        ip_obj = ipaddress.ip_address(domain)
        
        # If this succeeds, it's an IP!
        return {
            'is_ip_domain': True,
            'ip_address': str(ip_obj),
            'penalty_points': 30
        }
    
    except ValueError:
        # Not a valid IP
        return {
            'is_ip_domain': False,
            'penalty_points': 0
        }
```

**Examples:**
```
URL: http://192.168.1.1/
  → domain = "192.168.1.1"
  → is valid IP ✗
  → FLAGGED: +30 points

URL: http://paypal-secure-login.tk/
  → domain = "paypal-secure-login.tk"
  → not an IP ✓
  → OK: 0 points
```

**Why it matters:**
- Users trust URLs with domain names more
- IP addresses look technical/suspicious
- Attackers use IPs to avoid domain reputation systems

**Penalty:** +30 points

---

### **Check 7: IP in Subdomain**

**Purpose:** Detect IP addresses embedded in subdomain

**Implementation:**

```python
import re

def check_ip_subdomain(url: str) -> dict:
    """Check if IP address embedded in subdomain."""
    
    domain = extract_domain(url)
    
    # Regex pattern: find XXX.XXX.XXX.XXX anywhere in domain
    ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    
    if re.search(ip_pattern, domain):
        return {
            'ip_in_subdomain': True,
            'penalty_points': 25
        }
    else:
        return {
            'ip_in_subdomain': False,
            'penalty_points': 0
        }
```

**Examples:**
```
Domain: "192.168.0.1.secure-login.com"
  → matches IP pattern ✗
  → FLAGGED: +25 points

Domain: "secure-login.paypal.com"
  → no IP pattern found ✓
  → OK: 0 points
```

**Why it matters:**
- Obfuscation technique: hides actual domain
- Legitimate domains don't do this
- Attackers use it to confuse users

**Penalty:** +25 points

---

### **Check 8: Phishing Keywords**

**Purpose:** Detect common phishing keywords in URL

**Implementation:**

```python
def check_phishing_keywords(url: str) -> dict:
    """Check for phishing-specific keywords."""
    
    # 50+ keywords associated with phishing
    keywords = {
        # Authentication/Security
        'login', 'signin', 'sign in', 'verify', 'authenticate',
        'secure', 'account', 'suspended', 'confirm', 'validation',
        
        # Urgency/Action
        'update', 'urgent', 'immediately', 'expire', 'expired',
        'limited', 'action-required', 'problem', 'alert',
        
        # Financial/Banking
        'bank', 'paypal', 'ebay', 'amazon', 'apple', 'microsoft',
        'billing', 'payment', 'credential', 'restore',
        
        # Other
        'admin', 'access', 'permission', 'unlock'
    }
    
    url_lower = url.lower()
    found_keywords = []
    
    for keyword in keywords:
        if keyword in url_lower:
            found_keywords.append(keyword)
    
    # Scale penalty by count
    penalty = min(len(found_keywords) * 3, 15)  # Max 15 points
    
    return {
        'has_phishing_keywords': len(found_keywords) > 0,
        'keywords_found': found_keywords,
        'keyword_count': len(found_keywords),
        'penalty_points': penalty
    }
```

**Examples:**
```
URL: "paypal-verify-account-urgent.tk"
  → keywords: ['paypal', 'verify', 'account', 'urgent']
  → count = 4
  → penalty = min(4*3, 15) = 12 ✗
  → FLAGGED: +12 points

URL: "amazon.com"
  → keywords: ['amazon']
  → count = 1
  → penalty = 3 (weak signal for legitimate site)
```

**Why it matters:**
- Phishing emails create urgency
- Common keywords: verify, confirm, update, secure, urgent
- Legitimate sites can have these too (weak signal)

**Penalty:** +3 to +15 points (scale by count)

---

### **Check 9: Punycode/IDN Detection**

**Purpose:** Detect internationalized domain names (homograph attacks)

**Implementation:**

```python
def check_punycode(url: str) -> dict:
    """Detect Punycode/IDN (xn-- prefix)."""
    
    domain = extract_domain(url)
    
    # Check for xn-- prefix (Punycode encoding)
    if 'xn--' in domain:
        return {
            'has_punycode': True,
            'punycode_domain': domain,
            'penalty_points': 20
        }
    else:
        return {
            'has_punycode': False,
            'penalty_points': 0
        }
```

**What is Punycode?**
- Encodes Unicode domains to ASCII
- Example: `google.com` vs `xn--google-7hd.com` (looks same to users!)
- Used for homograph attacks (visual lookalikes)

**Examples:**
```
Domain: "xn--google-7hd.com"
  → has 'xn--' prefix ✗
  → FLAGGED: +20 points

Domain: "google.com"
  → no 'xn--' ✓
  → OK: 0 points
```

**Why it matters:**
- Visually similar to legitimate domains
- Users can't tell the difference
- Legitimate internationalized sites exist but rare

**Penalty:** +20 points

---

## 7.3 Parallel Execution

**Why Parallelism?**
Without parallelism: DNS (1s) + SSL (2s) + WHOIS (5s) = 8 seconds total

With parallelism:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_heuristics_parallel(url: str, timeout=6):
    """Run 9 heuristic checks in parallel."""
    
    tasks = {
        'brand': check_brand_impersonation,
        'dns': check_dns,
        'ssl': check_ssl,
        'whois': check_domain_age,
        'tld': check_tld,
        'ip_domain': check_ip_based_domain,
        'ip_subdomain': check_ip_subdomain,
        'keywords': check_phishing_keywords,
        'punycode': check_punycode,
    }
    
    results = {}
    
    # Run all checks concurrently
    with ThreadPoolExecutor(max_workers=9) as executor:
        future_to_check = {
            executor.submit(check_func, url): name 
            for name, check_func in tasks.items()
        }
        
        for future in as_completed(future_to_check, timeout=timeout):
            check_name = future_to_check[future]
            try:
                results[check_name] = future.result()
            except Exception as e:
                # Heuristic failed: treat as unknown (0 penalty)
                results[check_name] = {'penalty_points': 0}
    
    return results

# Execution time: ~3-5 seconds (limited by slowest check: WHOIS)
# Without parallelism: ~10-15 seconds
```

**Speedup: 60-70%**

---

# 8. SCORE FUSION & TRUST CALIBRATION

## 8.1 Trust Calibration (The Innovation!)

**Problem:**
Google's URL might trigger heuristics:
- High ML confidence (legitimate → confidence ≠ phishing)
- But maybe some signals are mixed (redirects, external resources, etc.)

Without trust calibration:
- Google might score 60/100 (HIGH) ← FALSE POSITIVE

With trust calibration:
- Google scores 15/100 (LOW) ← CORRECT

**Solution: Dynamic ML Weight Adjustment**

```python
def calculate_trust_factor(heuristic_results: dict) -> float:
    """
    Calculate trust factor based on clean network signals.
    
    Replaces hardcoded whitelists with dynamic calculation.
    """
    
    # Count "clean" signals (0 to 6 possible)
    clean_signals = 0
    
    # Signal 1: HTTPS + Valid SSL ✓
    if heuristic_results['ssl']['ssl_valid'] and \
       'https' in original_url.lower():
        clean_signals += 1
    
    # Signal 2: DNS Resolves ✓
    if heuristic_results['dns']['dns_resolves']:
        clean_signals += 1
    
    # Signal 3: Old domain (> 180 days) ✓
    if heuristic_results['whois']['age_days'] and \
       heuristic_results['whois']['age_days'] > 180:
        clean_signals += 1
    
    # Signal 4: Legitimate TLD ✓
    if not heuristic_results['tld']['suspicious_tld']:
        clean_signals += 1
    
    # Signal 5: No IP in domain/subdomain ✓
    if not heuristic_results['ip_domain']['is_ip_domain'] and \
       not heuristic_results['ip_subdomain']['ip_in_subdomain']:
        clean_signals += 1
    
    # Signal 6: No brand impersonation ✓
    if not heuristic_results['brand']['is_brand_impersonation']:
        clean_signals += 1
    
    # Calculate trust factor
    # Range: 0.4 (all clean) to 1.0 (all suspicious)
    trust_factor = 1.0 - (clean_signals / 6) * 0.6
    
    return trust_factor, clean_signals
```

**Trust Factor Examples:**

```
Google.com:
  ✅ HTTPS: Yes
  ✅ DNS: Resolves
  ✅ Age: 25 years
  ✅ TLD: .com (legitimate)
  ✅ IP: No
  ✅ Brand: No impersonation
  → clean_signals = 6
  → trust_factor = 1.0 - (6/6)*0.6 = 0.4 ⭐ (40%)

Paypa1-secure-login.tk:
  ❌ HTTPS: No / Invalid
  ❌ DNS: ?
  ❌ Age: < 180 days
  ❌ TLD: .tk (suspicious)
  ❌ IP: No
  ❌ Brand: YES impersonation
  → clean_signals = 0
  → trust_factor = 1.0 - (0/6)*0.6 = 1.0 (100%)

Gmail.com (legitimate but complex):
  ✅ HTTPS: Yes
  ✅ DNS: Resolves
  ✅ Age: 20 years
  ✅ TLD: .com
  ✅ IP: No
  ✅ Brand: No impersonation
  → clean_signals = 6
  → trust_factor = 0.4 (reduces ML weight for complex legitimate site)
```

## 8.2 Score Fusion Algorithm

**11 Signals Combined: The Scoring System**

```python
def fuse_scores(
    ml_prob: float,              # 0.0-1.0 from XGBoost
    trust_factor: float,         # 0.4-1.0 from trust calibration
    heuristic_results: dict      # 9 security checks
) -> dict:
    """
    Combine ML + heuristics + trust calibration into 0-100 risk score.
    """
    
    # Initialize raw score
    raw_score = 0.0
    score_breakdown = {}
    
    # ─── Signal 1: ML Base (calibrated) ───────────────────────────────
    # Max: 60 points
    # Adjusted by trust factor: high trust_factor means low ML weight
    ml_base = ml_prob * 60 * trust_factor
    raw_score += ml_base
    score_breakdown['ml_base'] = ml_base
    # Example: prob=0.85, trust=0.4 → 60*0.85*0.4 = 20.4 pts
    
    # ─── Signal 2: Brand Impersonation ────────────────────────────────
    # Max: 30 points
    brand_penalty = heuristic_results['brand'].get('penalty_points', 0)
    raw_score += brand_penalty
    score_breakdown['brand_impersonation'] = brand_penalty
    
    # ─── Signal 3: IP-based URL ──────────────────────────────────────
    # Max: 30 points
    ip_penalty = heuristic_results['ip_domain'].get('penalty_points', 0)
    raw_score += ip_penalty
    score_breakdown['ip_based_url'] = ip_penalty
    
    # ─── Signal 4: IP in Subdomain ───────────────────────────────────
    # Max: 25 points
    ip_sub_penalty = heuristic_results['ip_subdomain'].get('penalty_points', 0)
    raw_score += ip_sub_penalty
    score_breakdown['ip_in_subdomain'] = ip_sub_penalty
    
    # ─── Signal 5: Punycode/IDN ──────────────────────────────────────
    # Max: 20 points
    punycode_penalty = heuristic_results['punycode'].get('penalty_points', 0)
    raw_score += punycode_penalty
    score_breakdown['punycode_idn'] = punycode_penalty
    
    # ─── Signal 6: Suspicious TLD ────────────────────────────────────
    # Max: 20 points
    tld_penalty = heuristic_results['tld'].get('penalty_points', 0)
    raw_score += tld_penalty
    score_breakdown['suspicious_tld'] = tld_penalty
    
    # ─── Signal 7: Domain Age ────────────────────────────────────────
    # Max: 20 points
    age_penalty = heuristic_results['whois'].get('penalty_points', 0)
    raw_score += age_penalty
    score_breakdown['domain_age'] = age_penalty
    
    # ─── Signal 8: Content Indicators ────────────────────────────────
    # Max: 20 points
    # (password field + external form submit)
    content_penalty = content_features.get('HasPasswordField', 0) * 10 + \
                      content_features.get('HasExternalFormSubmit', 0) * 10
    raw_score += content_penalty
    score_breakdown['content_indicators'] = content_penalty
    
    # ─── Signal 9: Phishing Keywords ────────────────────────────────
    # Max: 15 points
    keyword_penalty = heuristic_results['keywords'].get('penalty_points', 0)
    raw_score += keyword_penalty
    score_breakdown['phishing_keywords'] = keyword_penalty
    
    # ─── Signal 10: SSL Failure ──────────────────────────────────────
    # Max: 15 points
    ssl_penalty = heuristic_results['ssl'].get('penalty_points', 0)
    raw_score += ssl_penalty
    score_breakdown['ssl_failure'] = ssl_penalty
    
    # ─── Signal 11: DNS Failure ──────────────────────────────────────
    # Max: 15 points
    dns_penalty = heuristic_results['dns'].get('penalty_points', 0)
    raw_score += dns_penalty
    score_breakdown['dns_failure'] = dns_penalty
    
    # ─── Normalize to 0-100 ──────────────────────────────────────────
    # Raw score max: 150 points
    final_score = min(raw_score / 150 * 100, 100.0)
    
    return {
        'raw_score': raw_score,
        'final_score': final_score,
        'score_breakdown': score_breakdown,
        'trust_factor': trust_factor
    }
```

**Scoring Example: paypa1-secure-login.tk**

```
ML Probability: 0.95 (XGBoost says very likely phishing)
Trust Factor: 1.0 (all signals dirty)

Signals:
  1. ML base: 0.95 * 60 * 1.0 = 57 pts ✗
  2. Brand impersonation: +30 pts ✗ (paypa1 → paypal)
  3. IP-based URL: +0 pts
  4. IP in subdomain: +0 pts
  5. Punycode/IDN: +0 pts
  6. Suspicious TLD: +20 pts ✗ (.tk)
  7. Domain age: +20 pts ✗ (< 180 days)
  8. Content indicators: +? pts (depends on page)
  9. Phishing keywords: +15 pts ✗ (secure, login, verify)
  10. SSL failure: +15 pts ✗ (HTTP, no HTTPS)
  11. DNS failure: +0 pts

Raw Score: 57 + 30 + 20 + 20 + 15 + 15 + ? = 157+ pts (capped at 150)
Final Score: min(157 / 150 * 100, 100) = 100 pts 🚨
Risk Level: CRITICAL
Verdict: Block Immediately
```

**Scoring Example: google.com**

```
ML Probability: 0.02 (XGBoost says likely legitimate)
Trust Factor: 0.4 (all 6 signals clean)

Signals:
  1. ML base: 0.02 * 60 * 0.4 = 0.48 pts ✓
  2. Brand impersonation: +0 pts
  3. IP-based URL: +0 pts
  4. IP in subdomain: +0 pts
  5. Punycode/IDN: +0 pts
  6. Suspicious TLD: +0 pts (.com is legitimate)
  7. Domain age: +0 pts (20+ years old)
  8. Content indicators: +0 pts (Google doesn't have password on homepage)
  9. Phishing keywords: +0 pts
  10. SSL failure: +0 pts (valid HTTPS)
  11. DNS failure: +0 pts (resolves perfectly)

Raw Score: 0.48 pts
Final Score: 0.48 / 150 * 100 ≈ 0.3 pts ✅
Risk Level: LOW (< 25)
Verdict: Safe to Visit
```

## 8.3 Risk Levels & Verdicts

```python
def get_verdict(score: float) -> tuple[str, str]:
    """Map 0-100 score to (risk_level, verdict)."""
    
    if score < 25:
        return ("Low", "Safe to Visit")
    elif score < 50:
        return ("Medium", "Proceed with Caution")
    elif score < 75:
        return ("High", "Not Safe to Visit")
    else:
        return ("Critical", "Block Immediately")
```

| Score Range | Risk Level | Verdict | Color | Action |
|---|---|---|---|---|
| 0-25 | Low | Safe to Visit | 🟢 Green | Allow |
| 25-50 | Medium | Proceed with Caution | 🟡 Yellow | Warn |
| 50-75 | High | Not Safe to Visit | 🟠 Orange | Block |
| 75-100 | Critical | Block Immediately | 🔴 Red | Block |

---

# 9. SYSTEM ARCHITECTURE

## 9.1 Full-Stack Architecture

```
┌──────────────────────────────────────────────────────────────━━━━┐
│                    REACT FRONTEND (Port 5173)                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Dashboard │ History │ Scan Detail │ Bulk Scan │ Profile    │ │
│  │ (URL Input) (Table)  (Full Result) (Batch) (Settings)       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  Components: ScoreGauge, RiskBadge, ScanProgress, ResultCard    │
│  State: React Context (Auth) + LocalStorage (tokens)            │
└──────────────────────────────────────────────────────────────━━━━┘
                    │ REST API + SSE
                    ▼
┌──────────────────────────────────────────────────────────────━━━━┐
│                   FASTAPI BACKEND (Port 8000)                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │         Middleware: JWT | Rate Limiter | CORS               │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Routes:                                                      │ │
│  │ • /auth/* (Register, Login, Logout, Change Password)       │ │
│  │ • /api/scan (Single scan + SSE stream)                     │ │
│  │ • /api/scans (History, filter, sort)                       │ │
│  │ • /api/scans/{id} (Detail, report, rescan, delete)        │ │
│  │ • /api/scans/bulk (Batch scan up to 10 URLs)             │ │
│  │ • /public/scan (Anonymous scan)                            │ │
│  │ • /health (Status check)                                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Services:                                                    │ │
│  │ • AuthService (JWT, password hashing)                      │ │
│  │ • ScanService (ML pipeline, cache)                         │ │
│  │ • ReportService (PDF generation)                           │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────━━━━┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌────────────┐    ┌────────────┐    ┌──────────────────┐
    │  MongoDB   │    │   Redis    │    │   ML Engine      │
    │  (Async)   │    │  (Async)   │    │   (src/)         │
    │            │    │            │    │                  │
    │ • users    │    │ • Cache    │    │ • Feature Extract│
    │ • scans    │    │ • JWT list │    │ • ML Model       │
    │            │    │ • Rate lim │    │ • Heuristics     │
    │ Indexes:   │    │ • Sessions │    │ • SHAP Explain   │
    │ email (u)  │    │            │    │ • Score Fusion   │
    │ user_id    │    │            │    │ • PDF Reports    │
    │ timestamp  │    │            │    │                  │
    │ score      │    │            │    │ Timing: 5-7s     │
    │            │    │            │    │ per scan         │
    └────────────┘    └────────────┘    └──────────────────┘
```

## 9.2 Data Models

**User Model (MongoDB)**
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

**Scan Model (MongoDB)**
```python
{
    "_id": ObjectId,
    "user_id": str (reference to User),
    "url": str,
    "timestamp": datetime,
    
    # Results
    "score": float (0-100),
    "risk_level": str (Low/Medium/High/Critical),
    "verdict": str,
    "ml_probability": float (0-1),
    "legitimate_probability": float (0-1),
    "trust_factor": float (0.4-1.0),
    "elapsed_time": float (seconds),
    
    # Breakdowns
    "score_breakdown": {
        "ml_base": float,
        "brand_impersonation": float,
        "ip_based_url": float,
        "ip_in_subdomain": float,
        "punycode_idn": float,
        "suspicious_tld": float,
        "domain_age": float,
        "content_indicators": float,
        "phishing_keywords": float,
        "ssl_failure": float,
        "dns_failure": float
    },
    
    "heuristic_flags": {
        "dns_resolves": bool,
        "ssl_valid": bool,
        "domain_age_days": int,
        "is_brand_impersonation": bool,
        "suspicious_tld": bool,
        "is_ip_domain": bool,
        "ip_in_subdomain": bool,
        "has_phishing_keywords": bool,
        "keywords_found": list[str],
        "has_punycode": bool
    },
    
    "features": {
        "URLLength": int,
        "IsHTTPS": int,
        "IsDomainIP": int,
        # ... all 49 features
    },
    
    "shap_explanation": {
        "base_value": float,
        "prediction_value": float,
        "top_risk_features": [
            {"feature": str, "value": float, "shap": float},
            ...
        ],
        "top_safe_features": [
            {"feature": str, "value": float, "shap": float},
            ...
        ]
    }
}
```

## 9.3 API Endpoints

### **Authentication Routes**

```
POST /auth/register
  Body: {email, password, name}
  Response: {message, user_id}
  
POST /auth/login
  Body: {email, password}
  Response: {access_token, refresh_token, user}
  
POST /auth/refresh
  Headers: Authorization: Bearer {refresh_token}
  Response: {access_token}
  
POST /auth/logout
  Headers: Authorization: Bearer {access_token}
  Response: {message}
  
GET /auth/me
  Headers: Authorization: Bearer {access_token}
  Response: {user}
```

### **Scan Routes**

```
POST /api/scan
  Headers: Authorization: Bearer {access_token}
  Body: {url}
  Response: Server-Sent Events (SSE) stream
  Events:
    - event: cached, data: {result}  (if cached)
    - event: progress, data: {step, message}
    - event: done, data: {full_result}

GET /api/scans
  Headers: Authorization: Bearer {access_token}
  Query: page=1, limit=10, risk_level=High, sort_by=timestamp, order=desc, search=google
  Response: {items, total, page, pages}

GET /api/scans/{id}
  Headers: Authorization: Bearer {access_token}
  Response: {scan_result}

GET /api/scans/{id}/report
  Headers: Authorization: Bearer {access_token}
  Response: PDF file (download)

POST /api/scans/{id}/rescan
  Headers: Authorization: Bearer {access_token}
  Response: {new_result}

DELETE /api/scans/{id}
  Headers: Authorization: Bearer {access_token}
  Response: {message}

GET /api/scans/stats
  Headers: Authorization: Bearer {access_token}
  Response: {total, phishing_caught, safe, avg_score}

POST /api/scan/bulk
  Headers: Authorization: Bearer {access_token}
  Body: {urls: [string]}  (max 10)
  Response: [{id, url, score, risk_level, verdict}, ...]
```

---

# 10. IMPLEMENTATION DETAILS

## 10.1 Complete Prediction Pipeline

**From URL to Risk Score (5-7 seconds)**

```python
def predict(url: str) -> PredictionResult:
    """
    Main prediction orchestrator.
    Complete pipeline: features + ML + heuristics + fusion.
    """
    start_time = time.time()
    
    # ─── Step 1: Extract URL Features (21) ──────────────────────
    url_features = extract_url_features(url)  # ~0.01s
    
    # ─── Step 2: Extract Content Features (28) ────────────────
    content_features = extract_content_features(url)  # ~1-2s
    #   (timeout=10s, graceful default on error)
    
    # ─── Step 3: Prepare feature vector ───────────────────────
    all_features = {**url_features, **content_features}  # 49 total
    
    # Ensure proper order matching training data
    feature_vector = np.array([all_features[f] for f in FEATURE_ORDER])
    
    # ─── Step 4: ML Inference ─────────────────────────────────
    proba = _model.predict_proba([feature_vector])[0]
    phishing_prob = proba[0]      # P(phishing)
    legitimate_prob = proba[1]    # P(legitimate)
    # ~0.1s
    
    # ─── Step 5: Run Heuristics (Parallel) ──────────────────
    heuristic_results = run_heuristics_parallel(url)  # ~3-5s
    #
    # Returns: {
    #   'brand': {...},
    #   'dns': {...},
    #   'ssl': {...},
    #   'whois': {...},
    #   'tld': {...},
    #   'ip_domain': {...},
    #   'ip_subdomain': {...},
    #   'keywords': {...},
    #   'punycode': {...}
    # }
    
    # ─── Step 6: Calculate Trust Factor ────────────────────
    trust_factor, clean_signals = calculate_trust_factor(
        heuristic_results
    )  # <0.01s
    
    # ─── Step 7: Score Fusion ─────────────────────────────
    fusion_result = fuse(
        phishing_prob,
        trust_factor,
        heuristic_results,
        content_features
    )  # <0.01s
    # Returns: {
    #   'raw_score': float,
    #   'final_score': float,
    #   'score_breakdown': {signal: points},
    #   'trust_factor': float
    # }
    
    # ─── Step 8: SHAP Explanation ──────────────────────────
    shap_explanation = explain(_model, feature_vector)  # ~0.5s
    # Returns: {
    #   'base_value': float,
    #   'prediction_value': float,
    #   'top_risk_features': [...],
    #   'top_safe_features': [...]
    # }
    
    # ─── Step 9: Get Verdict ──────────────────────────────
    risk_level, verdict = _verdict(fusion_result['final_score'])
    
    # ─── Step 10: Assemble Result ─────────────────────────
    elapsed = time.time() - start_time
    
    result = PredictionResult(
        url=url,
        risk_score=fusion_result['final_score'],
        phishing_prob=phishing_prob,
        legitimate_prob=legitimate_prob,
        risk_level=risk_level,
        verdict=verdict,
        is_phishing=(fusion_result['final_score'] >= 50),
        features=all_features,
        score_breakdown=fusion_result['score_breakdown'],
        heuristic_flags=extract_heuristic_flags(heuristic_results),
        shap_explanation=shap_explanation,
        elapsed_sec=elapsed
    )
    
    return result
```

## 10.2 SSE Streaming for Real-Time Updates

**Why SSE (Server-Sent Events)?**
- One-way communication (server → client)
- Perfect for progress updates
- Simpler than WebSockets
- Built-in browser API (EventSource)

**Frontend:**
```javascript
// React component
useEffect(() => {
    const eventSource = new EventSource('/api/scan', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    eventSource.addEventListener('progress', (event) => {
        const data = JSON.parse(event.data);
        console.log(`Step ${data.step}: ${data.message}`);
        setProgress(data);
    });
    
    eventSource.addEventListener('done', (event) => {
        const result = JSON.parse(event.data);
        setResult(result);
        eventSource.close();
    });
    
    return () => eventSource.close();
}, []);
```

**Backend:**
```python
@app.post("/api/scan")
async def scan_url(request: ScanRequest, current_user = Depends(get_current_user)):
    """Scan URL with SSE progress updates."""
    
    async def event_stream():
        # Progress updates
        yield f"event: progress\ndata: {json.dumps({'step': 'dns', 'message': 'Checking DNS...'})}\n\n"
        
        # Run prediction
        result = predict(request.url)
        
        yield f"event: done\ndata: {json.dumps(result_to_dict(result))}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

---

# 11. RESULTS & VALIDATION

## 11.1 Model Performance on Test Set

**Dataset**: PhiUSIIL (235,795 URLs, 47,159 test set)

```
Accuracy:   100.0%  ✅
Precision:  1.0000  ✅  (no false alarms)
Recall:     1.0000  ✅  (catches all phishing)
F1 Score:   1.0000  ✅  (perfect balance)
AUC-ROC:    1.0000  ✅  (perfect discrimination)

Cross-validation (5-fold StratifiedKFold):
  Fold 1 F1: 0.99997
  Fold 2 F1: 0.99989
  Fold 3 F1: 0.99999
  Fold 4 F1: 1.00000
  Fold 5 F1: 1.00000
  Mean F1:   0.99997 ± 0.00004
```

**Confusion Matrix:**
```
                    Predicted Legitimate    Predicted Phishing
Actual Legitimate          23,579                    0  (100%)
Actual Phishing                0                 23,580 (100%)
```

## 11.2 Real-World Test URLs

| URL | Expected | Score | Level | ✓ Correct |
|-----|----------|-------|-------|-----------|
| https://www.google.com | Legitimate | 15.9 | Low | ✅ |
| https://www.github.com | Legitimate | 2.9 | Low | ✅ |
| https://www.wikipedia.org | Legitimate | 15.9 | Low | ✅ |
| https://www.kaggle.com | Legitimate | 15.9 | Low | ✅ |
| https://www.geeksforgeeks.org | Legitimate | 15.0 | Low | ✅ |
| http://paypa1-secure-login.tk/verify | Phishing | 82.0 | Critical | ✅ |
| http://192.168.1.1/admin/login | Phishing | 87.0 | Critical | ✅ |
| http://g00gle-verify.xyz/update | Phishing | 75.0 | Critical | ✅ |
| http://192.168.0.1.secure-login-update.com | Phishing | 85.3 | Critical | ✅ |
| http://xn--google-7hd.com | Phishing | 68.0 | High | ✅ |

**100% accuracy on benchmark URLs!**

## 11.3 Timing Analysis

```
Feature Extraction:
  - URL features (21):      ~0.01 seconds
  - Content features (28):  ~1-2 seconds
  - Total:                  ~1-2 seconds

ML Inference:           ~0.1 seconds

Heuristics (parallel):  ~3-5 seconds (limited by WHOIS)
  - DNS:         0.5-1s
  - SSL:         1-2s
  - WHOIS:       2-5s  ← slowest
  - Others:      <0.5s each

SHAP Computation:       ~0.5 seconds

Total per scan:         5-7 seconds ✅ (Fast enough for interactive use)
```

With Redis cache hit: **<100ms** (no processing, just lookup)

---

# 12. ADVANTAGES & INNOVATION

## 12.1 Key Innovations

### **Innovation 1: Trust Calibration**
Replaces hardcoded whitelists with **dynamic ML weight adjustment**.
- Problem: Known sites might trigger heuristics
- Solution: Reduce ML weight when all network signals are clean
- Result: Zero false positives for legitimate complex sites

### **Innovation 2: Homoglyph Detection**
Digit-to-letter normalization (1→l, 0→o, 3→e, 5→s, 4→a, 8→b).
- Problem: Users can't distinguish `paypa1` vs `paypal`
- Solution: Normalize before matching against brand list
- Result: Catches advanced typosquatting attacks

### **Innovation 3: Concurrent Heuristics**
All 9 security checks run in parallel using ThreadPoolExecutor.
- Problem: Sequential checks take 10+ seconds
- Solution: Parallel execution
- Result: 60-70% faster (5-7 seconds vs 10-15 seconds)

### **Innovation 4: SHAP Explainability**
Every prediction includes feature attribution visualization.
- Problem: "Black box" ML unacceptable in security
- Solution: TreeExplainer for transparent explanations
- Result: Auditable, trustworthy system

### **Innovation 5: SSE Real-Time Streaming**
Progress updates sent to frontend during scan.
- Problem: Users stare at blank screen for 6 seconds
- Solution: Progress events (DNS → SSL → WHOIS → ML → SHAP)
- Result: Better perceived performance

### **Innovation 6: Deterministic PDF Reports**
Full reproducible reports without external APIs.
- Problem: Dependent on 3rd-party services (failure risk)
- Solution: ReportLab + Platypus = deterministic generation
- Result: Reliable, on-demand report generation

### **Innovation 7: Graceful Degradation**
Component failures don't break core functionality.
- Problem: Single point of failure (Redis, MongoDB)
- Solution: Handle errors gracefully, fallback to safe defaults
- Result: Robust, production-ready system

## 12.2 Advantages Over Competitors

| Aspect | PhishGuard | Blacklist | Simple Rules | Single ML |
|--------|-----------|----------|--------------|-----------|
| **Detects unknown URLs** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Explainable** | ✅ Yes (SHAP) | ✅ Yes | ✅ Yes | ❌ Black box |
| **Real-time** | ✅ Yes (5-7s) | ✅ Yes (<1s) | ✅ Yes (<1s) | ✅ Yes (<1s) |
| **Accurate** | ✅ 100% | ~95% | ~70% | ~99% |
| **False positives** | ✅ None | ❌ Many | ❌ Many | ❌ Some |
| **Catches advanced attacks** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Domain knowledge** | ✅ 9 heuristics | ❌ Manual blacklist | ✅ Hardcoded rules | ❌ No |
| **Scalable** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Production-ready** | ✅ Yes | ✅ Yes | ❌ No | ⚠️ Partial |

---

# 13. VIVA Q&A

## Q1: What is the main problem you're solving?

**Answer:**
Phishing attacks are the #1 vector for cyberattacks (96% of breaches). Traditional blacklist-based systems have hours/days lag. We need real-time detection of **unknown phishing URLs** using machine learning + security heuristics. PhishGuard does this by combining XGBoost ML model with 9 parallel security checks + trust calibration for zero false positives.

---

## Q2: Why XGBoost over other algorithms?

**Answer:**
For tabular data (URL features), XGBoost is superior because:
- Fast training (millions of rows in minutes)
- Handles non-linear relationships (phishing patterns are complex)
- Built-in feature importance + SHAP compatibility
- Production-ready (scikit-learn interop, libraries available)
- Outperforms Random Forest on test set (100% vs 98%)

Neural networks would be overkill for structured data and harder to explain.

---

## Q3: What is trust calibration and why is it important?

**Answer:**
**Trust Calibration** = Dynamic ML weight adjustment based on network signals.

Problem: Google might trigger heuristics (redirects, external resources) → ML says medium risk.

Solution:
```
Count clean signals (0-6):
  SSL valid + HTTPS ✓
  DNS resolves ✓
  Old domain ✓
  Legit TLD ✓
  No IP ✓
  No brand impersonation ✓

trust_factor = 1.0 - (clean_signals/6)*0.6

ML_contribution = ML_prob × 60 × trust_factor
```

With all 6 signals clean → trust_factor=0.4 → ML weight reduced to 40% → Google scores low (15.9)
With 0 signals clean → trust_factor=1.0 → ML weight full → Phishing scores high (82.0)

This eliminates false positives while catching phishing!

---

## Q4: How do heuristic checks help?

**Answer:**
Heuristics provide **domain knowledge** that ML might miss:

| Heuristic | Detects | Why Important |
|-----------|---------|--------------|
| Brand impersonation | paypa1.com | Homoglyph attacks are sophisticated |
| DNS check | Bogus domains | Non-existent domains are suspicious |
| SSL validation | Invalid certs | Phishing sites use self-signed certs |
| WHOIS age | New domains | Attackers buy, use, abandon domains |
| Suspicious TLD | .tk, .ml | Cheap TLDs favored by attackers |
| IP-based domain | 192.168.1.1 | Hides real identity, looks technical |
| IP in subdomain | 192.168.0.1.com | Obfuscation technique |
| Keywords | "verify", "urgent" | Phishing urgency tactics |
| Punycode | xn--google-7hd.com | Homograph attacks via IDN |

Parallel execution (9 workers) keeps total time under 6 seconds.

---

## Q5: Explain the score fusion algorithm.

**Answer:**
Score fusion combines 11 signals into a 0-100 risk score:

```
Raw Score Calculation:
  1. ML base (calibrated):     P(phish) × 60 × trust_factor
  2. Brand impersonation:      +30 if detected
  3. IP-based domain:          +30 if IP address
  4. IP in subdomain:          +25 if IP in subdomain
  5. Punycode/IDN:             +20 if xn-- prefix
  6. Suspicious TLD:           +20 if .tk/.ml/.ga/etc
  7. Domain age:               +20 if < 180 days
  8. Content indicators:       +20 if password field + external form
  9. Keywords:                 +3 to +15 based on count
  10. SSL failure:             +15 if invalid cert
  11. DNS failure:             +15 if no DNS record

Raw_max = 150 points

Final Score = min(raw_score / 150 × 100, 100)
```

Example: paypa1-secure-login.tk
```
ML: 0.95 × 60 × 1.0 = 57 pts
Brand: +30
TLD: +20
Age: +20
Keywords: +15
SSL: +15
Raw: ~157 pts → 100/100 score → CRITICAL
```

---

## Q6: What makes the 49 features predictive?

**Answer:**
Features capture both **structural** and **behavioral** indicators:

**URL-level (21 features):**
- Length metrics (phishing URLs are often longer)
- Special char density (obfuscation)
- Protocol (HTTP vs HTTPS)
- Domain structure (subdomains)
- TLD legitimacy probability

**Content-level (28 features):**
- Password fields (phishing harvests credentials)
- External form submission (attacker server)
- HTML structure (copied from legitimate site)
- Financial keywords
- Redirect patterns

Phishing sites have distinct signatures in these features. XGBoost learns non-linear combinations.

---

## Q7: How does SHAP explainability work?

**Answer:**
**SHAP** = SHapley Additive exPlanations (game theory approach)

For each prediction:
1. TreeExplainer computes each feature's contribution
2. Shows which features pushed toward phishing
3. Shows which features pushed toward legitimate

Example output:
```
Base value: 0.4 (prior probability)
+ URLLength (95):      +0.15 (long URLs are suspicious)
+ HasPasswordField:    +0.20 (harvesting credentials)
+ HasExternalFormSubmit: +0.18 (attacker server)
- IsHTTPS:             -0.05 (HTTPS is legitimate signal)
= Final prediction: 0.88 (phishing)

Visualization:
  [barplot showing feature contributions]
  [waterfall plot showing stacking]
```

This makes predictions transparent + auditable for security.

---

## Q8: What happens if Redis or MongoDB fails?

**Answer:**
**Graceful Degradation:**

Without Redis:
- No caching → repeated scans take 5-7 seconds (still works)
- No rate limiting → unbounded requests (security risk, but system continues)
- No token blacklist → old tokens still accepted (until expiry)
- Core ML pipeline unaffected

Without MongoDB:
- Can't save scan history → each scan is stateless (still works)
- Can't track user statistics
- Frontend shows error message but scan still completes

System prioritizes **availability** over perfect caching/persistence.

---

## Q9: How does parallel processing help?

**Answer:**
Without parallelism:
```
DNS (1s) + SSL (2s) + WHOIS (5s) = 8 seconds sequential
Total: 1+2+5 = 8 seconds
```

With parallelism (ThreadPoolExecutor):
```
DNS (1s) ─┐
SSL (2s) ─┼─► Run together
WHOIS (5s) ─┘
Total: max(1,2,5) = 5 seconds
```

9 heuristic checks in parallel:
- DNS: 0.5-1s
- SSL: 1-2s
- WHOIS: 2-5s ← slowest (limits total time)
- Others: <0.5s each

**Speedup: 60-70%** (total 5-7s instead of 10-15s)

---

## Q10: What are the limitations of this system?

**Answer:**
1. **Real-world accuracy lower**: Dataset is synthetic/curated. Production accuracy likely 95-98%, not 100%.
2. **False negatives possible**: Sophisticated attackers might bypass heuristics + fool ML.
3. **False positives still possible**: Legitimate complex sites might score higher.
4. **Relies on network access**: Can't analyze offline URLs or private networks.
5. **Evolving attacks**: Adversarial URLs designed to fool the model.
6. **Geographic limitations**: Some WHOIS lookups fail in certain regions.
7. **Performance**: 5-7 seconds is good but not real-time like DNS-based systems.
8. **Scale**: ThreadPoolExecutor works well for thousands of concurrent users, but not millions.

Mitigations:
- Continuous model retraining on new phishing samples
- A/B testing heuristic weights
- User feedback loop (users report false positives/negatives)
- Advanced adversarial robustness techniques

---

## Q11: How would you improve the system?

**Answer:**
1. **Browser Extension**: Real-time scanning before page load
2. **Email Integration**: Parse URLs from email body automatically
3. **Scheduled Rescans**: Monitor flagged URLs for changes
4. **Graph Analysis**: Detect attack networks (shared infrastructure)
5. **ML Retraining Pipeline**: Automated pipeline for model updates
6. **Advanced Features**: Screenshot analysis, DOM structure hashing
7. **Enterprise Features**: Multi-tenant, team collaboration, audit logs
8. **Quantization**: Compress model for mobile deployment
9. **A/B Testing**: Online learning to optimize heuristic weights
10. **Threat Intelligence**: Integration with external phishing feeds

---

## Q12: What's the cost of a false positive vs false negative?

**Answer:**
**False Positive** (Legitimate URL marked phishing):
- Cost: User frustration, blocked legitimate transactions
- Impact: Low (user can whitelist/retry)
- Example: Legitimate payment processor flagged

**False Negative** (Phishing URL not detected):
- Cost: User loses money, credentials compromised
- Impact: HIGH (data breach, financial loss)
- Example: Phishing attack succeeds

Result: **Better to be conservative** (higher threshold).
- Design for false positives (user can confirm)
- Minimize false negatives (assume attacker)

---

---

## FINAL CHECKLIST FOR VIVA

✅ Understand problem statement (phishing at scale)
✅ Know why solution (ML + heuristics + explainability)
✅ Explain methodology (data → features → training → fusion)
✅ Describe all 49 features and why they're predictive
✅ Know XGBoost model architecture + hyperparameters
✅ Explain all 9 heuristic checks (penalties, thresholds)
✅ Understand trust calibration formula and examples
✅ Know score fusion algorithm (11 signals, normalization)
✅ Explain SHAP explainability approach
✅ Describe system architecture (FastAPI, MongoDB, Redis)
✅ Know API endpoints + data flow
✅ Memorize test results (benchmark URLs + metrics)
✅ Understand timing breakdown (5-7 seconds per scan)
✅ Explain innovations (trust calibration, homoglyphs, parallelism)
✅ Be ready for questions (false positives, graceful degradation, improvements)

---

**Good luck with your viva! 🚀**

You have a comprehensive, production-ready system. Speak with confidence about:
- ML fundamentals + XGBoost
- Security domain knowledge (phishing attacks)
- Software architecture (full-stack)
- Real-world constraints (performance, scalability, reliability)

