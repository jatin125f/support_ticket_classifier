from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Absolute path to knowledge base directory
KB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "knowledge_base"


def load_knowledge_base():
    """
    Load all knowledge base documents from files.
    """
    documents = []

    if not KB_PATH.exists():
        return documents

    for file_path in sorted(KB_PATH.glob("*.txt")):
        try:
            content = file_path.read_text(encoding="utf-8")
            documents.append({
                "name": file_path.stem,
                "title": f"{file_path.stem.capitalize()} Policy & Guidelines",
                "content": content
            })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return documents


def retrieve_knowledge(text: str, top_k: int = 1) -> list:
    """
    Find the most relevant knowledge base documents.
    """
    documents = load_knowledge_base()

    if not documents:
        return []

    contents = [document["content"] for document in documents]
    all_text = [text] + contents

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2)
    )

    vectors = vectorizer.fit_transform(all_text)

    similarities = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    )[0]

    results = []

    for document, similarity in zip(documents, similarities):
        if similarity > 0:
            results.append({
                "name": document["name"],
                "content": document["content"],
                "similarity": round(float(similarity), 2)
            })

    results.sort(key=lambda x: x["similarity"], reverse=True)

    # If no similarity above 0, return the top default doc or empty list
    return results[:top_k]


if __name__ == "__main__":
    ticket = "My payment was deducted but my order is pending"
    results = retrieve_knowledge(ticket)

    print("\n===== KNOWLEDGE BASE TEST =====")
    print("\nTicket:", ticket)
    if results:
        for result in results:
            print("\nDocument:", result["name"])
            print("Similarity:", result["similarity"])
            print("Content:\n", result["content"])
    else:
        print("\nNo relevant knowledge found.")