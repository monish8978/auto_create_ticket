import os
import csv
import pandas as pd
from PyPDF2 import PdfReader
from utils.logger import log
from docx import Document
import textract
import warnings

# Suppress warnings from libraries (optional)
warnings.filterwarnings('ignore')


def extract_docx_text(file_path: str) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    """
    doc = Document(file_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text


def extract_doc_text(file_path: str) -> str:
    """
    Extracts text from a legacy DOC file using textract.
    """
    try:
        text = textract.process(file_path).decode('utf-8')
        return text
    except Exception as e:
        log.error(f"Failed to extract DOC file: {e}", exc_info=True)
        raise ValueError(f"Failed to extract .doc file: {e}")


def extract_pdf_text(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyPDF2.
    """
    reader = PdfReader(file_path)
    text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += page_text
        else:
            log.warning(f"No text found on page {i+1} of PDF {file_path}")
    return text


def extract_csv_text(file_path: str) -> str:
    """
    Extracts text from a CSV file by joining rows with spaces.
    """
    text = ""
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            text += ' '.join(row) + '\n'
    return text


def extract_excel_text(file_path: str) -> str:
    """
    Extracts text from an Excel file (XLS/XLSX) using pandas.
    Converts DataFrame to string for readability.
    """
    df = pd.read_excel(file_path)
    text = df.to_string(index=False)
    return text


def extract_txt_text(file_path: str) -> str:
    """
    Extracts text from a plain TXT file.
    """
    with open(file_path, "r", encoding='utf-8') as f:
        text = f.read()
    return text


def extract_file_text(file_path: str) -> str:
    """
    Extracts text from a file based on its extension.
    Supports PDF, CSV, Excel, TXT, DOCX, and DOC formats.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_pdf_text(file_path)
    elif ext == ".csv":
        return extract_csv_text(file_path)
    elif ext in [".xls", ".xlsx"]:
        return extract_excel_text(file_path)
    elif ext == ".txt":
        return extract_txt_text(file_path)
    elif ext == ".docx":
        return extract_docx_text(file_path)
    elif ext == ".doc":
        return extract_doc_text(file_path)
    else:
        log.error(f"Unsupported file type: {ext}")
        raise ValueError(f"Unsupported file type: {ext}")
