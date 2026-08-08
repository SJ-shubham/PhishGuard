import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

os.makedirs('outputs', exist_ok=True)

fig, ax = plt.subplots(figsize=(22, 28))
ax.set_xlim(0, 22)
ax.set_ylim(0, 28)
ax.axis('off')
fig.patch.set_facecolor('#0f172a')

def box(ax, x, y, w, h, bg, edge, radius=0.3, lw=1.5):
    r = FancyBboxPatch((x, y), w, h,
                        boxstyle=f"round,pad=0,rounding_size={radius}",
                        facecolor=bg, edgecolor=edge, linewidth=lw, zorder=3)
    ax.add_patch(r)

def txt(ax, x, y, s, size=9, color='white', weight='normal', ha='center', va='center'):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, zorder=4, fontfamily='monospace')

def arrow(ax, x1, y1, x2, y2, color='#64748b', lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                connectionstyle='arc3,rad=0.0'), zorder=2)

# TITLE
txt(ax, 11, 27.3, 'PhishGuard  -  System Architecture', size=18, color='white', weight='bold')
txt(ax, 11, 26.85, 'ML  x  Heuristics  x  FastAPI  x  MongoDB  x  Redis  x  React',
    size=10, color='#94a3b8')

# LAYER 0 - USER
box(ax, 7.5, 25.6, 7, 0.9, '#1e293b', '#3b82f6', lw=2)
txt(ax, 11, 26.05, 'User / Browser', size=11, weight='bold')
arrow(ax, 11, 25.6, 11, 25.1, color='#3b82f6', lw=2)
txt(ax, 11.6, 25.35, 'HTTP', size=7.5, color='#94a3b8')

# LAYER 1 - REACT FRONTEND
box(ax, 0.4, 21.5, 21.2, 3.5, '#0f1f3d', '#3b82f6', lw=2)
txt(ax, 11, 24.65, 'REACT FRONTEND', size=10, weight='bold', color='#60a5fa')
txt(ax, 11, 24.2, 'Vite 8  |  React Router v6  |  Axios  |  Tailwind CSS  |  port 5173',
    size=8, color='#94a3b8')

pages = [
    ('Login / Register',              0.7,  22.1),
    ('Dashboard\nURL input + SSE',    3.1,  22.1),
    ('History\nfilter+sort+delete',   5.95, 22.1),
    ('Scan Detail\nfull result+PDF',  8.8,  22.1),
    ('Bulk Scan\nup to 10 URLs',      11.65,22.1),
    ('Profile\nchange-pw + delete',   14.5, 22.1),
]
for label, px, py in pages:
    box(ax, px, py, 2.6, 1.7, '#1e3a5f', '#2563eb', lw=1)
    txt(ax, px+1.3, py+0.85, label, size=7.5, color='#bfdbfe')

comps = ['AuthContext', 'ProtectedRoute', 'Axios+auto-refresh',
         'ScoreGauge', 'RiskBadge', 'ScanProgress', 'ResultCard', 'Navbar']
for i, c in enumerate(comps):
    cx = 0.75 + i * 2.6
    box(ax, cx, 21.55, 2.4, 0.5, '#172554', '#1d4ed8', lw=0.8, radius=0.15)
    txt(ax, cx+1.2, 21.8, c, size=6.5, color='#93c5fd')

arrow(ax, 11, 21.5, 11, 21.0, color='#3b82f6', lw=2)
txt(ax, 12.5, 21.25, 'REST / SSE  (Vite proxy)', size=7.5, color='#94a3b8')

# LAYER 2 - FASTAPI BACKEND
box(ax, 0.4, 16.0, 21.2, 4.9, '#1a0f2e', '#8b5cf6', lw=2)
txt(ax, 11, 20.55, 'FASTAPI BACKEND', size=10, weight='bold', color='#a78bfa')
txt(ax, 11, 20.1, 'Uvicorn  |  async/await  |  Pydantic  |  port 8000', size=8, color='#94a3b8')

# Middleware strip
box(ax, 0.6, 19.4, 21.0, 0.65, '#2d1f4e', '#7c3aed', lw=1)
middlewares = [
    'JWT Auth Guard  (auth_guard.py)',
    'Rate Limiter  10 scans/min/user  (Redis-backed)',
    'CORS  |  origin: localhost:5173'
]
for i, m in enumerate(middlewares):
    txt(ax, 1.9 + i * 7.05, 19.72, m, size=7.5, color='#c4b5fd')

routes_data = [
    ('AUTH ROUTES  /auth/*',
     ['POST /register', 'POST /login', 'POST /logout',
      'POST /refresh', 'GET  /me',
      'PUT  /change-password', 'DELETE /delete-account'],
     0.6, 16.3, 4.9),
    ('SCAN ROUTES  /api/scan*',
     ['POST /scan  (SSE stream)', 'GET  /scans  (paginated)',
      'GET  /scans/stats', 'GET  /scans/{id}',
      'DELETE /scans/{id}', 'GET  /scans/{id}/report',
      'POST /scans/{id}/rescan', 'POST /scan/bulk'],
     5.7, 16.3, 6.2),
    ('PUBLIC  /public/*',
     ['POST /public/scan', '(no auth, no DB save)', 'Redis cache still used'],
     12.1, 16.3, 4.2),
    ('SERVICES',
     ['auth_service.py', 'scan_service.py', 'report_service.py'],
     16.5, 16.3, 4.9),
]
for title, items, rx, ry, rw in routes_data:
    box(ax, rx, ry, rw, 2.9, '#0d0620', '#6d28d9', lw=1)
    txt(ax, rx+rw/2, ry+2.63, title, size=8, weight='bold', color='#c4b5fd')
    for j, item in enumerate(items):
        txt(ax, rx+rw/2, ry+2.15-j*0.3, item, size=6.8, color='#e2e8f0')

arrow(ax, 4,    16.0, 4,    15.5, color='#7c3aed', lw=1.8)
arrow(ax, 10.5, 16.0, 10.5, 15.5, color='#7c3aed', lw=1.8)
arrow(ax, 17.5, 16.0, 17.5, 15.5, color='#7c3aed', lw=1.8)

# LAYER 3a - MONGODB
box(ax, 0.4, 10.5, 6.5, 4.8, '#0d2418', '#16a34a', lw=2)
txt(ax, 3.65, 15.0, 'MONGODB', size=10, weight='bold', color='#4ade80')
txt(ax, 3.65, 14.6, 'Motor  (async driver)', size=8, color='#86efac')

box(ax, 0.7, 13.4, 5.9, 1.0, '#052e16', '#15803d', lw=1)
txt(ax, 3.65, 14.05, 'users  collection', size=8, weight='bold', color='#bbf7d0')
txt(ax, 3.65, 13.65,
    '_id  name  email  password_hash  created_at  scan_count',
    size=5.8, color='#86efac')

box(ax, 0.7, 11.6, 5.9, 1.65, '#052e16', '#15803d', lw=1)
txt(ax, 3.65, 12.95, 'scans  collection', size=8, weight='bold', color='#bbf7d0')
scan_fields = [
    '_id  user_id  url  timestamp  score',
    'risk_level  verdict  ml_probability',
    'trust_factor  elapsed_time  score_breakdown',
    'heuristic_flags  features  shap_values'
]
for j, f in enumerate(scan_fields):
    txt(ax, 3.65, 12.55 - j * 0.28, f, size=6, color='#86efac')

txt(ax, 3.65, 10.85, 'Indexes: user_id, timestamp, score', size=7, color='#4ade80')

# LAYER 3b - REDIS
box(ax, 7.3, 10.5, 6.5, 4.8, '#1f0a0a', '#dc2626', lw=2)
txt(ax, 10.55, 15.0, 'REDIS', size=10, weight='bold', color='#f87171')
txt(ax, 10.55, 14.6, 'aioredis  |  async  |  port 6379', size=8, color='#fca5a5')

redis_blocks = [
    ('URL Result Cache', 'scan:cache:{sha256(url)}', 'TTL: 1 hour'),
    ('JWT Blacklist',    'blacklist:{token}',         'TTL: token remaining exp'),
    ('Rate Limit Counter','ratelimit:scan:{user_id}', 'TTL: 60s  |  max 10/min'),
]
for i, (title, key, note) in enumerate(redis_blocks):
    by = 13.5 - i * 1.1
    box(ax, 7.6, by, 5.9, 0.9, '#3b0a0a', '#b91c1c', lw=0.8, radius=0.2)
    txt(ax, 10.55, by+0.67, title, size=7.5, weight='bold', color='#fca5a5')
    txt(ax, 10.55, by+0.4,  key,   size=6.5, color='#fecaca')
    txt(ax, 10.55, by+0.15, note,  size=6.2, color='#f87171')

txt(ax, 10.55, 10.85, 'Fails gracefully if Redis is unavailable', size=7, color='#f87171')

# LAYER 3c - ML ENGINE
box(ax, 14.1, 5.2, 7.1, 10.1, '#0a1628', '#0ea5e9', lw=2)
txt(ax, 17.65, 15.0, 'ML ENGINE  (src/)', size=10, weight='bold', color='#38bdf8')

ml_blocks = [
    ('Feature Extraction  (49 features)',
     ['URL: length / entropy / TLD-prob / special-chars',
      'Content: LOC / ext-refs / forms / images / HTTPS'],
     14.3, 13.4, 6.7, 1.3),
    ('XGBoost Classifier  (phishguard_model.pkl)',
     ['Trained on 235K URLs  (PhiUSIIL dataset)',
      'Output: P(phishing) 0.0-1.0   F1=0.9999  AUC=1.0'],
     14.3, 11.75, 6.7, 1.4),
    ('Heuristic Engine  (9 checks, concurrent)',
     ['Brand: homoglyph + typosquat  (Levenshtein)',
      'DNS resolution  |  SSL/HTTPS validation',
      'WHOIS domain age  |  TLD reputation',
      'IP-in-subdomain  |  Keywords (50+)  |  Punycode/IDN'],
     14.3, 9.4, 6.7, 2.1),
    ('Trust Calibration + Score Fusion',
     ['trust = 1 - (n_clean/6) x 0.6',
      'raw  = ML x trust  +  heuristic penalties',
      'final = raw / RAW_MAX(150) x 100  ->  0-100'],
     14.3, 7.9, 6.7, 1.3),
    ('SHAP TreeExplainer',
     ['Per-prediction feature attribution',
      'top_risk + top_safe features stored in MongoDB'],
     14.3, 6.6, 6.7, 1.1),
    ('PDF Report Engine  (ReportLab)',
     ['7 sections: risk summary / signals / SHAP / recommendations'],
     14.3, 5.5, 6.7, 0.85),
]
for title, items, bx, by, bw, bh in ml_blocks:
    box(ax, bx, by, bw, bh, '#0c2a3d', '#0369a1', lw=1, radius=0.2)
    txt(ax, bx+bw/2, by+bh-0.22, title, size=7.5, weight='bold', color='#7dd3fc')
    for j, item in enumerate(items):
        txt(ax, bx+bw/2, by+bh-0.52-j*0.28, item, size=6.2, color='#bae6fd')

for y in [13.4, 11.75, 9.4, 7.9, 6.6]:
    arrow(ax, 17.65, y, 17.65, y-0.12, color='#0ea5e9', lw=1)

# DATA FLOW PANEL
box(ax, 0.4, 5.2, 13.4, 5.0, '#0f172a', '#334155', lw=1.5)
txt(ax, 6.75, 10.0, 'DATA FLOW  --  Scan Request (end-to-end)',
    size=9, weight='bold', color='#94a3b8')

steps = [
    '1.  User submits URL via Dashboard input',
    '2.  React  ->  POST /api/scan  (JWT in Authorization header)',
    '3.  Rate Limiter checks Redis counter  (10 scans/min/user)',
    '4.  Cache hit?  ->  return instantly, still save to MongoDB history',
    '5.  Cache miss  ->  run predict(url) in asyncio thread executor',
    '6.  9 heuristic checks run concurrently via ThreadPoolExecutor',
    '7.  XGBoost computes P(phishing)  +  SHAP values',
    '8.  Trust calibration + score fusion  ->  final_score (0-100)',
    '9.  Full result saved to MongoDB  scans  collection',
    '10. Result cached in Redis  (TTL: 1 hour)',
    '11. SSE stream emits progress events + "done" event with result JSON',
    '12. React renders ResultCard: score / verdict / signals / SHAP chart',
    '13. User clicks Download PDF  ->  GET /api/scans/{id}/report',
    '14. Backend rebuilds PredictionResult from MongoDB  ->  PDF streamed',
]
for i, s in enumerate(steps):
    col = '#60a5fa' if i % 2 == 0 else '#94a3b8'
    txt(ax, 0.7, 9.45 - i * 0.32, s, size=6.8, color=col, ha='left')

# LEGEND
legend_items = [
    ('#3b82f6', 'React Frontend'),
    ('#8b5cf6', 'FastAPI Backend'),
    ('#16a34a', 'MongoDB'),
    ('#dc2626', 'Redis'),
    ('#0ea5e9', 'ML Engine (src/)'),
]
for i, (c, label) in enumerate(legend_items):
    lx = 0.9 + i * 4.0
    box(ax, lx, 4.75, 3.6, 0.35, c+'22', c, lw=1, radius=0.1)
    txt(ax, lx+1.8, 4.925, label, size=7.5, color=c)

plt.tight_layout(pad=0)
out = os.path.join('outputs', 'phishguard_architecture.png')
plt.savefig(out, dpi=150, bbox_inches='tight',
            facecolor='#0f172a', edgecolor='none')
print(f'Saved: {os.path.abspath(out)}')
