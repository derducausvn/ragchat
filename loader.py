import fitz  # PyMuPDF
import docx
import pandas as pd
import os

def load_txt_from_pdf(filepath):
    text = ""
    doc = fitz.open(filepath)
    for page in doc:
        text += page.get_text()
    return text

def load_txt_from_docx(filepath):
    doc = docx.Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

def load_txt_from_excel(filepath):
    dfs = pd.read_excel(filepath, sheet_name=None)
    combined_text = ""
    for name, df in dfs.items():
        combined_text += f"Sheet: {name}\n"
        combined_text += df.fillna("").to_string(index=False)
        combined_text += "\n\n"
    return combined_text

def load_all_documents(folder_path):
    documents = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filename.endswith(".pdf"):
                text = load_txt_from_pdf(filepath)
            elif filename.endswith(".docx"):
                text = load_txt_from_docx(filepath)
            elif filename.endswith(".xlsx"):
                text = load_txt_from_excel(filepath)
            else:
                continue
            documents.append((filename, text))
    return documents

def load_txt_from_excel(filepath):
    dfs = pd.read_excel(filepath, sheet_name=None)
    combined_text = ""

    for name, df in dfs.items():
        df = df.fillna("")
        combined_text += f"\nSheet: {name}\n"
        for _, row in df.iterrows():
            row_text = " | ".join(str(cell).strip() for cell in row if str(cell).strip())
            combined_text += row_text + "\n"
    
    return combined_text
