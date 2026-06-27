from langchain_chroma import Chroma
from backend.app.core.config import settings
from rag.toolbox.miscellaneous import rag_embedding_function
import chromadb

_chroma_client = chromadb.CloudClient(
  api_key=settings.chroma_api_key,
  tenant=settings.chroma_tenant,
  database=settings.chroma_database
)

class SolarOpsChroma(Chroma):
    def __init__(self):
        if settings.chroma_docker and settings.chroma_cloud:
            raise ValueError("In .env file: Either CHROMA_DOCKER should be true or CHROMA_CLOUD should be true or both are false. But both cannot be true!!!")
        if settings.chroma_docker:
            super().__init__(collection_name=settings.rag_collection_name,
                             embedding_function=rag_embedding_function(),
                             host=settings.chroma_host,
                             port=settings.chroma_port,
                             collection_metadata={
                                                    "hnsw:space": "cosine"
                                                },
                            )
        elif settings.chroma_cloud:
            super().__init__(collection_name=settings.rag_collection_name,
                            embedding_function=rag_embedding_function(),
                            client=_chroma_client,
                            collection_metadata={
                                                    "hnsw:space": "cosine"
                                                },
                            )
        else:
            super().__init__(collection_name=settings.rag_collection_name,
                            embedding_function=rag_embedding_function(),
                            persist_directory="chroma_data",)
                        
    @property
    def size(self) -> int:
        return self._collection.count()
        
_solarops_chroma_instance: SolarOpsChroma | None = None

def get_solarops_chroma_instance() -> SolarOpsChroma:
    global _solarops_chroma_instance
    if _solarops_chroma_instance is None:
        _solarops_chroma_instance = SolarOpsChroma()
    return _solarops_chroma_instance