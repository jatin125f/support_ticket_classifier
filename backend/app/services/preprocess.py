import re


def preprocess_text(text: str) -> str:
    """
    Clean and normalize customer support ticket text.
    """

    # Convert to lowercase
    text = text.lower()

    # Remove special characters and numbers
    text = re.sub(r"[^a-z\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


if __name__ == "__main__":
    sample = "My PAYMENT was deducted!!! 😭"
    print("Original :", sample)
    print("Processed:", preprocess_text(sample))