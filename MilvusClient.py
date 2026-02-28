from typing import List, Dict
import logging
from pymilvus import connections, Collection
import numpy as np
import json
import pandas as pd
import asyncio
import os
from dotenv import load_dotenv
import sys

load_dotenv()

class Logger:
    def __init__(self, log_file="app_v1.0.log"):
        # Безопасная настройка кодировки
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding='utf-8')
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding='utf-8')

        # Настройка логирования
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.__stdout__)  # ← sys.__stdout__ — оригинальный поток, работает везде
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_error(self, message: str):
        self.logger.error(message)

logger = Logger()

#Класс для обработки данных
class DataProcessor:
    @staticmethod
    def _prepare_main(result: List[Dict], output_fields: List[str]) -> List[Dict]:
        return [{field: (np.frombuffer(result[0]["embedding"][0], dtype=np.float16) if field == 'embedding' else item[field]) for field in output_fields if field in item} for item in result]


class MilvusBase:
    def __init__(self):
        connections.connect(
            alias="default",
            host=str(os.getenv("MILVUS_HOST", "localhost")),
            port=str(os.getenv("MILVUS_PORT", "19530"))
        )
        self.dtype_map = {
            101: np.float32,
            102: np.float16, 
            103: np.uint8,    
        }

    @staticmethod
    def _author_in(data: List[int]) -> str:
        return f"id in {data}"

    @staticmethod
    def _author_notin(data: List[int]) -> str:
        return f"id not in {data}"

    def _build_expr(self, data: Dict) -> str:
        expr_parts = []
        if "adjacency_list" in data:
            expr_parts.append(self._author_notin(data["adjacency_list"]))
        if "filter_embedding" in data:
            expr_parts.append(self._author_in(data["filter_embedding"]))
        return " and ".join(expr_parts)
    
    async def get_entity_by_ids(self, data: List[int]) -> List[Dict]:
        collection_name = self.__class__.__name__.lower()  # Получаем имя класса в нижнем регистре (например, 'author')
        collection = getattr(self, f"{collection_name}_collection", None)
        
        if not collection:
            raise ValueError(f"Коллекция '{collection_name}' не найдена.")
        
        """Получение данных по списку ID."""
        logger.log_info("get_entity_by_ids: данные пришли")
        try:
            keys_filter = [item.name for item in collection.schema.fields]
            result = collection.query(expr=self._author_in(data), output_fields=keys_filter)
            return DataProcessor._prepare_main(result, keys_filter)
        except Exception as e:
            logger.log_error(f"Ошибка в get_entity_by_ids: {e}")
            raise

    async def search(
        self,
        **kwargs
    ) -> List[Dict]:

        logger.log_info("search_helper: запуск поиска ближайших эмбеддингов")

        # Пример: 'author' для класса Author
        collection_name = self.__class__.__name__.lower()
        collection = getattr(self, f"{collection_name}_collection", None)
    
        if not collection:
            raise ValueError(f"Коллекция '{collection_name}' не найдена.")
        
        try:
            embeddings = np.array(kwargs.get("embedding", None), dtype=np.float16)
            if embeddings.ndim == 1:
                embeddings = np.expand_dims(embeddings, axis=0)

            expr = kwargs.get("expr", None)
            result = collection.search(
                data=embeddings,
                anns_field="embedding",
                param={"metric_type": "COSINE", "params": {"nprobe": 10}},
                limit=kwargs.get("top_k", 1000),
                expr=expr,
                output_fields=kwargs.get("output_fields", None)
            )

            return result
        except Exception as exc:
            logger.log_error(f"search_helper: ошибка при поиске: {exc}")
            raise


class AuthorAvarage(MilvusBase):
    def __init__(self):
        super().__init__()
        self.authoravarage_collection = Collection(name=str(os.getenv("MILVUS_AUTHORAVARAGE", "")))
        self.graph_collection = Collection(name=str(os.getenv("MILVUS_GRAPH", "")))
    #Author Graph
    def create_graph(self, data: List[int]) -> List[Dict]:
        """Получение весов между авторами."""
        return self.graph_collection.query(expr=self._author_in(data), output_fields=["weight_author"])
    
    # AuthorGraph
    async def build_author_edges(self, author_ids: List[int]) -> List[pd.DataFrame]:
        author_edges = []
        for data_author in self.create_graph(author_ids):  
            publication_weight = {int(key): value for key, value in json.loads(data_author["weight_author"]).items()}
            df = pd.DataFrame(publication_weight.items(), columns=['target', 'weight'])
            df["source"] = data_author["id"]
            author_edges.append(df)
        return author_edges

    async def get_author_adjacency_list(self, author_id: int) -> List[int]:
        result = await self.get_entity_by_ids([author_id])
        return (result[0]["metadata"]).get("adjacency_list", [])

    async def get_author_publications(self, author_id: list[int]) -> List[Dict]:
        result = await self.get_entity_by_ids(author_id)
        return [(item["metadata"]).get("publications_massiv", []) for item in result]

class OrganizationName(MilvusBase):
    def __init__(self):
        super().__init__()
        self.organizationname_collection = Collection(name=str(os.getenv('MILVUS_ORGANIZATION', "")))

class AuthorName(MilvusBase):
    def __init__(self):
        super().__init__()
        self.authorname_collection = Collection(name=str(os.getenv('MILVUS_AUTHOR', "")))

class PublicationName(MilvusBase):
    def __init__(self):
        super().__init__()
        self.publicationname_collection = Collection(name=str(os.getenv("MILVUS_PUBLICATION", "")))


class TopicName(MilvusBase):
    """
    Коллекция с эмбеддингами топиков (topic).
    Ожидается, что primary key совпадает с Topic.num в PostgreSQL.
    """

    def __init__(self):
        super().__init__()
        self.topicname_collection = Collection(name=str(os.getenv("MILVUS_TOPIC", "")))

class Conference(MilvusBase):
    def __init__(self):
        super().__init__()
        self.conference_collection = Collection(name=str(os.getenv("MILVUS_CONFERENCE", "")))
        
    async def source_id(self, id: int) -> int:
        result = await self.get_entity_by_ids([id])
        return int(result[0]["source_id"])
    
class Journal(MilvusBase):
    def __init__(self):
        super().__init__()
        self.journal_collection = Collection(name=str(os.getenv("MILVUS_JOURNAL", "")))

    async def source_id(self, id: int) -> int:
        result = await self.get_entity_by_ids([id])
        return int(result[0]["source_id"])
    
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from typing import List, Dict
    import numpy as np

    milvus = OrganizationName()
    result = asyncio.run(milvus.get_entity_by_ids([1]))
    print(result)
    
