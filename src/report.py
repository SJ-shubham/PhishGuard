"""
Deterministic PDF Report Engine — PhishGuard
=============================================
Generates a professional A4 PDF from a PredictionResult.
No external AI API required — all content is derived deterministically
from the ML + heuristic pipeline outputs.

Report sections
---------------
1. Header          — PhishGuard branding, URL, timestamp, report ID
2. Risk Summary    — Score meter, verdict badge, ML probability, trust factor
3. Score Breakdown — Per-signal contribution table (all 11 signals)
4. Heuristic Findings — Detailed result of every heuristic check
5. SHAP Attribution   — Top ML risk / safe feature contributions
                        (embeds waterfall PNG if path is supplied)
6. Recommendations    — Deterministic, flag-driven security advice
7. Technical Appendix — All 49 extracted ML feature values

Usage
-----
  from src.report import generate_report
  pdf_path = generate_report(result, output_dir="outputs/reports")
  # optionally: generate_report(result, shap_image="outputs/shap/...waterfall.png")
"""

import os
import re
import hashlib
import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Image,
)

# ── Layout ────────────────────────────────────────────────────────────────────
_PAGE_W, _PAGE_H = A4
_LM = _RM = 50.0
_TM = _BM = 45.0
_INNER_W = _PAGE_W - _LM - _RM

# ── Color palette ─────────────────────────────────────────────────────────────
_NAVY   = colors.HexColor("#1a2332")
_NAVY2  = colors.HexColor("#243447")
_WHITE  = colors.white
_OFF_W  = colors.HexColor("#f8f9fc")
_LGRAY  = colors.HexColor("#ecf0f1")
_DGRAY  = colors.HexColor("#95a5a6")
_BLACK  = colors.HexColor("#2c3e50")

_LEVEL = {
    "Low":      {"fg": colors.HexColor("#27ae60"), "bg": colors.HexColor("#d5f5e3")},
    "Medium":   {"fg": colors.HexColor("#e67e22"), "bg": colors.HexColor("#fef9e7")},
    "High":     {"fg": colors.HexColor("#e74c3c"), "bg": colors.HexColor("#fdebd0")},
    "Critical": {"fg": colors.HexColor("#c0392b"), "bg": colors.HexColor("#fadbd8")},
}

# ── Paragraph styles (module-level, built once) ───────────────────────────────
_ST = {
    "hdr_title":  ParagraphStyle("hdr_title",  fontName="Helvetica-Bold", fontSize=18,
                                  textColor=colors.white, leading=22),
    "hdr_sub":    ParagraphStyle("hdr_sub",    fontName="Helvetica",      fontSize=8.5,
                                  textColor=colors.HexColor("#bdc3c7"), leading=12),
    "hdr_sub_r":  ParagraphStyle("hdr_sub_r",  fontName="Helvetica",      fontSize=8.5,
                                  textColor=colors.HexColor("#bdc3c7"), leading=12,
                                  alignment=TA_RIGHT),
    "url_p":      ParagraphStyle("url_p",      fontName="Courier",        fontSize=8.5,
                                  textColor=colors.HexColor("#2980b9"),  leading=12),
    "section":    ParagraphStyle("section",    fontName="Helvetica-Bold", fontSize=11,
                                  textColor=colors.HexColor("#1a2332"),
                                  spaceBefore=14, spaceAfter=5),
    "body":       ParagraphStyle("body",       fontName="Helvetica",      fontSize=9,
                                  textColor=_BLACK, spaceAfter=3, leading=13),
    "small":      ParagraphStyle("small",      fontName="Helvetica",      fontSize=8,
                                  textColor=_DGRAY, spaceAfter=2, leading=11),
    "mono":       ParagraphStyle("mono",       fontName="Courier",        fontSize=8,
                                  textColor=_BLACK, leading=11),
    "verdict_p":  ParagraphStyle("verdict_p",  fontName="Helvetica-Bold", fontSize=15,
                                  textColor=colors.white, alignment=TA_CENTER, leading=20),
    "score_p":    ParagraphStyle("score_p",    fontName="Helvetica-Bold", fontSize=46,
                                  alignment=TA_CENTER, leading=50),
    "th":         ParagraphStyle("th",         fontName="Helvetica-Bold", fontSize=8.5,
                                  textColor=colors.white),
    "th_c":       ParagraphStyle("th_c",       fontName="Helvetica-Bold", fontSize=8.5,
                                  textColor=colors.white, alignment=TA_CENTER),
    "td":         ParagraphStyle("td",         fontName="Helvetica",      fontSize=8.5,
                                  textColor=_BLACK,  leading=11),
    "td_b":       ParagraphStyle("td_b",       fontName="Helvetica-Bold", fontSize=8.5,
                                  textColor=_BLACK,  leading=11),
    "td_c":       ParagraphStyle("td_c",       fontName="Helvetica",      fontSize=8.5,
                                  textColor=_BLACK,  leading=11, alignment=TA_CENTER),
    "td_r":       ParagraphStyle("td_r",       fontName="Helvetica-Bold", fontSize=8.5,
                                  textColor=colors.HexColor("#c0392b"), leading=11),
    "td_g":       ParagraphStyle("td_g",       fontName="Helvetica-Bold", fontSize=8.5,
                                  textColor=colors.HexColor("#27ae60"), leading=11),
    "td_gr":      ParagraphStyle("td_gr",      fontName="Helvetica",      fontSize=8.5,
                                  textColor=_DGRAY,  leading=11),
    "td_mono":    ParagraphStyle("td_mono",    fontName="Courier",        fontSize=7.5,
                                  textColor=_BLACK,  leading=10),
    "bullet":     ParagraphStyle("bullet",     fontName="Helvetica",      fontSize=9,
                                  textColor=_BLACK, leftIndent=16, spaceAfter=5, leading=13),
    "rec_warn":   ParagraphStyle("rec_warn",   fontName="Helvetica",      fontSize=9,
                                  textColor=colors.HexColor("#922b21"),
                                  leftIndent=16, spaceAfter=6, leading=13),
    "rec_ok":     ParagraphStyle("rec_ok",     fontName="Helvetica",      fontSize=9,
                                  textColor=colors.HexColor("#1d8348"),
                                  leftIndent=16, spaceAfter=6, leading=13),
}

_TS_HDR = TableStyle([   # common table header row style
    ("BACKGROUND",    (0, 0), (-1, 0), _NAVY),
    ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
    ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE",      (0, 0), (-1, 0), 8.5),
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 7),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [_OFF_W, _LGRAY]),
    ("BOX",           (0, 0), (-1, -1), 0.5, _DGRAY),
    ("LINEBELOW",     (0, 0), (-1, 0),  0.8, _DGRAY),
    ("LINEBELOW",     (0, 1), (-1, -2), 0.3, _LGRAY),
])


# ── Utilities ─────────────────────────────────────────────────────────────────

def _safe_stem(url: str) -> str:
    name = re.sub(r"https?://", "", url)
    name = re.sub(r"[^\w\-.]", "_", name)
    return name[:50]


def _report_id(url: str) -> str:
    h = hashlib.md5(url.encode()).hexdigest()[:8].upper()
    return f"PG-{datetime.datetime.now().strftime('%Y%m%d')}-{h}"


def _bool_cell(val: bool, true_is_bad: bool = False) -> Paragraph:
    """Colored True/False cell."""
    if val:
        style = _ST["td_r"] if true_is_bad else _ST["td_g"]
        text  = "Yes" if true_is_bad else "Yes"
    else:
        style = _ST["td_g"] if true_is_bad else _ST["td_r"]
        text  = "No"
    return Paragraph(text, style)


def _shap_bar(val: float, width: int = 18) -> str:
    """Text bar for SHAP value."""
    n = min(int(abs(val) / 0.4 * width), width)
    return "█" * n + "░" * (width - n)


def _score_bar_cells(score: float, level: str) -> Table:
    """Colored horizontal progress bar as a 2-cell table."""
    filled = max(int(round(score / 100 * _INNER_W)), 2)
    empty  = _INNER_W - filled
    fg     = _LEVEL.get(level, _LEVEL["Critical"])["fg"]
    t = Table([["", ""]], colWidths=[filled, empty])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), fg),
        ("BACKGROUND", (1, 0), (1, 0), _LGRAY),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    return t


# ── Footer ────────────────────────────────────────────────────────────────────

def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(_DGRAY)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    canvas.drawString(_LM, 22, f"PhishGuard Security Report  •  {ts}")
    canvas.drawRightString(_PAGE_W - _RM, 22, f"Page {doc.page}")
    canvas.setStrokeColor(_LGRAY)
    canvas.setLineWidth(0.5)
    canvas.line(_LM, 30, _PAGE_W - _RM, 30)
    canvas.restoreState()


# ── Section 1: Header ─────────────────────────────────────────────────────────

def _section_header(result, rid: str) -> list:
    ts = datetime.datetime.now().strftime("%d %B %Y  %H:%M")

    left  = [Paragraph("PhishGuard", _ST["hdr_title"]),
              Paragraph("URL Security Analysis Report", _ST["hdr_sub"])]
    right = [Paragraph(f"Report ID: <b>{rid}</b>", _ST["hdr_sub_r"]),
              Paragraph(f"Generated: {ts}", _ST["hdr_sub_r"])]

    hdr = Table([[left, right]], colWidths=[_INNER_W * 0.6, _INNER_W * 0.4])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _NAVY),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("ALIGN",         (1, 0), (1,  0),  "RIGHT"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))

    url_row = Table(
        [[Paragraph("Analyzed URL", _ST["small"]),
          Paragraph(result.url, _ST["url_p"])]],
        colWidths=[78, _INNER_W - 78],
    )
    url_row.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), _NAVY2),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    return [hdr, url_row, Spacer(1, 12)]


# ── Section 2: Risk Summary ───────────────────────────────────────────────────

def _section_risk_summary(result) -> list:
    score   = result.risk_score
    level   = result.risk_level
    verdict = result.verdict
    lc      = _LEVEL.get(level, _LEVEL["Critical"])
    fg, bg  = lc["fg"], lc["bg"]

    # Score number
    score_cell = Paragraph(
        f'<font color="#{fg.hexval()[2:]}">{score:.1f}</font>', _ST["score_p"]
    )
    label_cell = Paragraph(
        f'<font color="#{_DGRAY.hexval()[2:]}">out of 100</font>',
        ParagraphStyle("sc_lbl", fontName="Helvetica", fontSize=9,
                       alignment=TA_CENTER, leading=12),
    )

    # Verdict badge
    verdict_badge = Table([[Paragraph(verdict, _ST["verdict_p"])]],
                          colWidths=[_INNER_W * 0.45])
    verdict_badge.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), fg),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    level_label = Paragraph(
        f'Risk Level: <b>{level}</b>',
        ParagraphStyle("ll", fontName="Helvetica", fontSize=9.5,
                       alignment=TA_CENTER, textColor=fg),
    )

    # Stats row: ML probabilities + trust factor + elapsed
    tf      = result.score_breakdown.get("trust_factor", 1.0)
    elapsed = result.elapsed_sec
    stats_data = [
        [Paragraph("ML P(phishing)",  _ST["small"]),
         Paragraph("ML P(legitimate)",_ST["small"]),
         Paragraph("Trust Factor",    _ST["small"]),
         Paragraph("Analysis Time",   _ST["small"])],
        [Paragraph(f"<b>{result.phishing_prob:.4f}</b>",  _ST["td_b"]),
         Paragraph(f"<b>{result.legitimate_prob:.4f}</b>", _ST["td_b"]),
         Paragraph(f"<b>{tf:.2f}</b>",                    _ST["td_b"]),
         Paragraph(f"<b>{elapsed}s</b>",                  _ST["td_b"])],
    ]
    stats = Table(stats_data, colWidths=[_INNER_W / 4] * 4)
    stats.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND",    (0, 0), (-1, 0),  _LGRAY),
        ("BACKGROUND",    (0, 1), (-1, 1),  _OFF_W),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BOX",           (0, 0), (-1, -1), 0.5, _DGRAY),
        ("LINEBELOW",     (0, 0), (-1, 0),  0.5, _DGRAY),
    ]))

    # Left: score number; Right: verdict badge + risk level
    right_content = [verdict_badge, Spacer(1, 5), level_label]
    summary = Table(
        [[score_cell, right_content]],
        colWidths=[_INNER_W * 0.30, _INNER_W * 0.70],
    )
    summary.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (1,  0),  "CENTER"),
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("BOX",           (0, 0), (-1, -1), 0.8, fg),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))

    bar = _score_bar_cells(score, level)
    bar_label = Paragraph(
        f"Risk Score: {score:.1f}/100",
        ParagraphStyle("bl", fontName="Helvetica", fontSize=7.5,
                       textColor=_DGRAY, alignment=TA_RIGHT),
    )

    return [
        Paragraph("Risk Summary", _ST["section"]),
        HRFlowable(width=_INNER_W, thickness=1, color=_LGRAY),
        Spacer(1, 8),
        summary,
        Spacer(1, 4),
        bar,
        bar_label,
        Spacer(1, 10),
        stats,
        Spacer(1, 14),
    ]


# ── Section 3: Score Breakdown ────────────────────────────────────────────────

def _section_score_breakdown(result) -> list:
    bd = result.score_breakdown

    rows = [[
        Paragraph("Signal",          _ST["th"]),
        Paragraph("Points Scored",   _ST["th_c"]),
        Paragraph("Max Points",      _ST["th_c"]),
        Paragraph("Status",          _ST["th_c"]),
    ]]

    signals = [
        ("ML Base (trust-calibrated)",  bd.get("ml_base",            0), 60),
        ("Brand Impersonation",         bd.get("brand_impersonation", 0), 30),
        ("IP-based URL",                bd.get("ip_based_url",        0), 30),
        ("IP in Subdomain",             bd.get("ip_in_subdomain",     0), 25),
        ("Suspicious TLD",              bd.get("suspicious_tld",      0), 20),
        ("Punycode / IDN",              bd.get("punycode_idn",        0), 20),
        ("Domain Age",                  bd.get("domain_age",          0), 20),
        ("Content Indicators",          bd.get("content_indicators",  0), 20),
        ("SSL Failure",                 bd.get("ssl_failure",         0), 15),
        ("DNS Failure",                 bd.get("dns_failure",         0), 15),
        ("Keyword Signals",             bd.get("keyword_signals",     0), 15),
    ]

    for name, val, max_val in signals:
        triggered = val > 0
        val_p   = Paragraph(f"{val:.2f}", _ST["td_r"] if triggered else _ST["td_gr"])
        max_p   = Paragraph(f"{max_val}", _ST["td_c"])
        label_p = Paragraph(name, _ST["td_b"] if triggered else _ST["td"])
        status_p = Paragraph(
            "TRIGGERED" if triggered else "—",
            _ST["td_r"] if triggered else _ST["td_gr"],
        )
        rows.append([label_p, val_p, max_p, status_p])

    # Totals row
    rows.append([
        Paragraph("Raw Total / Final Score", _ST["td_b"]),
        Paragraph(f"{bd.get('raw_total', 0):.2f} → {bd.get('final_score', 0):.2f}",
                  _ST["td_b"]),
        Paragraph("150 → 100", _ST["td_c"]),
        Paragraph("", _ST["td"]),
    ])

    t = Table(rows, colWidths=[_INNER_W * 0.44, _INNER_W * 0.20,
                                _INNER_W * 0.18, _INNER_W * 0.18])
    t.setStyle(TableStyle(list(_TS_HDR.getCommands()) + [
        ("ALIGN",      (1, 0), (3, -1), "CENTER"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d6eaf8")),
        ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))

    return [
        Paragraph("Score Breakdown", _ST["section"]),
        HRFlowable(width=_INNER_W, thickness=1, color=_LGRAY),
        Spacer(1, 6),
        t,
        Spacer(1, 14),
    ]


# ── Section 4: Heuristic Findings ─────────────────────────────────────────────

def _section_heuristic_findings(result) -> list:
    hf = result.heuristic_flags

    def _yn(val, bad_if_true: bool = False):
        if val is None:
            return Paragraph("N/A", _ST["td_gr"])
        if isinstance(val, bool):
            if bad_if_true:
                return Paragraph("Yes" if val else "No",
                                 _ST["td_r"] if val else _ST["td_g"])
            else:
                return Paragraph("Yes" if val else "No",
                                 _ST["td_g"] if val else _ST["td_r"])
        return Paragraph(str(val), _ST["td"])

    rows = [[
        Paragraph("Check",   _ST["th"]),
        Paragraph("Result",  _ST["th_c"]),
        Paragraph("Detail",  _ST["th"]),
    ]]

    # DNS
    detail = hf.get("dns_error", "") or (f"IP: {hf.get('ip_address','')}" if hf.get("ip_address") else "Resolved OK")
    rows.append([Paragraph("DNS Resolution",    _ST["td"]),
                 _yn(hf.get("dns_resolves")),
                 Paragraph(str(detail), _ST["td"])])

    # SSL
    ssl_detail = hf.get("ssl_error", "Valid certificate") if not hf.get("ssl_valid") else "Valid HTTPS certificate"
    rows.append([Paragraph("SSL / TLS",         _ST["td"]),
                 _yn(hf.get("ssl_valid")),
                 Paragraph(str(ssl_detail), _ST["td"])])

    # HTTPS
    rows.append([Paragraph("Uses HTTPS",        _ST["td"]),
                 _yn(hf.get("is_https")),
                 Paragraph("Secure transport" if hf.get("is_https") else "Plain HTTP — no encryption", _ST["td"])])

    # Brand
    brand_detail = ""
    if hf.get("brand_impersonation"):
        bm = hf.get("brand_matched", "")
        bd = hf.get("brand_distance", 0)
        brand_detail = (f"Homoglyph of {bm.title()}" if bd == 0
                        else f"Typosquat of {bm.title()} (dist={bd})")
    else:
        brand_detail = "No brand impersonation found"
    rows.append([Paragraph("Brand Impersonation", _ST["td"]),
                 _yn(hf.get("brand_impersonation"), bad_if_true=True),
                 Paragraph(brand_detail, _ST["td"])])

    # Domain age
    age_days    = hf.get("domain_age_days", -1)
    age_created = hf.get("domain_created", "unknown")
    age_detail  = (f"Created: {age_created}  ({age_days} days ago)"
                   if age_days and age_days > 0 else "WHOIS unavailable")
    rows.append([Paragraph("Domain Age",        _ST["td"]),
                 _yn(hf.get("domain_is_new"), bad_if_true=True),
                 Paragraph(age_detail, _ST["td"])])

    # TLD
    tld_val = hf.get("tld", "")
    rows.append([Paragraph("Suspicious TLD",    _ST["td"]),
                 _yn(hf.get("suspicious_tld"), bad_if_true=True),
                 Paragraph(f".{tld_val}" if tld_val else "—", _ST["td"])])

    # IP in subdomain
    ip_detail = hf.get("detected_ip", "—") if hf.get("ip_in_subdomain") else "Not detected"
    rows.append([Paragraph("IP in Subdomain",   _ST["td"]),
                 _yn(hf.get("ip_in_subdomain"), bad_if_true=True),
                 Paragraph(ip_detail, _ST["td"])])

    # Keywords
    kws = hf.get("found_keywords", [])
    kw_detail = ", ".join(kws) if kws else "No phishing keywords found"
    rows.append([Paragraph("Phishing Keywords", _ST["td"]),
                 _yn(hf.get("suspicious_keywords"), bad_if_true=True),
                 Paragraph(kw_detail, _ST["td"])])

    # Punycode
    pparts = hf.get("punycode_parts", [])
    pun_detail = ", ".join(pparts) if pparts else "No IDN encoding detected"
    rows.append([Paragraph("Punycode / IDN",    _ST["td"]),
                 _yn(hf.get("has_punycode"), bad_if_true=True),
                 Paragraph(pun_detail, _ST["td"])])

    # Path
    path_flags = hf.get("path_flags", [])
    path_detail = ", ".join(path_flags) if path_flags else "No suspicious path patterns"
    rows.append([Paragraph("Suspicious Path",   _ST["td"]),
                 _yn(hf.get("path_is_suspicious"), bad_if_true=True),
                 Paragraph(path_detail, _ST["td"])])

    t = Table(rows, colWidths=[_INNER_W * 0.30, _INNER_W * 0.14, _INNER_W * 0.56])
    t.setStyle(TableStyle(list(_TS_HDR.getCommands()) + [
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
    ]))

    return [
        Paragraph("Heuristic Findings", _ST["section"]),
        HRFlowable(width=_INNER_W, thickness=1, color=_LGRAY),
        Spacer(1, 6),
        t,
        Spacer(1, 14),
    ]


# ── Section 5: SHAP Attribution ───────────────────────────────────────────────

def _section_shap(result, shap_image: Optional[str] = None) -> list:
    shap = result.shap_explanation
    if shap is None:
        return []

    elements = [
        Paragraph("SHAP Feature Attribution", _ST["section"]),
        HRFlowable(width=_INNER_W, thickness=1, color=_LGRAY),
        Spacer(1, 4),
        Paragraph(
            f"Base value (model average): <b>{shap.base_value:+.4f}</b> log-odds  |  "
            f"Final prediction value: <b>{shap.prediction_value:+.4f}</b> log-odds",
            _ST["body"],
        ),
        Paragraph(
            "Positive SHAP → pushes toward Legitimate.  "
            "Negative SHAP → pushes toward Phishing.",
            _ST["small"],
        ),
        Spacer(1, 6),
    ]

    # SHAP table: top risk + top safe features
    rows = [[Paragraph("Feature", _ST["th"]),
             Paragraph("SHAP Value", _ST["th_c"]),
             Paragraph("Direction", _ST["th_c"]),
             Paragraph("Strength", _ST["th"])]]

    combined = (
        [(f, v, "Phishing")   for f, v in shap.top_risk_features[:8]] +
        [(f, v, "Legitimate") for f, v in shap.top_safe_features[:6]]
    )

    for feat, val, direction in combined:
        is_risk = direction == "Phishing"
        val_p   = Paragraph(f"{val:+.4f}", _ST["td_r"] if is_risk else _ST["td_g"])
        dir_p   = Paragraph(direction,     _ST["td_r"] if is_risk else _ST["td_g"])
        bar_p   = Paragraph(_shap_bar(val), _ST["td_mono"])
        rows.append([Paragraph(feat, _ST["td"]), val_p, dir_p, bar_p])

    t = Table(rows, colWidths=[_INNER_W * 0.40, _INNER_W * 0.14,
                                _INNER_W * 0.16, _INNER_W * 0.30])
    t.setStyle(TableStyle(list(_TS_HDR.getCommands()) + [
        ("ALIGN", (1, 0), (2, -1), "CENTER"),
    ]))
    elements.append(t)

    # Embed waterfall PNG if the file exists
    if shap_image and os.path.isfile(shap_image):
        elements += [
            Spacer(1, 10),
            Paragraph("SHAP Waterfall Plot", _ST["body"]),
            Spacer(1, 4),
            Image(shap_image, width=_INNER_W, height=_INNER_W * 0.55,
                  kind="proportional"),
        ]

    elements.append(Spacer(1, 14))
    return elements


# ── Section 6: Recommendations ────────────────────────────────────────────────

def _build_recommendations(result) -> list[tuple[str, str]]:
    """Return list of (severity, text) tuples. severity: 'warn' | 'ok'."""
    hf   = result.heuristic_flags
    bd   = result.score_breakdown
    recs = []

    if hf.get("brand_impersonation"):
        brand = hf.get("brand_matched", "a known brand")
        dist  = hf.get("brand_distance", 0)
        if dist == 0:
            recs.append(("warn",
                f"CRITICAL — Homoglyph/character-substitution attack targeting "
                f"{brand.title()}. The domain uses lookalike characters (e.g. 0→o, "
                f"1→l) to impersonate a trusted brand. Never enter credentials."))
        else:
            recs.append(("warn",
                f"Typosquat attack — domain is {dist} character edit(s) away from "
                f"{brand.title()}. Registry check confirmed it is NOT the official "
                f"domain. Do not proceed."))

    if hf.get("has_punycode"):
        parts = hf.get("punycode_parts", [])
        recs.append(("warn",
            f"Internationalized Domain Name (Punycode) detected: "
            f"{', '.join(parts)}. This is a homograph attack — the URL may display "
            f"as a trusted domain in your browser's address bar while resolving "
            f"to a completely different server."))

    if hf.get("ip_in_subdomain"):
        ip = hf.get("detected_ip", "")
        recs.append(("warn",
            f"IP address ({ip}) embedded inside the subdomain — a known evasion "
            f"technique to bypass domain-based security filters. The registered "
            f"domain appears legitimate but the actual target is an IP address."))

    if result.features.get("IsDomainIP", 0) == 1:
        recs.append(("warn",
            "URL uses a raw IP address instead of a registered domain name. "
            "Legitimate services always use domain names with valid SSL certificates."))

    if hf.get("suspicious_tld"):
        tld = hf.get("tld", "")
        recs.append(("warn",
            f"The .{tld} top-level domain is heavily associated with phishing "
            f"campaigns, free disposable registrars, or high-abuse registries. "
            f"Treat any site on this TLD with extreme caution."))

    if hf.get("suspicious_keywords"):
        kws = hf.get("found_keywords", [])
        recs.append(("warn",
            f"Phishing-indicative keywords detected in the URL: "
            f"{', '.join(kws)}. Attackers embed these words to create urgency "
            f"and legitimacy. Official services rarely include them in domain names."))

    if not hf.get("ssl_valid"):
        err = hf.get("ssl_error", "")
        recs.append(("warn",
            f"No valid SSL/TLS certificate ({err}). Any credentials or data "
            f"submitted would be transmitted in plaintext and intercepted by "
            f"a network attacker (MITM)."))

    if not hf.get("dns_resolves"):
        recs.append(("warn",
            "Domain does not resolve via DNS. The site is unreachable. This "
            "could be a decommissioned phishing page, a future-dated attack, "
            "or a DNS-based block already in effect."))

    if hf.get("domain_is_new"):
        age = hf.get("domain_age_days", -1)
        recs.append(("warn",
            f"Domain is very recently registered ({age} days ago). Phishing "
            f"campaigns typically register fresh domains immediately before "
            f"launching attacks to avoid reputation-based blacklists."))

    if hf.get("path_is_suspicious"):
        flags = hf.get("path_flags", [])
        recs.append(("warn",
            f"Suspicious URL path structure: {', '.join(flags)}. Long paths, "
            f"random tokens, and excessive query parameters are hallmarks of "
            f"phishing redirect chains and obfuscated tracking URLs."))

    if not recs:
        score = result.risk_score
        if score < 30:
            recs.append(("ok",
                "No significant threat indicators detected across all heuristic "
                "checks. The site has a valid SSL certificate, an established "
                "domain, and no phishing signals in its URL structure. Standard "
                "caution still applies when submitting any credentials online."))
        else:
            recs.append(("ok",
                "Some risk signals present but no specific attack pattern "
                "conclusively identified. Verify this URL matches the official "
                "domain of the service before proceeding."))

    return recs


def _section_recommendations(result) -> list:
    recs = _build_recommendations(result)

    elements = [
        Paragraph("Security Recommendations", _ST["section"]),
        HRFlowable(width=_INNER_W, thickness=1, color=_LGRAY),
        Spacer(1, 6),
    ]

    for severity, text in recs:
        prefix = "⚠  " if severity == "warn" else "✓  "
        style  = _ST["rec_warn"] if severity == "warn" else _ST["rec_ok"]
        elements.append(Paragraph(f"{prefix}{text}", style))

    elements.append(Spacer(1, 14))
    return elements


# ── Section 7: Technical Appendix ─────────────────────────────────────────────

def _section_appendix(result) -> list:
    feats = result.features
    if not feats:
        return []

    # Build 3-column table: feature | value | feature | value | feature | value
    items  = sorted(feats.items())
    n      = len(items)
    ncols  = 3
    nrows  = (n + ncols - 1) // ncols

    hdr_row = []
    for _ in range(ncols):
        hdr_row += [Paragraph("Feature", _ST["th"]),
                    Paragraph("Value",   _ST["th_c"])]

    rows = [hdr_row]
    for r in range(nrows):
        row = []
        for c in range(ncols):
            idx = r + c * nrows
            if idx < n:
                k, v = items[idx]
                v_str = f"{v:.4f}" if isinstance(v, float) else str(v)
                row.append(Paragraph(k, _ST["td"]))
                row.append(Paragraph(v_str, _ST["td_c"]))
            else:
                row += [Paragraph("", _ST["td"]), Paragraph("", _ST["td_c"])]
        rows.append(row)

    col_w_label = _INNER_W / ncols * 0.68
    col_w_val   = _INNER_W / ncols * 0.32
    col_widths  = [col_w_label, col_w_val] * ncols

    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle(list(_TS_HDR.getCommands()) + [
        ("ALIGN",     (1, 0), (-1, -1), "CENTER"),
        ("FONTSIZE",  (0, 1), (-1, -1), 7.5),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    return [
        Paragraph("Technical Appendix — ML Feature Values", _ST["section"]),
        HRFlowable(width=_INNER_W, thickness=1, color=_LGRAY),
        Spacer(1, 4),
        Paragraph(
            "All 49 features extracted from the URL and page content, "
            "used as input to the XGBoost classifier.",
            _ST["small"],
        ),
        Spacer(1, 6),
        t,
        Spacer(1, 10),
    ]


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_report(
    result,
    output_dir: str = "outputs/reports",
    shap_image: Optional[str] = None,
) -> str:
    """
    Generate a PDF report from a PredictionResult.

    Parameters
    ----------
    result     : PredictionResult from src.predictor.predict()
    output_dir : Directory to write the PDF into (created if absent)
    shap_image : Optional path to a SHAP waterfall PNG to embed

    Returns
    -------
    Absolute path to the generated PDF file.
    """
    os.makedirs(output_dir, exist_ok=True)

    stem = _safe_stem(result.url)
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rid  = _report_id(result.url)
    path = os.path.join(output_dir, f"{stem}_{ts}.pdf")

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=_LM, rightMargin=_RM,
        topMargin=_TM,  bottomMargin=_BM,
        title=f"PhishGuard Report — {result.url}",
        author="PhishGuard",
        subject=f"URL Security Analysis — Risk: {result.risk_level}",
    )

    story: list = []
    story += _section_header(result, rid)
    story += _section_risk_summary(result)
    story += _section_score_breakdown(result)
    story += _section_heuristic_findings(result)
    story += _section_shap(result, shap_image)
    story += _section_recommendations(result)
    story += _section_appendix(result)

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return os.path.abspath(path)