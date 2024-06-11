from flask import Flask, request, jsonify
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate

from flask import Flask, request, render_template

app = Flask(__name__)

folder_path = "db"
pdf_path = "nasa_systems_engineering_handbook_0.pdf"

cached_llm = Ollama(model="mistral")

embedding = FastEmbedEmbeddings()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1024, chunk_overlap=80, length_function=len, is_separator_regex=False
)

raw_prompt = PromptTemplate.from_template(
    """ 
    <s>[INST] You are a technical assistant good at searching documents. If you do not have an answer from the provided information say so. [/INST] </s>
    [INST] {input}
           Context: {context}
           Answer:
    [/INST]
"""
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask_pdf", methods=["POST"])
def askPDFPost():
    json_content = request.json
    query = json_content.get("query")

    vector_store = Chroma(persist_directory=folder_path, embedding_function=embedding)

    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 20, "score_threshold": 0.1},
    )

    document_chain = create_stuff_documents_chain(cached_llm, raw_prompt)
    chain = create_retrieval_chain(retriever, document_chain)

    result = chain.invoke({"input": query})

    sources = []
    for doc in result["context"]:
        sources.append(
            {"source": doc.metadata["source"], "page_content": doc.page_content}
        )

    response_answer = {"answer": result["answer"], "sources": sources}
    return jsonify(response_answer)

@app.route("/pdf", methods=["POST"])
def pdfPost():
    loader = PDFPlumberLoader(pdf_path)
    docs = loader.load_and_split()

    chunks = text_splitter.split_documents(docs)

    vector_store = Chroma.from_documents(
        documents=chunks, embedding=embedding, persist_directory=folder_path
    )

    vector_store.persist()

    response = {
        "status": "Successfully Loaded",
        "filename": pdf_path,
        "doc_len": len(docs),
        "chunks": len(chunks),
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)