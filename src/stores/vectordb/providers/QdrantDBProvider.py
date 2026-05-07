from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_client: str, default_vector_size: int = 786,
                                     distance_method: str = None, index_threshold: int=100):

        self.client = None
        self.db_client = db_client
        self.distance_method = None
        self.default_vector_size = default_vector_size
        
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger('uvicorn')

    async def connect(self):
        self.client = QdrantClient(path=self.db_client)

    async def disconnect(self):
        self.client = None

    async def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    async def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    async def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            self.logger.info(f"Deleting collection: {collection_name}")
            return self.client.delete_collection(collection_name=collection_name)
        
    async def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name):
            self.logger.info(f"Creating new Qdrant collection: {collection_name}")
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True
        
        return False
    
    async def insert_one(self, collection_name: str, text: str, vector: list,
                        metadata: dict = None, 
                        record_id: str = None):
        
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Cannot insert to non-existent collection: {collection_name}")
            return False
        
        if record_id is None:
            # Generate a simple integer ID (in production, use uuid)
            record_id = 0  # You'll need to track this properly
        
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text, 
                            "metadata": metadata or {}
                        }
                    )
                ]
            )
            return True
        except Exception as e:
            self.logger.error(f"Error while inserting: {e}")
            return False
    
    async def insert_many(self, collection_name: str, texts: list, 
                        vectors: list, metadata: list = None, 
                        record_ids: list = None, batch_size: int = 50):
        
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(len(texts)))
        
        for start_idx in range(0, len(texts), batch_size):
            end_idx = min(start_idx + batch_size, len(texts))
            
            points = []
            for idx in range(start_idx, end_idx):
                points.append(
                    models.PointStruct(
                        id=record_ids[idx],
                        vector=vectors[idx],
                        payload={
                            "text": texts[idx], 
                            "metadata": metadata[idx]
                        }
                    )
                )
            
            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
            except Exception as e:
                self.logger.error(f"Error inserting batch: {e}")
                return False
        
        return True
        
    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        if not self.client:
            return None
        
        if not self.is_collection_existed(collection_name):
            return None
        
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=vector,
                limit=limit,
                with_payload=True
            )
            return [
                RetrievedDocument(**{
                    "score": result.score,
                    "text": result.payload["text"],
                })
                for result in results.points
            ]
            
        except Exception as e:
            self.logger.error(f"Error searching vectors: {e}")
            return None