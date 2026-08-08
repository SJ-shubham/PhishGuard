# PhishGuard Project - Presentation Script (1-2 minutes)

---

## OPENING [0:00-0:08]

"Hello everyone! This is **PhishGuard** — a real-time phishing detection system that uses artificial intelligence to protect you from malicious URLs. Instead of relying on outdated blacklists, our system combines advanced machine learning with intelligent security checks to identify threats in seconds.

Let me walk you through how it works."

---

## INTERFACE TOUR [0:08-0:45]

### **1. Login & Register [0:08-0:12]**
"First, users create an account and log in. PhishGuard uses JWT authentication to keep your data secure."

**[SHOW: Login page → Register page]**

---

### **2. Dashboard - Main Scanning [0:12-0:25]**
"Here's the main dashboard. It's simple — just paste any URL you want to check. Let me scan a URL."

**[SHOW: Dashboard page]**

"Click scan... and you'll see real-time progress as our system runs through multiple security checks."

**[SHOW: Progress bar with steps]**

"Our system checks DNS resolution, validates SSL certificates, analyzes the domain age, detects brand impersonation, and scans for phishing keywords — all happening in parallel."

---

### **3. Results Display [0:25-0:35]**
"Within 5 to 7 seconds, you get a detailed risk score on a 0-100 scale. Here's a phishing site — score 82 out of 100, marked as Critical Risk."

**[SHOW: Result card with score gauge (red), risk badge, verdict]**

"You can see exactly why it's flagged: the domain is brand impersonation, uses a suspicious TLD, and has phishing keywords. This is our SHAP explainability in action — transparency matters."

---

### **4. Detailed Analysis [0:35-0:42]**
"Click 'View Details' for a complete breakdown. You'll see the ML prediction score, all 11 contributing signals, and SHAP feature importance charts showing which factors most influenced the decision."

**[SHOW: Scan detail page with breakdown table, heuristics cards, SHAP charts]**

"You can download a full PDF report for records."

---

### **5. History & Bulk Scanning [0:42-0:50]**
"All your scans are saved in history with filtering and sorting. You can also perform bulk scanning — check up to 10 URLs at once and see results side by side."

**[SHOW: History page → Bulk scan page]**

---

## HOW IT WORKS - TECHNICAL [0:50-1:20]

"Behind the scenes, here's what powers PhishGuard:

**The AI Model:** We trained an XGBoost classifier on 235,000 real phishing and legitimate URLs. It achieves **100% accuracy** on our test set with perfect precision and recall.

**The Features:** Our system extracts 49 engineered features — URL characteristics, content analysis, HTML structure — and feeds them into the model.

**The Heuristics:** We don't just trust AI alone. Nine concurrent security checks verify:
- DNS resolution
- SSL certificate validity
- Domain age
- Brand impersonation detection
- Phishing keyword scanning
- IP address patterns
- And more

**Trust Calibration:** Sites like Google get lower risk scores because they pass all legitimate checks, even if the ML gives them a high score. This eliminates false alarms on complex legitimate sites.

**Result:** Every prediction is explainable. Users understand why a URL is flagged."

---

## KEY FEATURES [1:20-1:35]

"Here's what makes PhishGuard powerful:

✓ **Real-time detection** — 5-7 second scans using parallel processing
✓ **Explainable AI** — SHAP technology shows exactly which features triggered alerts
✓ **Zero false positives** — Trust calibration prevents blocking legitimate sites
✓ **Detects advanced attacks** — Homoglyphs (paypa1 vs paypal), IP obfuscation, zero-day campaigns
✓ **No blacklist dependency** — ML catches threats that haven't been seen before
✓ **Full-stack security** — JWT authentication, rate limiting, Redis caching, encrypted passwords"

---

## CLOSING [1:35-1:50]

"PhishGuard represents a modern approach to cybersecurity. Instead of asking 'Is this URL on a blocklist?', we ask 'Does this URL exhibit phishing characteristics?'

With 96% of cyberattacks starting with phishing, real-time detection like this can save organizations millions in potential data breaches.

The system is production-ready, fully documented, and deployed with a React frontend, FastAPI backend, MongoDB database, and Redis caching.

Thank you — that's PhishGuard!"

---

## TOTAL TIMING: **1 minute 50 seconds**

---

## DEMO SEQUENCE (What to show on screen):

1. **0:08** → Login page (type credentials)
2. **0:12** → Dashboard with URL input field
3. **0:14** → Type URL and click scan
4. **0:19** → Show animated progress bar (pause if needed)
5. **0:25** → Show result card with red gauge
6. **0:35** → Click "View Details" → full breakdown
7. **0:42** → Click back, show History page
8. **0:46** → Show Bulk Scan page
9. **1:20** → Could show architecture diagram or system flowchart
10. **1:35** → Show feature importance chart from models

---

## VOICE TONE & DELIVERY TIPS:

✓ **Speak clearly and confidently** — not too fast
✓ **Pause at key moments** — let important info sink in
✓ **Use hand gestures** — point at UI elements
✓ **Emphasize numbers** — "100% accuracy", "5-7 seconds"
✓ **Use simple language** — avoid heavy jargon for general audiences
✓ **Build momentum** — start slow, accelerate through features
✓ **End strong** — emphasize real-world impact

---

## VARIATIONS

### For Technical Audience (add more detail):
- Mention XGBoost hyperparameters
- Discuss trust calibration formula
- Show SHAP waterfall plot
- Add confusion matrix statistics

### For Business/Non-Technical Audience (simplify):
- Skip technical detail
- Focus on "why it matters"
- Emphasize real-world impact
- Add phishing statistics

