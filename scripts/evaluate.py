import os
import sys
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.ai.hybrid_engine import hybrid_classify
from backend.app.services.ml_classifier import classify_with_ml

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sample", "tickets.csv"))


def evaluate_system():
    if not os.path.exists(DATA_PATH):
        print(f"Dataset not found at {DATA_PATH}")
        return None

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} sample tickets from {DATA_PATH}")

    y_true = df["category"].tolist()
    y_pred_hybrid = []
    y_pred_ml = []
    methods_used = []

    for text in df["text"]:
        # Hybrid prediction
        hybrid_res = hybrid_classify(text)
        y_pred_hybrid.append(hybrid_res["category"])
        methods_used.append(hybrid_res["method"])

        # ML-only prediction
        ml_res = classify_with_ml(text)
        y_pred_ml.append(ml_res["category"])

    hybrid_acc = accuracy_score(y_true, y_pred_hybrid)
    ml_acc = accuracy_score(y_true, y_pred_ml)

    print("\n" + "=" * 60)
    print("HYBRID AI ENGINE EVALUATION REPORT")
    print("=" * 60)
    print(f"Total Test Samples: {len(df)}")
    print(f"Hybrid Engine Overall Accuracy: {hybrid_acc * 100:.2f}%")
    print(f"ML Classifier Baseline Accuracy: {ml_acc * 100:.2f}%")
    print("\nMethod Distribution during inference:")
    method_series = pd.Series(methods_used).value_counts()
    for method, count in method_series.items():
        print(f"  - {method}: {count} ({count/len(df)*100:.1f}%)")

    print("\nDetailed Classification Report (Hybrid Engine):")
    report = classification_report(y_true, y_pred_hybrid, zero_division=0)
    print(report)

    cm = confusion_matrix(y_true, y_pred_hybrid, labels=sorted(list(set(y_true))))
    labels = sorted(list(set(y_true)))
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    print("Confusion Matrix:")
    print(cm_df)

    return {
        "total_samples": len(df),
        "hybrid_accuracy": round(float(hybrid_acc), 4),
        "ml_accuracy": round(float(ml_acc), 4),
        "classification_report": report,
        "method_distribution": method_series.to_dict()
    }


if __name__ == "__main__":
    evaluate_system()
