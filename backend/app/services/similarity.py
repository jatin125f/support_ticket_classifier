import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample", "tickets.csv")


def find_similar_tickets(text: str, top_k: int = 3, exclude_text: str = None) -> list:
    """
    Find the most similar historical customer tickets.
    Excludes identical/self ticket text if exclude_text is provided or if exact match.
    """
    if not os.path.exists(DATA_PATH):
        return []

    # Load historical tickets
    df = pd.read_csv(DATA_PATH)
    if df.empty:
        return []

    # Target text for self-exclusion
    target_clean = (exclude_text or text).strip().lower()

    # Combine new ticket with existing tickets
    all_text = [text] + df["text"].tolist()

    # Convert text into TF-IDF vectors
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2)
    )

    vectors = vectorizer.fit_transform(all_text)

    # Compare new ticket with previous tickets
    similarities = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    )[0]

    # Add similarity scores
    df["similarity"] = similarities

    # Filter out tickets with 0 similarity
    matches = df[df["similarity"] > 0].copy()

    # Avoid showing the ticket itself as a similar ticket
    matches = matches[matches["text"].str.strip().str.lower() != target_clean]

    results = matches.sort_values(
        by="similarity",
        ascending=False
    ).head(top_k)

    # Convert results to list
    similar_tickets = []
    for _, row in results.iterrows():
        similar_tickets.append({
            "id": int(row["id"]),
            "text": row["text"],
            "category": row["category"],
            "priority": row["priority"],
            "similarity": round(float(row["similarity"]), 2)
        })

    return similar_tickets


if __name__ == "__main__":
    ticket = "My card was charged twice"
    results = find_similar_tickets(ticket)

    print("\n===== SIMILARITY SEARCH =====")
    print("\nNew Ticket:", ticket)
    if results:
        for result in results:
            print("\nSimilar Ticket ID:", result["id"])
            print("Text:", result["text"])
            print("Category:", result["category"])
            print("Priority:", result["priority"])
            print("Similarity:", result["similarity"])
    else:
        print("\nNo similar tickets found.")