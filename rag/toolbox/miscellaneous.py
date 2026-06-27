from backend.app.core.config import settings
def document_id(content: str) -> str:
    import hashlib
    payload = content
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def rag_embedding_function() -> list[float]: 
    if settings.llm_enabled:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=settings.rag_embedding_model,
                                api_key=settings.openai_api_key)
    else:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")

from langchain_text_splitters import RecursiveCharacterTextSplitter
def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=size, chunk_overlap=overlap, separators=["\n\n", "\n", " ", ""],
    )
    text_chunks = text_splitter.split_text(text)
    return text_chunks