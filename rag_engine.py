import os
import faiss
import openai
import numpy as np
from loader import load_all_documents
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Settings ===
EMBED_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 500

# === Utility ===
def chunk_text(text, chunk_size=CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# === Step 1: Load and Chunk Documents ===
def prepare_corpus(data_folder):
    raw_docs = load_all_documents(data_folder)
    corpus = []
    metadata = []

    for filename, content in raw_docs:
        chunks = chunk_text(content)
        corpus.extend(chunks)
        metadata.extend([(filename, i) for i in range(len(chunks))])
    
    return corpus, metadata

# === Step 2: Embed Chunks ===
def embed_texts(texts):
    clean_texts = [t for t in texts if t.strip()]
    embeddings = []

    # OpenAI limit: 100 items per request
    for i in range(0, len(clean_texts), 100):
        batch = clean_texts[i:i + 100]
        response = openai.embeddings.create(
            model=EMBED_MODEL,
            input=batch
        )
        batch_embeddings = [np.array(e.embedding).astype("float32") for e in response.data]
        embeddings.extend(batch_embeddings)

    return embeddings

# === Step 3: Build FAISS Index ===
def build_faiss_index(embeddings):
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index

# === Step 4: Search and Generate ===
def retrieve_answer(query, corpus, metadata, index, embeddings, top_k=3):
    query_emb = embed_texts([query])[0]
    _, I = index.search(np.array([query_emb]), top_k)
    context = ""

    for i in I[0]:
        filename, chunk_id = metadata[i]
        context += f"\n[{filename} - chunk {chunk_id}]\n{corpus[i]}\n"

    return context

def generate_response(query, context):
    prompt = f"""You are a helpful assistant. Answer the user's question based only on the context below.
Context:\n{context}\n
Question: {query}
Answer:"""

    response = openai.chat.completions.create(
        model="gpt-4o",  # Or gpt-3.5-turbo
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()
