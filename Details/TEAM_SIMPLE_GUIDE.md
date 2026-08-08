# PhishGuard - Simple Team Guide for 4 People

---

# THE BIG PICTURE FIRST

Imagine you're building a **security guard robot** that checks if URLs (web addresses) are fake or real.

**The Robot Has 4 Jobs:**

```
1. TALKING TO USERS (Frontend)     → Person 1 does this
   "Hi! Please give me a URL to check"
   
2. THINKING & DECIDING (Backend)   → Person 2 does this
   "Okay, let me check this URL and decide if it's safe"
   
3. BRAIN & KNOWLEDGE (ML)          → Person 3 does this
   "I use my AI brain + security knowledge to decide"
   
4. INSTRUCTION MANUAL (Documentation) → Person 4 does this
   "Here's how to use the robot and how it works"
```

---

# 👤 PERSON 1: FRONTEND DEVELOPER

## Your Job (In Plain English)
You are building **what users see on their screen**. It's like designing the control panel that people use to interact with the security robot.

## What You Create

### 1. **Login Page**
Users enter their email and password here.
- "I am John, my email is john@gmail.com, password is abc123"
- You save their login info safely

### 2. **Dashboard Page** (Main Page)
This is the home page where users check URLs.
- User pastes URL: `https://paypal.com` (is it real PayPal or fake?)
- User clicks "Check URL"
- A progress bar appears: "Checking DNS..." → "Checking SSL..." → "Checking Brand..."
- After 5-7 seconds, it shows: **"Score: 82 - DANGER! This is likely FAKE"**

Example:
```
┌─────────────────────────────────────┐
│ PhishGuard URL Checker              │
├─────────────────────────────────────┤
│                                     │
│ Paste URL here: [_____________]    │
│                 [Check URL]         │
│                                     │
│ ████████░░░░░░░░░░░░░░░░░░░░░░  60% │
│ Current Step: Checking Brand...    │
│                                     │
└─────────────────────────────────────┘
```

### 3. **History Page**
Shows all URLs the user has checked before.
- Day 1: Checked google.com → Safe
- Day 2: Checked paypa1-secure.tk → DANGER
- Day 3: Checked facebook.com → Safe

User can:
- Sort by date (newest first or oldest first)
- Filter by result (show only "DANGER" results or "Safe" results)
- Search for a URL ("show me results about PayPal")

### 4. **Detail Page**
When user clicks on an old result, they see EVERYTHING about it:
- Score: 82/100
- Risk Level: CRITICAL
- Why it's dangerous:
  - ❌ Uses suspicious TLD (.tk)
  - ❌ Looks like PayPal (brand impersonation)
  - ❌ Has phishing keywords ("verify", "login", "secure")
  - ✅ DNS resolves (got some points for this)
- A colored gauge showing the risk
- Charts showing which features made it risky
- Download a PDF report

### 5. **Bulk Scan Page**
Users can check 10 URLs at once (instead of one at a time).

Example:
```
Paste multiple URLs (one per line):

google.com
github.com
paypa1-secure-login.tk

[Check All URLs]

Results:
├─ google.com → Safe (15.9)
├─ github.com → Safe (2.9)
└─ paypa1-secure-login.tk → DANGER (82.0)
```

### 6. **Profile Page**
User settings:
- View my email: john@gmail.com
- Change my password
- Delete my account

### 7. **Beautiful Components** (Building Blocks)

You create reusable pieces:

**ScoreGauge** → A circle that fills up like a gas gauge
```
    ┌─────────┐
    │    82   │  ← Score inside circle
    │ ◐◀─────◉│  ← Red color = DANGER
    └─────────┘
```

**RiskBadge** → A colored label
```
CRITICAL (Red)    HIGH (Orange)    MEDIUM (Yellow)    LOW (Green)
```

**ScanProgress** → Progress bar showing what's happening
```
████████░░░░░░░░░░░░ 40%
Currently checking: Domain Age
```

**ResultCard** → A box showing one result
```
┌──────────────────────────┐
│ URL: paypal.fake.tk      │
│ Score: 82/100 (CRITICAL) │
│ Time: 2024-01-15 10:30am │
│ [View Details] [Delete]  │
└──────────────────────────┘
```

## Technologies You Use
- **React**: A tool to build interactive websites
- **JavaScript**: The programming language for websites
- **Tailwind CSS**: Makes things look pretty (colors, spacing, etc.)
- **Axios**: Sends requests to the backend ("Hey backend, check this URL!")

## How Many Files You Create
Approximately **15-20 files** totaling **2,000-3,000 lines of code**

## Example: What You Actually Write

Here's a simple example of one page:

```javascript
// Dashboard.jsx - The main page

import React, { useState } from 'react';
import axios from 'axios';

export default function Dashboard() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // When user clicks "Check URL"
  const handleScan = async () => {
    setIsLoading(true);
    
    try {
      // Send URL to backend
      const response = await axios.post('/api/scan', {
        url: url
      });
      
      // Show result
      setResult(response.data);
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1>PhishGuard - Check if URLs are Safe</h1>
      
      {/* Input field */}
      <input 
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Paste URL here..."
      />
      
      {/* Check button */}
      <button onClick={handleScan} disabled={isLoading}>
        {isLoading ? 'Checking...' : 'Check URL'}
      </button>
      
      {/* Show result */}
      {result && (
        <div>
          <h2>Score: {result.score}/100</h2>
          <p>Risk Level: {result.risk_level}</p>
          <p>Verdict: {result.verdict}</p>
        </div>
      )}
    </div>
  );
}
```

## Your Checklist (What You Need to Do)

- ✅ Create Login page (email + password form)
- ✅ Create Register page (sign up form)
- ✅ Create Dashboard page (main URL input)
- ✅ Create History page (see past checks)
- ✅ Create Detail page (see full result of one check)
- ✅ Create Bulk Scan page (check 10 URLs at once)
- ✅ Create Profile page (user settings)
- ✅ Create ScoreGauge component (circle gauge)
- ✅ Create RiskBadge component (colored label)
- ✅ Create ScanProgress component (progress bar)
- ✅ Create Navbar component (top navigation bar)
- ✅ Create authentication system (login/logout)
- ✅ Create API client (send requests to backend)
- ✅ Make it look nice with Tailwind CSS
- ✅ Make sure it works on phone (responsive design)

---

# 👤 PERSON 2: BACKEND DEVELOPER

## Your Job (In Plain English)
You are building **the brain of the robot**. You receive requests from the website (Person 1), process them, and send back answers. It's like being the manager who coordinates everything.

## What You Create

### 1. **Authentication System** (Login/Logout)

When user tries to login:

**Flow:**
```
User submits: email=john@gmail.com, password=abc123

Your code:
├─ Check if this email exists in database
├─ If yes: Check if password is correct
├─ If correct: Create a special token (like a secret key)
│  TOKEN = "abc123xyz789..." (very long random string)
├─ Send token back to user
└─ User holds this token to prove they are John

Every time user does something:
├─ User sends token: "abc123xyz789..."
├─ You check token: "Yes, this is John"
└─ Allow them to continue
```

### 2. **Endpoints** (Things the Website Asks You To Do)

An "endpoint" is like a button the website can press. Each button does something different.

**Example Endpoints:**

```
Button: POST /auth/register
Action: Create a new account
User gives: email, password, name
You return: success or error

Button: POST /auth/login
Action: Log in to account
User gives: email, password
You return: token (proof they are logged in)

Button: POST /api/scan
Action: Check if a URL is safe
User gives: URL they want to check
You:
  ├─ Check if user is logged in (use token)
  ├─ Check if user hasn't scanned too much today (rate limit)
  ├─ Ask Person 3 (ML) to analyze the URL
  ├─ Save result to database
  ├─ Send back: score, risk level, details
  
Button: GET /api/scans
Action: Get list of all URLs user checked before
You return: list of past scans

Button: GET /api/scans/5
Action: Get details of scan number 5
You return: all information about scan 5

Button: DELETE /api/scans/5
Action: Delete scan number 5
You permanently remove it
```

### 3. **Database** (Where You Store Information)

You need to store data in a database (like a filing cabinet).

**What You Store:**

**Users Table:**
```
Email              | Password Hash        | Created Date
john@gmail.com     | $2b$12$abcd...      | 2024-01-01
jane@gmail.com     | $2b$12$efgh...      | 2024-01-02
```

**Scans Table:**
```
ID | User Email | URL | Score | Risk Level | Date | Heuristic Details | ML Features
1  | john@...   | paypal.fake.tk | 82 | CRITICAL | 2024-01-15 | {...} | {...}
2  | john@...   | google.com | 15 | LOW | 2024-01-15 | {...} | {...}
3  | jane@...   | github.com | 3 | LOW | 2024-01-15 | {...} | {...}
```

### 4. **Caching** (Making Things Fast)

If John checks paypal.tk on Monday and again on Tuesday:
- Monday: Takes 6 seconds (Person 3 has to analyze it)
- Tuesday: Should take <1 second (just look up stored result)

You use a tool called **Redis** (like a super-fast mini database):
```
Monday:
├─ John asks: "Is paypal.tk safe?"
├─ Not in cache, so ask Person 3 to analyze
├─ Person 3 takes 6 seconds and gives answer
├─ Save answer in cache: "paypal.tk = score 82"
└─ Tell John: "Score 82"

Tuesday (when John asks again):
├─ Check cache first: "Do I have paypal.tk cached?"
├─ Cache says: "Yes! Score is 82"
└─ Tell John immediately: "Score 82" (no waiting!)
```

### 5. **Rate Limiting** (Prevent Abuse)

Stop users from scanning 1000 URLs in 1 second (that's bad).

```
Rule: Each user can scan maximum 10 URLs per minute

If John scans:
├─ 1st URL: ✅ OK (1 out of 10)
├─ 2nd URL: ✅ OK (2 out of 10)
├─ 3rd URL: ✅ OK (3 out of 10)
├─ ...
├─ 10th URL: ✅ OK (10 out of 10)
└─ 11th URL: ❌ BLOCKED! "You scanned too much. Try again in 60 seconds"
```

### 6. **Sending Results to Website** (Real-Time Updates)

When John clicks "Check URL", he sees real-time progress:

```
Step 1: "Checking DNS..." (0 seconds)
Step 2: "Validating SSL..." (1 second)
Step 3: "Checking Brand..." (2 seconds)
Step 4: "Checking Keywords..." (3 seconds)
Step 5: "Running ML Model..." (4 seconds)
Step 6: "Generating Report..." (6 seconds)
Final: "Done! Score: 82"
```

You send updates to the website in real-time (called SSE - Server-Sent Events).

## Technologies You Use
- **FastAPI**: A tool to create the brain
- **Python**: The programming language
- **MongoDB**: A database to store information
- **Redis**: A super-fast mini-database for caching

## How Many Files You Create
Approximately **10-15 files** totaling **3,000-4,000 lines of code**

## Example: What You Actually Write

```python
# main.py - The main brain file

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer

app = FastAPI()

# When user clicks "Check URL"
@app.post("/api/scan")
async def scan_url(request: ScanRequest, current_user = Depends(get_current_user)):
    """
    This function is called when website sends a scan request
    
    current_user = person's email (if they're logged in)
    request.url = the URL they want to check
    """
    
    # Step 1: Check if user has scanned too much today
    scans_today = count_scans_today(current_user)
    if scans_today >= 10:  # Max 10 per minute
        raise HTTPException(status_code=429, detail="Too many requests")
    
    # Step 2: Check if result already in cache (fast)
    cached = check_redis_cache(request.url)
    if cached:
        return cached_result  # Return instantly!
    
    # Step 3: Ask Person 3 (ML) to analyze URL
    result = predict(request.url)  # Takes 6 seconds
    
    # Step 4: Save result to database
    save_to_mongodb(current_user, result)
    
    # Step 5: Save to cache for next time
    save_to_redis_cache(request.url, result)
    
    # Step 6: Send result back to website
    return result


# When user logs in
@app.post("/auth/login")
async def login(email: str, password: str):
    """
    User submits email and password
    """
    
    # Step 1: Check if email exists in database
    user = find_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Email not found")
    
    # Step 2: Check if password is correct
    if not check_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong password")
    
    # Step 3: Create a token (like a secret key)
    token = create_jwt_token(user.email)
    
    # Step 4: Send token back to website
    return {
        "token": token,
        "user": {"email": user.email, "name": user.name}
    }
```

## Your Checklist (What You Need to Do)

- ✅ Create login endpoint (check email + password)
- ✅ Create register endpoint (create new account)
- ✅ Create logout endpoint (remove token)
- ✅ Create scan endpoint (analyze URL + return result)
- ✅ Create get history endpoint (return list of past scans)
- ✅ Create get detail endpoint (return full details of one scan)
- ✅ Create delete scan endpoint (remove one scan)
- ✅ Create bulk scan endpoint (check 10 URLs at once)
- ✅ Set up MongoDB database
- ✅ Set up Redis caching
- ✅ Implement rate limiting (10 scans/min per user)
- ✅ Implement authentication (JWT tokens)
- ✅ Connect to Person 3's ML code
- ✅ Send real-time updates to website (SSE)
- ✅ Handle errors gracefully

---

# 👤 PERSON 3: ML & HEURISTICS DEVELOPER

## Your Job (In Plain English)
You are building **the AI brain** that actually decides if a URL is safe or dangerous. You combine:
1. **Machine Learning** (AI that learned from examples)
2. **Security Rules** (Things security experts know about phishing)

## What You Create

### 1. **Feature Extraction** (Collecting Clues)

A URL contains many clues. You extract 49 clues from each URL.

**Example Clues:**

```
Looking at: https://paypa1-secure-login.tk/verify?email=user@example.com

CLUE 1: URL Length = 65 characters
  → If URL is very long (>100), it's suspicious
  
CLUE 2: Uses HTTPS = YES (1 point for good)
  → If URL doesn't use HTTPS, it's bad
  
CLUE 3: Domain looks like IP address = NO (0 points)
  → If URL is like http://192.168.1.1, it's suspicious
  
CLUE 4: TLD is .tk = YES (suspicious!)
  → .tk is cheap and often used by attackers
  
CLUE 5: Domain looks like PayPal = YES (homoglyph!)
  → "paypa1" vs "paypal" - looks same but different!
  
CLUE 6: Has password field on page = YES
  → Legitimate paypal.com doesn't ask password on landing page
  
... (43 more clues)
```

**The 49 Clues Are:**
- 21 clues from URL itself (domain length, special characters, etc.)
- 28 clues from the actual webpage (does it have a password field, external form, etc.)

### 2. **Machine Learning Model** (AI Brain)

You train an AI using 235,000 examples of real phishing vs real legitimate URLs.

**How It Works:**

```
Training Phase:
├─ Feed AI: "Here are 100,000 real phishing URLs with their 49 clues"
├─ Feed AI: "Here are 100,000 real legitimate URLs with their 49 clues"
├─ AI learns: "When I see these patterns of clues, it's phishing"
└─ AI learns: "When I see these patterns of clues, it's legitimate"

Testing Phase:
├─ Give AI a NEW URL it never saw before
├─ AI says: "Based on the 49 clues, I'm 85% sure this is PHISHING"
├─ Check if AI is correct... YES! ✅
└─ Do this 47,000 times... AI got them all RIGHT! 😍
```

AI Accuracy: **100% CORRECT** (on test set)

### 3. **9 Security Checks** (Rules from Security Experts)

Even if AI is not 100% sure, you have 9 additional security checks that run at the same time:

**Check 1: Brand Impersonation**
```
Question: Does this URL pretend to be PayPal or Google?

How it works:
├─ Extract domain: "paypa1-secure.tk"
├─ Normalize homoglyphs: "paypa1" → "paypal" (1 looks like l)
├─ Check against brands: ['google', 'paypal', 'amazon', ...]
└─ Result: "YES! This looks like PayPal!" ⚠️ (+30 risk points)
```

**Check 2: DNS Resolution**
```
Question: Does this domain actually exist?

How it works:
├─ Try to resolve: "paypa1-secure.tk"
├─ DNS server says: "I don't know this domain"
└─ Result: "Domain doesn't exist" ⚠️ (+15 risk points)
```

**Check 3: SSL Certificate**
```
Question: Does this website have a valid security certificate?

How it works:
├─ Try to connect via HTTPS
├─ Check if certificate is valid (not expired, right domain, etc.)
├─ If INVALID: ⚠️ (+15 risk points)
└─ If VALID: ✅ (no points)
```

**Check 4: Domain Age**
```
Question: How old is this domain?

How it works:
├─ Look up when domain was registered
├─ If registered < 180 days ago: Suspicious ⚠️ (+20 points)
└─ If registered > 180 days ago: Probably OK ✅
```

**Check 5: Suspicious TLD**
```
Question: Does this use a suspicious top-level domain?

Suspicious TLDs: .tk, .ml, .ga, .cf (these are FREE and often misused)

Result:
├─ URL is paypal.tk → Suspicious TLD ⚠️ (+20 points)
└─ URL is paypal.com → Normal TLD ✅
```

**Check 6: IP-Based Domain**
```
Question: Is the domain actually an IP address?

How it works:
├─ URL is: http://192.168.1.1/admin/
├─ Domain IS an IP address ⚠️ (+30 points)
└─ This is very suspicious!
```

**Check 7: IP in Subdomain**
```
Question: Is there an IP address hidden in the subdomain?

How it works:
├─ URL is: http://192.168.0.1.secure-login.com/
├─ Contains IP address! ⚠️ (+25 points)
└─ This is obfuscation
```

**Check 8: Phishing Keywords**
```
Question: Does the URL contain phishing keywords?

Phishing keywords: "verify", "login", "urgent", "confirm", "secure", 
                  "update", "account", "suspended", etc.

How it works:
├─ URL contains: "verify", "login", "secure"
├─ 3 keywords found ⚠️ (+9 points)
└─ More keywords = more suspicious
```

**Check 9: Punycode Detection**
```
Question: Does this use Punycode (internationalized domain name)?

How it works:
├─ URL is: http://xn--google-7hd.com
├─ Contains "xn--" prefix ⚠️ (+20 points)
└─ This is often used for homograph attacks (looks like google.com to users!)
```

### 4. **Parallel Execution** (Speed Optimization)

All 9 checks run at the same time (not one after another):

```
Without parallelism (slow):
├─ Check 1: 1 second
├─ Check 2: 1 second
├─ Check 3: 2 seconds
├─ Check 4: 5 seconds  ← WHOIS is slowest
├─ Check 5: 0.5 seconds
├─ Check 6: 0.5 seconds
├─ Check 7: 0.5 seconds
├─ Check 8: 0.5 seconds
└─ Check 9: 0.5 seconds
Total: 11 seconds ⏱️

With parallelism (fast):
└─ All 9 checks run TOGETHER
   │← They all start at the same time
   │← They all work on the URL simultaneously
   │← Only wait for the slowest one (5 seconds for WHOIS)
Total: 5 seconds ⏱️  (2x faster!)
```

### 5. **Score Fusion** (Combining Everything)

Now you have:
- AI says: 85% sure it's phishing
- 9 security checks say: +95 risk points

How do you combine these into ONE score (0-100)?

**Formula:**

```
Start with 0 points

Add AI contribution:
├─ AI says 85% phishing
├─ Max AI can contribute: 60 points
└─ AI contribution = 0.85 × 60 = 51 points

Add heuristic contributions:
├─ Brand impersonation: +30 points (if detected)
├─ IP-based domain: +30 points (if detected)
├─ IP in subdomain: +25 points (if detected)
├─ Punycode: +20 points (if detected)
├─ Suspicious TLD: +20 points (if detected)
├─ Domain age: +20 points (if detected)
├─ Content indicators: +20 points (if detected)
├─ Phishing keywords: +15 points (if detected)
├─ SSL failure: +15 points (if detected)
└─ DNS failure: +15 points (if detected)
   (Max from heuristics: 90 points)

Maximum possible raw score: 150 points

Convert to 0-100 scale:
└─ Final Score = (Raw Score / 150) × 100
```

**Example:**
```
URL: paypa1-secure-login.tk/verify

AI says: 0.95 (95% phishing) = 57 points
Brand impersonation: +30 (looks like PayPal)
Suspicious TLD: +20 (.tk)
Domain age: +20 (new domain)
Phishing keywords: +12 (verify, login, secure, login)
SSL failure: +15 (not HTTPS)

Raw = 57 + 30 + 20 + 20 + 12 + 15 = 154 points
Final = (154 / 150) × 100 = 100/100 ← DEFINITELY PHISHING! 🚨
```

### 6. **Trust Calibration** (The Smart Part!)

**Problem:** Sometimes legitimate sites trigger the security checks.

**Example:** Google's homepage might:
- Have redirects (counts against it)
- Have external links (counts against it)
- But it's DEFINITELY legitimate!

**Solution:** If a site is clean in the important ways, trust it more.

```
Count "clean signals":
├─ HTTPS with valid SSL certificate? ✅ +1
├─ DNS resolves? ✅ +1
├─ Old domain (>180 days)? ✅ +1
├─ Legitimate TLD (.com, .org, etc.)? ✅ +1
├─ No IP in domain/subdomain? ✅ +1
└─ No brand impersonation? ✅ +1
   Total: 6 clean signals (best case)

Create trust factor:
└─ trust_factor = 1.0 - (6/6) × 0.6 = 0.4 (40%)

What this means:
└─ Reduce AI's contribution to 40% of max
└─ So legitimate site can't get stuck with high score
```

**Real Example:**
```
google.com:
├─ AI says: "maybe 10% phishing" = 6 points
├─ All 6 signals are clean → trust_factor = 0.4
├─ AI weighted: 6 × 0.4 = 2.4 points
├─ Heuristics add nothing (everything is clean)
├─ Final: 2.4/150 × 100 = 1.6/100 ← SAFE ✅

paypa1-secure-login.tk:
├─ AI says: "95% phishing" = 57 points
├─ All 6 signals are dirty → trust_factor = 1.0
├─ AI weighted: 57 × 1.0 = 57 points
├─ Heuristics add: +30 +20 +20 +12 = +82 points
├─ Final: 139/150 × 100 = 92.6/100 ← DANGER! 🚨
```

### 7. **SHAP Explanation** (Why Did It Decide That?)

For every URL, explain WHY it got that score:

```
For paypa1-secure-login.tk:

Top factors that made it look DANGEROUS:
1. "Brand looks like: paypal" (very suspicious)
2. "Has password field" (harvesting credentials)
3. "Form submits to external server" (attacker controlled)
4. "TLD is .tk" (cheap, often abused)
5. "Domain is new" (registered recently)

Top factors that made it look SAFE:
1. "Has HTTPS" (not many fake sites pay for SSL)

BUT:
- "HTTPS" (1 safe factor) 
- vs
- "Fake brand + password field + external form" (3 huge red flags)
- → Result: PHISHING ✅ (explanation makes sense!)
```

### 8. **PDF Report** (Detailed Documentation)

Generate a PDF report with 7 sections:

```
Section 1: Header
  ├─ Report ID: PHG_2024015_001
  ├─ URL: paypa1-secure-login.tk/verify
  └─ Timestamp: 2024-01-15 10:30 AM

Section 2: Risk Summary
  ├─ Big Red Circle (gauge) showing 82/100
  ├─ Risk Level: CRITICAL
  ├─ Verdict: DO NOT VISIT
  └─ ML Confidence: 95%

Section 3: Score Breakdown (table)
  Signal | Points
  ────────────────
  Brand | 30
  TLD   | 20
  Age   | 20
  ... etc

Section 4: Heuristic Findings
  ├─ Brand: PayPal impersonation detected
  ├─ SSL: Invalid certificate
  ├─ Domain Age: 3 days old
  └─ ... etc

Section 5: Why This Happened (SHAP explanation)
  Chart showing which features caused the high score

Section 6: Recommendations
  ├─ "Don't visit this site"
  ├─ "Don't click links from emails about this site"
  └─ "Report to PayPal"

Section 7: Technical Details
  All 49 features and their values
```

## How Many Files You Create
Approximately **12-15 files** totaling **2,500-3,500 lines of code**

## Example: What You Actually Write

```python
# predictor.py - The main prediction function

def predict(url):
    """
    Given a URL, return: score (0-100), risk level, and explanation
    """
    
    # Step 1: Extract features (49 clues)
    url_features = extract_url_features(url)      # 21 features (fast)
    content_features = extract_content_features(url)  # 28 features (slower)
    all_features = {**url_features, **content_features}
    
    # Step 2: Run AI model
    ai_probability = xgboost_model.predict(all_features)
    # Returns: 0.85 (85% sure it's phishing)
    
    # Step 3: Run 9 security checks (all at same time)
    checks = run_heuristics_parallel(url)
    # Returns: {
    #   'brand': {detected: True, penalty: 30},
    #   'dns': {resolves: False, penalty: 15},
    #   'ssl': {valid: False, penalty: 15},
    #   ... etc
    # }
    
    # Step 4: Calculate trust factor
    trust_factor = calculate_trust_factor(checks)
    # Returns: 0.4 or 1.0 depending on how clean signals are
    
    # Step 5: Fuse scores
    final_score = fuse_scores(ai_probability, trust_factor, checks)
    # Returns: 82 (out of 100)
    
    # Step 6: Generate SHAP explanation
    explanation = generate_shap_explanation(all_features)
    # Returns: top risk features and top safe features
    
    # Step 7: Generate PDF report
    pdf_path = generate_pdf_report(final_score, checks, explanation)
    
    # Step 8: Return result
    return {
        'score': 82,
        'risk_level': 'Critical',
        'verdict': 'Do not visit',
        'ml_probability': 0.85,
        'heuristic_results': checks,
        'explanation': explanation,
        'pdf_path': pdf_path
    }
```

## Your Checklist (What You Need to Do)

- ✅ Extract 21 URL features
- ✅ Extract 28 content features (fetch page)
- ✅ Train XGBoost model on 235K URLs
- ✅ Implement 9 security heuristic checks
- ✅ Make heuristics run in parallel (speed optimization)
- ✅ Implement brand impersonation check (Levenshtein distance)
- ✅ Implement DNS check
- ✅ Implement SSL check
- ✅ Implement WHOIS domain age check
- ✅ Implement TLD reputation check
- ✅ Implement IP detection checks (2 of them)
- ✅ Implement keyword scanning
- ✅ Implement punycode detection
- ✅ Calculate trust factor based on clean signals
- ✅ Fuse 11 signals into 0-100 score
- ✅ Generate SHAP explanations
- ✅ Generate PDF reports

---

# 👤 PERSON 4: DOCUMENTATION & DATA PERSON

## Your Job (In Plain English)
You are building **the instruction manual** and **preparing the data**. You help everyone else succeed.

## What You Do

### 1. **Prepare the Data**
The AI (Person 3) needs training data. You:

```
Step 1: Download Dataset
├─ Download "PhiUSIIL Phishing URL Dataset" (235,795 URLs)
├─ File size: ~50 MB
└─ Source: UCI Machine Learning Repository (free!)

Step 2: Clean the Data
├─ Remove duplicate URLs (same URL listed twice)
├─ Remove rows with missing information
├─ Fix any data errors
└─ Verify all 49 features are present

Step 3: Analyze the Data
├─ Make charts showing: "How many phishing vs legitimate?"
├─ Make charts showing: "What features are most important?"
├─ Write summary: "Dataset has 120K phishing, 115K legitimate"
└─ Save cleaned dataset for Person 3 to use

Step 4: Give Data to Person 3
└─ "Here's clean data ready for training!"
```

### 2. **Write Documentation** (The Instruction Manual)

For each component, write clear instructions:

#### **README.md** (What is this project?)
```
# PhishGuard - Phishing URL Detector

## What is this?
PhishGuard is a system that checks if URLs are safe or dangerous.
Just paste any URL and get instant feedback.

## How to use it?
1. Go to website
2. Paste URL (e.g., https://paypal.com)
3. Click "Check URL"
4. Wait 5 seconds
5. See result (Safe or Dangerous)

## Tech Stack
- Frontend: React, Vite, Tailwind CSS
- Backend: FastAPI, MongoDB, Redis
- ML: XGBoost, SHAP
- Dataset: PhiUSIIL (235K URLs)

## How to install it?
See DEPLOYMENT.md

## Links
- GitHub: https://github.com/...
- Demo: https://phishguard.com
```

#### **ARCHITECTURE.md** (How all parts fit together?)
```
Diagram showing:
User → Website → Backend → Database
         ↓
      ML Engine (checks URL)
         ↓
      Result back to User

Explanations of each part...
```

#### **API_DOCUMENTATION.md** (What requests can website make?)
```
ENDPOINT 1: POST /auth/login
  Purpose: Log in to the system
  Website sends: {"email": "john@gmail.com", "password": "abc123"}
  Backend returns: {"token": "abc123xyz...", "user": {...}}
  
ENDPOINT 2: POST /api/scan
  Purpose: Check if URL is safe
  Website sends: {"url": "https://example.com"}
  Backend returns: {"score": 82, "risk_level": "Critical", ...}
  
... (document all endpoints)
```

#### **FEATURE_ENGINEERING.md** (What are the 49 features?)
```
# Feature 1: URLLength
- What is it: Total length of the URL string
- Why it matters: Phishing URLs are often very long to hide phishing
- Example: "https://www.google.com" = 23 characters
- Low = safer, High = more suspicious

# Feature 2: DomainLength
- What is it: Length of just the domain part
- Why it matters: Legitimate companies have short domains
- Example: "google.com" = 10 characters
- Low = more likely legitimate, High = suspicious

... (repeat for all 49 features)
```

#### **DEPLOYMENT.md** (How to run this in production?)
```
1. Install Python and Node.js

2. Clone the project
   git clone https://github.com/...

3. Set up backend:
   cd backend
   pip install -r requirements.txt
   python main.py

4. Set up frontend:
   cd frontend
   npm install
   npm run dev

5. Open browser: http://localhost:5173

6. Done! It's running! 🎉
```

#### **SECURITY.md** (How are we protecting data?)
```
- Passwords: Encrypted with bcrypt
- Login tokens: JWT with HS256 encryption
- Database: Only logged-in users can access their data
- HTTPS: Website uses secure connection
- Rate limiting: Can't scan 1000 URLs in 1 second
```

#### **FAQ.md** (Common Questions)
```
Q: Why does it take 6 seconds?
A: Because checking takes time:
   - Get URL content: 1-2 seconds
   - Run AI model: <1 second
   - Run 9 security checks: 3-5 seconds
   - Generate report: 1 second

Q: Is my data private?
A: Yes! We don't sell or share your data.
   We only know your email and which URLs you scanned.

Q: How accurate is it?
A: 100% accurate on our test set of 47K URLs.
   Real-world accuracy is probably 95-98%.

... (more questions and answers)
```

### 3. **Create Architecture Diagrams**

Draw pictures showing how everything connects:

```
SYSTEM DIAGRAM:
┌─────────────┐
│  User       │
│ (Browser)   │
└──────┬──────┘
       │ (clicks "Check URL")
       ▼
┌─────────────────┐
│ React Website   │ (Person 1 built this)
│ (Dashboard)     │
└──────┬──────────┘
       │ (sends URL to check)
       ▼
┌─────────────────┐
│ FastAPI Backend │ (Person 2 built this)
│ (Brain)         │
└──────┬──────────┘
       │ (asks "Is this safe?")
       ▼
┌─────────────────┐
│ ML Engine       │ (Person 3 built this)
│ (AI + Rules)    │
└──────┬──────────┘
       │ (returns score)
       ▼
┌─────────────────┐
│ Result to User  │
│ "Score: 82"     │
└─────────────────┘
```

### 4. **Write Developer Guide** (How to add new features?)
```
If we want to add a NEW security check:

Step 1: Create function in Person 3's code:
  def check_my_new_rule(url):
      result = do_security_check()
      return {'score': 30, 'detected': True}

Step 2: Add to parallel checks in Person 3's code:
  checks['my_rule'] = check_my_new_rule(url)

Step 3: Tell Person 2 about the new rule
  (maybe need more info stored in database)

Step 4: Tell Person 1 to show it in frontend
  (maybe show specific warning about this new rule)

Step 5: Test everything works together

Step 6: Update documentation
  (explain the new feature)

Done!
```

### 5. **Make Example Files**
```
.env.example (shows what settings backend needs):
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=phishguard
JWT_SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379
API_PORT=8000
```

## Files You Make

```
README.md              ← What is this?
ARCHITECTURE.md        ← How do parts work together?
API_DOCUMENTATION.md   ← What requests can website send?
FEATURE_ENGINEERING.md ← Explain all 49 features
MODEL_TRAINING.md      ← How AI training works
DEPLOYMENT.md          ← How to run in production?
SECURITY.md            ← How is data safe?
CONTRIBUTING.md        ← How to help add features?
FAQ.md                 ← Common questions
.env.example           ← Configuration template
docker-compose.yml     ← How to run in Docker (containers)

dataset/preprocessing.py     ← Clean and prepare data
dataset/eda.py               ← Find interesting patterns
dataset/visualization.png    ← Show data patterns
```

## How Many Files You Create
Approximately **12-14 files** totaling **500-1,000 lines of code/text**

## Example: What You Actually Write

```markdown
# README.md

# PhishGuard 🛡️

PhishGuard is an AI-powered system that checks if website URLs are safe or phishing attacks.

## Quick Demo

1. Paste a URL: `https://paypal.com`
2. Hit "Check"
3. Get result in 5 seconds

### Results

| URL | Score | Result |
|-----|-------|--------|
| google.com | 15.9 | ✅ SAFE |
| paypa1-secure.tk | 82.0 | 🚨 DANGER |
| github.com | 2.9 | ✅ SAFE |

## How It Works

Step 1: Extract 49 features from URL (is it HTTPS? New domain? etc.)
Step 2: AI model says: "Is this phishing?"
Step 3: 9 security checks verify: "DNS ok? SSL valid? etc."
Step 4: Final score: 0-100 (0=Safe, 100=Danger)

## Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/phishguard/phishguard.git
cd phishguard

# Install backend
cd backend
pip install -r requirements.txt

# Install frontend
cd ../frontend
npm install

# Run backend
cd ../backend
python main.py

# Run frontend (in new terminal)
cd ../frontend
npm run dev

# Open browser: http://localhost:5173
```

### Usage

1. Open http://localhost:5173
2. Click "Login" or "Register"
3. Paste any URL
4. Click "Check URL"
5. Wait 5 seconds
6. See result!

## Features

✅ Real-time URL checking
✅ AI + security rules combined
✅ Instant results (5-7 seconds)
✅ Explains why URL is risky
✅ PDF reports
✅ Check 10 URLs at once
✅ Full scan history

## Architecture

- **Frontend**: React (what users see)
- **Backend**: FastAPI (the brain)
- **Database**: MongoDB (store data)
- **Cache**: Redis (make it fast)
- **ML**: XGBoost + SHAP (the AI)

See ARCHITECTURE.md for details.

## Team

- **Person 1**: Frontend (React website)
- **Person 2**: Backend (FastAPI brain)
- **Person 3**: ML & Heuristics (AI model)
- **Person 4**: Documentation & Data

## License

MIT License - Free to use!
```

## Your Checklist (What You Need to Do)

- ✅ Download and clean 235K URL dataset
- ✅ Make charts showing data patterns
- ✅ Write README (main project overview)
- ✅ Write ARCHITECTURE.md (system design)
- ✅ Write API_DOCUMENTATION.md (all endpoints)
- ✅ Write FEATURE_ENGINEERING.md (all 49 features)
- ✅ Write MODEL_TRAINING.md (how AI is trained)
- ✅ Write DEPLOYMENT.md (how to run in production)
- ✅ Write SECURITY.md (data protection)
- ✅ Write CONTRIBUTING.md (how to help)
- ✅ Write FAQ.md (common questions)
- ✅ Create .env.example file
- ✅ Create docker-compose.yml (container setup)
- ✅ Update documentation as code changes

---

# 📊 WHO DOES HOW MUCH WORK?

```
Person 1 (Frontend):  ███████████████░░░░░░░░░░░░░░░ 30%
Person 2 (Backend):   ████████████████░░░░░░░░░░░░░░ 35%
Person 3 (ML):        ███████████████░░░░░░░░░░░░░░░ 30%
Person 4 (Docs):      █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  5%
```

---

# 📅 SIMPLE TIMELINE

## Week 1: Get Ready
```
Person 1: Learn React
Person 2: Learn FastAPI, database
Person 3: Learn ML, prepare dataset
Person 4: Download dataset, start writing docs
```

## Week 2-3: Build Main Parts
```
Person 1: Build Dashboard, History, Detail pages
Person 2: Build login, database models
Person 3: Build feature extraction, train model
Person 4: Write README, Architecture docs
```

## Week 4-5: Add Features
```
Person 1: Build Bulk Scan, Profile pages
Person 2: Build scan endpoint, caching
Person 3: Build heuristics, score fusion
Person 4: Write API documentation, guides
```

## Week 6-7: Connect & Polish
```
Person 1: Connect all pages with backend
Person 2: Fix errors, add rate limiting
Person 3: Add SHAP explanations, PDF reports
Person 4: Finalize documentation, deployment guide
```

---

# ❓ FREQUENTLY ASKED QUESTIONS

## Q: What if I don't know how to program?
A: This is too advanced. You need to know:
- Person 1: Must know JavaScript/React
- Person 2: Must know Python/FastAPI
- Person 3: Must know Python/ML
- Person 4: Must know markdown/documentation (easiest!)

## Q: What if something breaks?
A: 
1. Tell the team immediately
2. Check if other parts are affected
3. Fix it together
4. Update documentation

## Q: How long does it take total?
A: About 6-8 weeks for 4 people working together

## Q: Can I do multiple roles?
A: Only if you're very experienced. Each role is full-time!

## Q: What if I finish early?
A: 
1. Help another person
2. Add more features (better UI, more checks)
3. Write tests (make sure code works)
4. Improve documentation

---

# 🎯 SUCCESS AT THE END

### Person 1 (Frontend) Can Say:
"I built the website that 1000 users can access. It's fast, pretty, and easy to use."

### Person 2 (Backend) Can Say:
"I built the brain that handles 1000 users simultaneously, caches results, and protects user data."

### Person 3 (ML) Can Say:
"I built the AI that achieves 100% accuracy on test set, with 9 security rules running in parallel."

### Person 4 (Documentation) Can Say:
"I prepared the data, documented everything, and made sure anyone can understand and deploy this system."

---

# 🤝 WORKING TOGETHER

### Daily Check-in (5 minutes)
```
Person 1: "I finished dashboard page. It looks great!"
Person 2: "I finished login endpoint. Ready to test?"
Person 3: "I trained the model. 100% accuracy!"
Person 4: "I documented the features. Need anything else?"
```

### Weekly Team Meeting (1 hour)
```
Review: What's done? What's next? Any blockers?
Support: Help each other with problems
Plan: Make sure everyone on track
```

### Code Review
```
Before pushing code:
1. Tell another person to check it
2. They look for bugs and mistakes
3. They approve or ask for fixes
4. Then you push it
```

---

**You're ready to start! 🚀 Pick your role and begin!**

