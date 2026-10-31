import os
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample", "tickets.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "ticket_classifier.pkl")


def train_model():
    # Load dataset
    df = pd.read_csv(DATA_PATH)

    X = df["text"]
    y = df["category"]

    # TF-IDF + Logistic Regression
    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )),
        ("classifier", LogisticRegression(
            max_iter=1000
        ))
    ])

    # Train model
    model.fit(X, y)

    # Save model
    joblib.dump(model, MODEL_PATH)

    print("Model trained successfully!")
    print(f"Model saved at: {MODEL_PATH}")
    return model


if __name__ == "__main__":
    train_model()