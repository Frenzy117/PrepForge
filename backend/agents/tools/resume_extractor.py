import os
from io import BytesIO

import docx
import pdfplumber
from langchain_core.tools import tool


def extract_resume_text_bytes(file_bytes: bytes, file_path: str) -> str:
    """Extract plain text from PDF or DOCX bytes."""
    extension = os.path.splitext(file_path)[-1].lower()

    if extension == ".docx":
        try:
            document = docx.Document(BytesIO(file_bytes))
            return "\n".join(para.text for para in document.paragraphs)
        except Exception as e:
            return f"Error processing .docx file: {e}"

    if extension == ".pdf":
        try:
            text = []
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_content = page.extract_text()
                    if page_content:
                        text.append(page_content)
            return "\n".join(text)
        except Exception as e:
            return f"Error processing the PDF file: {e}"

    if extension == ".doc":
        return "DOC format is not supported. Please upload PDF or DOCX."

    return "Unsupported file type. Please upload your CV in .pdf or .docx format."


def extract_resume_text_from_path(file_path: str) -> str:
    """Extract plain text from a local PDF or DOCX file."""
    with open(file_path, "rb") as f:
        return extract_resume_text_bytes(f.read(), file_path)


@tool
def extract_resume_text(file_path: str) -> str:
    """
    Extracts the text content from a CV file in PDF or DOCX format at a local path.

    Args:
        file_path: The local file path to the CV document.

    Returns:
        The extracted plain text from the CV, or an error message.
    """
    return extract_resume_text_from_path(file_path)
