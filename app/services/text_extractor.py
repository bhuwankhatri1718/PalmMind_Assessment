
from pathlib import Path

import fitz


def extract_text(file_path: Path) -> str:
    """
    Extract text from a PDF or TXT document.
    """

    file_extension = file_path.suffix.lower()

    if file_extension == ".pdf":
        extracted_text = []

        with fitz.open(file_path) as pdf:
            for page in pdf:
                extracted_text.append(page.get_text())

        text = "\n".join(extracted_text)

    elif file_extension == ".txt":
        text = file_path.read_text(encoding="utf-8")

    else:
        raise ValueError("Only PDF and TXT files are supported.")

    if not text.strip():
        raise ValueError("The uploaded document contains no extractable text.")

    return text.strip()
