import streamlit as st
import pandas as pd
import io
from rag_engine import prepare_corpus, embed_texts, build_faiss_index, retrieve_answer, generate_response

st.set_page_config(page_title="RAG Chatbot", layout="centered")
st.title("🧠 RAG Chatbot for Customer Questionnaires")

# Load data & build index (on first load)
def initialize():
    st.info("⏳ Loading documents and building index...")
    corpus, metadata = prepare_corpus("data")
    embeddings = embed_texts(corpus)
    index = build_faiss_index(embeddings)
    return corpus, metadata, index, embeddings

corpus, metadata, index, embeddings = initialize()

# User Input
query = st.text_input("💬 Ask a question:")
if st.button("Get Answer") and query.strip():
    with st.spinner("Thinking..."):
        context = retrieve_answer(query, corpus, metadata, index, embeddings)
        answer = generate_response(query, context)

        st.subheader("🧾 Answer:")
        st.write(answer)

        with st.expander("📚 Retrieved context"):
            st.code(context)

st.header("📤 Upload Excel Questionnaire (1 question per row)")

uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("✅ Uploaded file preview:")
    st.dataframe(df.head())

    question_column = st.selectbox("🧠 Select column containing the questions:", df.columns.tolist())

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

            # Optional: download
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False)
            st.download_button(
                "📥 Download answered file",
                buffer.getvalue(),
                file_name="answered_questionnaire.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )