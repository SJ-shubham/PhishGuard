# PhishGuard - 4 Members Quick Start (Pick Your Role!)

---

# 🎬 START HERE: Pick Your Role

## **👨‍💻 PERSON 1: FRONTEND DEVELOPER**

### Your Job in ONE Sentence:
**Build the website that users see and click on.**

### What You Produce:
- ✅ Login page → User enters email + password
- ✅ Dashboard → Paste URL, click "Check", see result
- ✅ History page → See all URLs you checked
- ✅ Detail page → Full details about one check
- ✅ Bulk scan → Check 10 URLs at once
- ✅ Profile page → User settings

### Tech You Need:
- React (JavaScript library)
- Tailwind CSS (make it look pretty)
- Axios (talk to backend)

### Time to Complete:
**60-80 hours** (about 2 weeks for 1 person, 1 week for experienced dev)

### Files You'll Make:
`frontend/pages/*.jsx`, `frontend/components/*.jsx`, styling files

### Success = When:
Users can login → check URL → see result with nice visuals ✅

---

## **🧠 PERSON 2: BACKEND DEVELOPER**

### Your Job in ONE Sentence:
**Build the brain that receives requests from website and sends back answers.**

### What You Produce:
- ✅ Login system → Users can register and login
- ✅ Scan endpoint → Website sends URL, you return score
- ✅ History endpoint → Return list of past checks
- ✅ Database → Store user info and scan results
- ✅ Caching → Make repeated checks instant
- ✅ Rate limiting → Stop people from abusing system

### Tech You Need:
- FastAPI (Python web framework)
- MongoDB (database)
- Redis (super-fast cache)
- Python async (handle many users at once)

### Time to Complete:
**80-100 hours** (about 2.5 weeks for 1 person)

### Files You'll Make:
`backend/main.py`, `backend/routes/*.py`, `backend/models/*.py`, `backend/services/*.py`

### Success = When:
Website can send URLs to your backend → you return proper scores ✅

---

## **🤖 PERSON 3: ML DEVELOPER**

### Your Job in ONE Sentence:
**Build the AI brain and security checks that decide if URLs are phishing.**

### What You Produce:
- ✅ Feature extraction → Get 49 clues from each URL
- ✅ AI model → Train XGBoost on 235K examples
- ✅ 9 security checks → Brand, DNS, SSL, etc. (parallel)
- ✅ Score fusion → Combine AI + heuristics
- ✅ SHAP explanations → Explain WHY the score
- ✅ PDF reports → Generate detailed reports

### Tech You Need:
- Python (data science)
- XGBoost (AI/ML library)
- SHAP (explain AI decisions)
- Pandas/NumPy (data processing)

### Time to Complete:
**70-90 hours** (about 2-2.5 weeks for 1 person)

### Files You'll Make:
`src/features/*.py`, `src/heuristics/*.py`, `src/predictor.py`, `src/fusion.py`, `train.py`

### Success = When:
You can take any URL and return 0-100 score with explanation ✅

---

## **📚 PERSON 4: DOCUMENTATION PERSON**

### Your Job in ONE Sentence:
**Write the instruction manual + prepare the data (lighter job!).**

### What You Produce:
- ✅ Clean dataset → Download and prepare 235K URLs
- ✅ README → "What is this project?"
- ✅ API docs → "What can website ask backend?"
- ✅ Feature dictionary → "What do the 49 features mean?"
- ✅ Architecture diagram → "How do all parts connect?"
- ✅ Deployment guide → "How to run in production?"

### Tech You Need:
- Markdown (simple text format)
- Python (basic scripting)
- Pandas (read CSV files)
- Basic understanding of the other 3 parts

### Time to Complete:
**20-30 hours** (about 0.5-1 week for 1 person)

### Files You'll Make:
`README.md`, `ARCHITECTURE.md`, `API_DOCUMENTATION.md`, `dataset/preprocessing.py`

### Success = When:
Anyone can read your docs and understand the entire project ✅

---

# 📋 STEP-BY-STEP STARTING GUIDE

## **WEEK 1: GET ORGANIZED**

### All Team Members Together (30 minutes):
```
1. Everyone reads this document
2. Each person chooses their role
3. Copy their detailed guide (see below for filenames)
4. Understand: "What am I building?"
```

### Person 1 (Frontend):
```
TO-DO THIS WEEK:
□ Learn React (if not already known)
□ Set up React project with Vite
□ Create basic pages structure (empty shells)
□ Set up Tailwind CSS
□ Create component folder structure
```

### Person 2 (Backend):
```
TO-DO THIS WEEK:
□ Learn FastAPI (if not already known)
□ Create FastAPI project
□ Set up MongoDB connection
□ Set up Redis connection
□ Create basic route structure (empty endpoints)
```

### Person 3 (ML):
```
TO-DO THIS WEEK:
□ Download PhiUSIIL dataset (from UCI)
□ Learn XGBoost (if not already known)
□ Look at dataset structure
□ Plan feature extraction strategy
□ Prepare training script skeleton
```

### Person 4 (Documentation):
```
TO-DO THIS WEEK:
□ Download dataset
□ Clean dataset (remove duplicates, etc.)
□ Create basic documentation files
□ Make EDA charts (show data patterns)
□ Create README skeleton
```

---

## **WEEK 2-3: BUILD CORE FEATURES**

### Person 1 (Frontend):
```
□ Dashboard page with URL input
□ Login/Register pages
□ Make pages beautiful with Tailwind
□ Connect to backend API (even if fake response for now)
```

### Person 2 (Backend):
```
□ Login endpoint (/auth/login)
□ Register endpoint (/auth/register)
□ Scan endpoint (/api/scan) - dummy version
□ History endpoint (/api/scans)
□ Database models for users and scans
```

### Person 3 (ML):
```
□ Extract 21 URL features
□ Extract 28 content features
□ Train XGBoost model on dataset
□ Make sure model achieves high accuracy
```

### Person 4 (Documentation):
```
□ Write README with examples
□ Create API documentation template
□ Document the 49 features
□ Show EDA charts to team
```

---

## **WEEK 4-5: ADD SPECIAL FEATURES**

### Person 1 (Frontend):
```
□ History page (list of past scans)
□ Detail page (full info about one scan)
□ Bulk scan page (check 10 URLs)
□ Make real-time progress work
```

### Person 2 (Backend):
```
□ Implement caching (Redis)
□ Implement rate limiting
□ Connect to Person 3's ML code ✨
□ Send real-time progress updates
```

### Person 3 (ML):
```
□ Build 9 heuristic checks
□ Make them run in parallel
□ Calculate trust calibration
□ Combine AI + heuristics score
□ Add SHAP explanations
```

### Person 4 (Documentation):
```
□ Complete API documentation
□ Write deployment guide
□ Document all 49 features fully
□ Create architecture diagrams
```

---

## **WEEK 6-7: POLISH & FINALIZE**

### Person 1 (Frontend):
```
□ Make responsive (works on phone)
□ Add animations and polish
□ Fix any bugs
□ Make sure all features work end-to-end
```

### Person 2 (Backend):
```
□ Write error handling
□ Add logging
□ Test with Person 1's frontend
□ Fix any bugs
```

### Person 3 (ML):
```
□ Generate PDF reports
□ Finalize SHAP explanations
□ Test full pipeline
□ Make sure it's fast (<7 seconds)
```

### Person 4 (Documentation):
```
□ Write FAQ
□ Finalize all documentation
□ Create deployment guide
□ Make sure everyone can understand project
```

---

# 📚 DETAILED GUIDES (Go Read These!)

## Person 1 (Frontend) - Read This:
📄 **File**: `TEAM_SIMPLE_GUIDE.md` → Section "PERSON 1: FRONTEND DEVELOPER"

Contains:
- Detailed code examples
- Component breakdown
- File structure

## Person 2 (Backend) - Read This:
📄 **File**: `TEAM_SIMPLE_GUIDE.md` → Section "PERSON 2: BACKEND DEVELOPER"

Contains:
- API endpoint explanations
- Database schema
- Code examples

## Person 3 (ML) - Read This:
📄 **File**: `TEAM_SIMPLE_GUIDE.md` → Section "PERSON 3: ML & HEURISTICS DEVELOPER"

Contains:
- 49 features explained
- ML model details
- 9 heuristic checks
- Code examples

## Person 4 (Documentation) - Read This:
📄 **File**: `TEAM_SIMPLE_GUIDE.md` → Section "PERSON 4: DOCUMENTATION & DATA PERSON"

Contains:
- What to document
- Example files to write
- Code examples

---

# 🔧 QUICK SETUP FOR EACH ROLE

## Person 1 (Frontend) - First 2 Hours:
```bash
# Install Node.js if not already done

# Create React project
npm create vite@latest phishguard-frontend -- --template react
cd phishguard-frontend

# Install dependencies
npm install
npm install axios react-router-dom tailwindcss

# Start development
npm run dev

# Open in browser: http://localhost:5173
```

## Person 2 (Backend) - First 2 Hours:
```bash
# Install Python 3.10+

# Create project folder
mkdir phishguard-backend
cd phishguard-backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Create requirements file
pip install fastapi uvicorn motor redis pymongo pydantic python-jose bcrypt

# Start
uvicorn main:app --reload
```

## Person 3 (ML) - First 2 Hours:
```bash
# Install Python 3.10+

# Create project
mkdir phishguard-ml
cd phishguard-ml

# Virtual environment
python -m venv venv
# Activate it (same as above)

# Install packages
pip install pandas numpy xgboost scikit-learn shap matplotlib

# Download dataset (from UCI)
# Save as: dataset/PhiUSIIL_Phishing_URL_Dataset.csv

# Start exploring!
python
>>> import pandas as pd
>>> df = pd.read_csv("dataset/PhiUSIIL_Phishing_URL_Dataset.csv")
>>> print(df.shape)  # Should show (235795, 49)
```

## Person 4 (Documentation) - First 2 Hours:
```bash
# Create documentation folder
mkdir phishguard-docs

# Download dataset
# Go to: https://archive.ics.uci.edu/dataset/967/
# Download PhiUSIIL dataset (~50 MB)

# Create first documents
# Create: README.md
# Create: ARCHITECTURE.md
# Create: API_DOCUMENTATION.md

# Download Person 3's dataset
# Explore it with Python

import pandas as pd
df = pd.read_csv("dataset.csv")
print(df.describe())  # See patterns
```

---

# ✅ DAILY CHECKLIST

## Every Day, Each Person Asks Themselves:

```
☐ Did I work on my assigned tasks?
☐ Did I encounter any blockers?
☐ Do I need help from another person?
☐ Did I update my progress?
☐ Did I commit my code to GitHub?
☐ Did I tell the team what I'm doing?
```

---

# 🚨 IF YOU GET STUCK

### Person 1 (Frontend):
- Can't connect to backend? → Ask Person 2
- Don't know how to make a component? → Google "React component tutorial"
- Not looking pretty? → Google "Tailwind CSS"

### Person 2 (Backend):
- Can't connect to MongoDB? → Check MongoDB is running
- API not returning data? → Check the code (print statements!)
- Person 1's website shows error? → Check error in browser console

### Person 3 (ML):
- Model accuracy too low? → Check features are extracted correctly
- Heuristics not working? → Test individually
- Slow predictions? → Person 2 should use caching

### Person 4 (Documentation):
- Not sure what to write? → Ask other team members questions
- Dataset corrupted? → Re-download from UCI
- Can't understand code? → Ask the person who wrote it

---

# 📞 COMMUNICATION

### Daily (5 minutes in Slack/WhatsApp):
```
Person 1: "✅ Finished Dashboard page"
Person 2: "✅ Finished login endpoint"
Person 3: "✅ Model training done - 99% accuracy"
Person 4: "✅ Documented 25 features"
```

### Weekly Meeting (1 hour):
```
1. What's done?
2. What's next?
3. Any problems?
4. How can we help each other?
```

### Emergency (Immediate):
```
"Hey! I found a bug that breaks everything"
→ Everyone helps immediately
```

---

# 🎯 FINAL GOAL

**Create a website where:**
- Users login securely
- Users paste any URL
- System analyzes URL in 5 seconds
- Shows beautiful result: "Safe" (green) or "Danger" (red)
- User understands WHY it made that decision
- All code is documented so anyone can understand it

---

# 📁 ALL YOUR DOCUMENTS ARE HERE:

```
c:\Users\Shubham\Desktop\PhishGuard\
├─ TEAM_SIMPLE_GUIDE.md          ← MAIN DETAILED GUIDE (Read this first!)
├─ TEAM_DIVISION_4_MEMBERS.md    ← Very detailed breakdown
├─ TEAM_DIVISION_QUICKREF.md     ← Quick reference during work
├─ TEAM_STRUCTURE_VISUAL.md      ← Visual diagrams
├─ VIVA_DETAILED_EXPLANATION.md  ← For your presentation
├─ VIVA_QUICK_REFERENCE.md       ← Viva cheat sheet
└─ (other project files)
```

---

# 🚀 YOU'RE READY!

**Pick your role, read your guide, and start building!**

Questions? Ask the team or refer to the detailed guides above.

**Good luck! 💪**

