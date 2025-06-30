import fitz  # PyMuPDF
import docx
import pandas as pd
import os

def load_txt_from_pdf(filepath):
    try:
        text = ""
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"[ERROR] Failed to load PDF {filepath}: {e}")
        return ""

def load_txt_from_docx(filepath):
    try:
        doc = docx.Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"[ERROR] Failed to load DOCX {filepath}: {e}")
        return ""

def load_txt_from_excel(filepath):
    try:
        dfs = pd.read_excel(filepath, sheet_name=None)
        combined_text = ""
        for name, df in dfs.items():
            df = df.fillna("")
            combined_text += f"\nSheet: {name}\n"
            for _, row in df.iterrows():
                row_text = " | ".join(str(cell).strip() for cell in row if str(cell).strip())
                combined_text += row_text + "\n"
        return combined_text
    except Exception as e:
        print(f"[ERROR] Failed to load Excel {filepath}: {e}")
        return ""

def load_all_documents(folder_path):
    documents = []
    if not os.path.exists(folder_path):
        print(f"[WARNING] Folder '{folder_path}' not found. Skipping document loading.")
        return documents
    
    for root, _, files in os.walk(folder_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            text = ""
            if filename.endswith(".pdf"):
                text = load_txt_from_pdf(filepath)
            elif filename.endswith(".docx"):
                text = load_txt_from_docx(filepath)
            elif filename.endswith(".xlsx"):
                text = load_txt_from_excel(filepath)
            else:
                continue
            if text.strip():
                documents.append((filename, text))
    return documents
