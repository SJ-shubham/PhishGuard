"""
PhishGuard - Model Training Script
===================================
Trains an XGBoost classifier on the PhiUSIIL Phishing URL Dataset.

Dataset:  dataset/PhiUSIIL_Phishing_URL_Dataset.csv
Output:   models/phishguard_model.pkl
          models/feature_list.pkl
          models/eval_report.txt

Feature categories
------------------
URL-level (static, no page download needed):
  URLLength, DomainLength, IsDomainIP, TLDLegitimateProb, URLCharProb,
  TLDLength, NoOfSubDomain, HasObfuscation, NoOfObfuscatedChar,
  ObfuscationRatio, NoOfLettersInURL, LetterRatioInURL, NoOfDegitsInURL,
  DegitRatioInURL, NoOfEqualsInURL, NoOfQMarkInURL, NoOfAmpersandInURL,
  NoOfOtherSpecialCharsInURL, SpacialCharRatioInURL, IsHTTPS,
  CharContinuationRate

Content-level (require fetching the page):
  LineOfCode, LargestLineLength, HasTitle, DomainTitleMatchScore,
  URLTitleMatchScore, HasFavicon, Robots, IsResponsive, NoOfURLRedirect,
  NoOfSelfRedirect, HasDescription, NoOfPopup, NoOfiFrame,
  HasExternalFormSubmit, HasSocialNet, HasSubmitButton, HasHiddenFields,
  HasPasswordField, Bank, Pay, Crypto, HasCopyrightInfo, NoOfImage,
  NoOfCSS, NoOfJS, NoOfSelfRef, NoOfEmptyRef, NoOfExternalRef

Excluded:
  URLSimilarityIndex — excluded because in this dataset every legitimate
  URL has exactly 100.0 (std=0), making it a proxy for the label itself.
  It cannot be computed reliably for unseen URLs without a whitelist.
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # non-interactive backend

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
)
from xgboost import XGBClassifier

# ── Paths ────────────────────────────────────────────────────────────────────
DATASET_PATH = os.path.join("dataset", "PhiUSIIL_Phishing_URL_Dataset.csv")
MODEL_DIR    = "models"
MODEL_PATH   = os.path.join(MODEL_DIR, "phishguard_model.pkl")
FEAT_PATH    = os.path.join(MODEL_DIR, "feature_list.pkl")
REPORT_PATH  = os.path.join(MODEL_DIR, "eval_report.txt")
PLOTS_DIR    = os.path.join(MODEL_DIR, "plots")

# ── Columns to drop before training ─────────────────────────────────────────
# Non-numeric identifiers
DROP_COLS = ["FILENAME", "URL", "Domain", "TLD", "Title"]
# Leaky feature: all legitimate URLs have value=100.0 (std=0) in this dataset
DROP_COLS += ["URLSimilarityIndex"]
TARGET    = "label"


def load_data(path: str):
    print(f"[1/6] Loading dataset from: {path}")
    df = pd.read_csv(path)
    print(f"      Rows: {len(df):,}  |  Columns: {df.shape[1]}")
    print(f"      Label distribution -> {df[TARGET].value_counts().to_dict()}")
    return df


def prepare_features(df: pd.DataFrame):
    print("[2/6] Preparing features ...")
    df = df.drop(columns=DROP_COLS, errors="ignore")
    X = df.drop(columns=[TARGET])
    y = df[TARGET]
    print(f"      Feature count: {X.shape[1]}")
    print(f"      Features: {list(X.columns)}")
    return X, y


def split_data(X, y, test_size=0.2, random_state=42):
    print(f"[3/6] Splitting data  (test={int(test_size*100)}%, stratified) ...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    print(f"      Train: {len(X_train):,}  |  Test: {len(X_test):,}")
    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train):
    print("[4/6] Training XGBoost model ...")

    # Hyperparameters tuned for phishing detection on tabular URL data
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
        scale_pos_weight=1,        # labels are roughly balanced
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
        tree_method="hist",        # faster on large datasets
    )

    t0 = time.time()
    model.fit(
        X_train, y_train,
        verbose=False
    )
    elapsed = time.time() - t0
    print(f"      Training complete in {elapsed:.1f}s")
    return model


def evaluate_model(model, X_train, X_test, y_train, y_test, feature_names):
    print("[5/6] Evaluating model ...")

    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec  = recall_score(y_test, y_pred)
    f1   = f1_score(y_test, y_pred)
    auc  = roc_auc_score(y_test, y_proba)

    # 5-fold cross-validation on training set (F1)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1", n_jobs=-1)

    lines = [
        "=" * 60,
        "  PhishGuard — Model Evaluation Report",
        "=" * 60,
        "",
        "  Test-set Metrics",
        "  -----------------",
        f"  Accuracy  : {acc:.4f}  ({acc*100:.2f}%)",
        f"  Precision : {prec:.4f}",
        f"  Recall    : {rec:.4f}",
        f"  F1 Score  : {f1:.4f}",
        f"  AUC-ROC   : {auc:.4f}",
        "",
        "  5-Fold CV F1 (on train set)",
        "  ----------------------------",
        f"  Mean F1   : {cv_scores.mean():.4f}",
        f"  Std F1    : {cv_scores.std():.4f}",
        f"  Per-fold  : {[round(s, 4) for s in cv_scores]}",
        "",
        "  Classification Report",
        "  ----------------------",
        classification_report(y_test, y_pred,
                              target_names=["Phishing (0)", "Legitimate (1)"]),
        "=" * 60,
    ]

    report = "\n".join(lines)
    print()
    print(report)

    os.makedirs(PLOTS_DIR, exist_ok=True)

    # ── Confusion matrix ─────────────────────────────────────────────────────
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                  display_labels=["Phishing", "Legitimate"])
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Confusion Matrix — PhishGuard XGBoost", fontsize=13, pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "confusion_matrix.png"), dpi=150)
    plt.close()
    print(f"      Saved: {os.path.join(PLOTS_DIR, 'confusion_matrix.png')}")

    # ── Top-20 feature importances ───────────────────────────────────────────
    importances = model.feature_importances_
    feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 7))
    feat_imp.head(20).plot(kind="barh", ax=ax, color="#2563EB")
    ax.invert_yaxis()
    ax.set_xlabel("Importance Score (Gain)", fontsize=11)
    ax.set_title("Top-20 Feature Importances — XGBoost", fontsize=13, pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "feature_importances.png"), dpi=150)
    plt.close()
    print(f"      Saved: {os.path.join(PLOTS_DIR, 'feature_importances.png')}")

    # ── Prediction probability distribution ──────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(y_proba[y_test == 0], bins=50, alpha=0.65, color="#EF4444", label="Phishing")
    ax.hist(y_proba[y_test == 1], bins=50, alpha=0.65, color="#22C55E", label="Legitimate")
    ax.axvline(0.5, color="black", linestyle="--", linewidth=1.2, label="Threshold 0.5")
    ax.set_xlabel("Predicted Probability (Legitimate)", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title("Score Distribution — Phishing vs Legitimate", fontsize=13, pad=12)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "score_distribution.png"), dpi=150)
    plt.close()
    print(f"      Saved: {os.path.join(PLOTS_DIR, 'score_distribution.png')}")

    return report, feat_imp


def save_artifacts(model, feature_names, report):
    print("[6/6] Saving model artifacts ...")
    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(list(feature_names), FEAT_PATH)

    with open(REPORT_PATH, "w") as f:
        f.write(report)

    print(f"      Model   -> {MODEL_PATH}")
    print(f"      Features-> {FEAT_PATH}")
    print(f"      Report  -> {REPORT_PATH}")


def main():
    print()
    print("=" * 60)
    print("  PhishGuard — Training Pipeline")
    print("=" * 60)
    print()

    df = load_data(DATASET_PATH)
    X, y = prepare_features(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    model = train_model(X_train, y_train)
    report, feat_imp = evaluate_model(
        model, X_train, X_test, y_train, y_test, X.columns
    )
    save_artifacts(model, X.columns, report)

    print()
    print("  Top-10 most important features:")
    for feat, score in feat_imp.head(10).items():
        print(f"    {feat:<35} {score:.4f}")

    print()
    print("  Training complete.")
    print()


if __name__ == "__main__":
    main()