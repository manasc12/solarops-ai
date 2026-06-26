from langchain_chroma import Chroma
from backend.app.core.config import settings
from rag.toolbox.miscellaneous import rag_embedding_function
import chromadb

chroma_client = chromadb.CloudClient(
  api_key=settings.chroma_api_key,
  tenant=settings.chroma_tenant,
  database=settings.chroma_database
)

class SolarOpsChroma(Chroma):
    def __init__(self):
        # this one is for local development using docker
        # super().__init__(collection_name=settings.rag_collection_name,
        #                  embedding_function=rag_embedding_function(),
        #                  host=settings.chroma_host,
        #                  port=settings.chroma_port,
        #                  collection_metadata={
        #                                         "hnsw:space": "cosine"
        #                                     },
        #                 )

        
        # this one is for Chroma Cloud
        super().__init__(collection_name=settings.rag_collection_name,
                         embedding_function=rag_embedding_function(),
                         client=chroma_client,
                         collection_metadata={
                                                "hnsw:space": "cosine"
                                            },
                        )
                        
    @property
    def size(self) -> int:
        return self._collection.count()
        