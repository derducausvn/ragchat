import streamlit as st
import pandas as pd
import io
import os
from rag_engine import prepare_corpus, embed_texts, build_faiss_index, retrieve_answer, generate_response

st.set_page_config(page_title="RAG Chatbot", layout="centered")
st.title("Customer Questionnaires Agent")

# Load data & build index (on first load)
def initialize():
    corpus, metadata = prepare_corpus("data")
    if isinstance(corpus, str) and corpus.startswith("No documents were loaded"):
        st.warning("⚠️ No knowledge base found. Add PDF, Excel, or Word files to the 'data/' folder.")
        return None, None, None, None

    embeddings = embed_texts(corpus)
    index = build_faiss_index(embeddings)
    return corpus, metadata, index, embeddings

# Only initialize if not yet done
if "index" not in st.session_state:
    corpus, metadata, index, embeddings = initialize()
    if corpus and index and embeddings:
        st.session_state["corpus"] = corpus
        st.session_state["metadata"] = metadata
        st.session_state["embeddings"] = embeddings
        st.session_state["index"] = index
else:
    corpus = st.session_state["corpus"]
    metadata = st.session_state["metadata"]
    embeddings = st.session_state["embeddings"]
    index = st.session_state["index"]

# If index is ready, show features
if corpus and index and embeddings:
    query = st.text_input("💬 Ask a question:")
    if st.button("Get Answer") and query.strip():
        with st.spinner("Thinking..."):
            context = retrieve_answer(query, corpus, metadata, index, embeddings)
            answer = generate_response(query, context)

            st.subheader("🧾 Answer:")
            st.write(answer)

            with st.expander("📚 Retrieved context"):
                st.code(context)

    st.header("📤 Upload Excel Questionnaire")
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("✅ Uploaded file preview:")
        st.dataframe(df.head())

        question_column = st.selectbox("Select column containing the questions:", df.columns.tolist())

        if st.button("Auto-fill Answers"):
            with st.spinner("Generating answers..."):
                answers = []
                for question in df[question_column].dropna():
                    context = retrieve_answer(str(question), corpus, metadata, index, embeddings)
                    answer = generate_response(str(question), context)
                    answers.append(answer)

                df["Auto Answer"] = answers
                st.success("✅ Done! See the answers below:")
                st.dataframe(df[[question_column, "Auto Answer"]])

                buffer = io.BytesIO()
                df.to_excel(buffer, index=False)
                st.download_button(
                    "📥 Download answered file",
                    buffer.getvalue(),
                    file_name="answered_questionnaire.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # === 📚 Knowledge Upload Section ===
    st.header("📚 Knowledge Upload")

    knowledge_files = st.file_uploader(
        "Upload knowledge files (PDF, Word, Excel)",
        type=["pdf", "docx", "xlsx"],
        accept_multiple_files=True
    )

    if knowledge_files:
        os.makedirs("data", exist_ok=True)
        for file in knowledge_files:
            file_path = os.path.join("data", file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())
        st.success("✅ Files uploaded to the knowledge base folder.")

        if st.button("🔄 Integrate Knowledge"):
            with st.spinner("Indexing uploaded documents..."):
                corpus, metadata = prepare_corpus("data")
                embeddings = embed_texts(corpus)
                index = build_faiss_index(embeddings)

                # Update session state
                st.session_state["corpus"] = corpus
                st.session_state["metadata"] = metadata
                st.session_state["embeddings"] = embeddings
                st.session_state["index"] = index

            st.success("✅ Knowledge integrated successfully!")

else:
    st.stop()
