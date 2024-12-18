import json
from typing import List
from asyncpg.connection import Connection
import pydantic
from shared.database import typed_fetch
from ..dtos import DatasetDto
from shared.database import BaseRepository


class DatasetsRepository(BaseRepository):
    """Datasets repository used to fetch or post datasets"""

    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)
        
    async def get_all_datasets(self, ) -> List[DatasetDto]:
        """Get all datasets -- TODO: based on image_type??"""

        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    ds.id,
                    ds.dataset_type_id,
                    ds.dataset_name,
                    ds.dataset_size,
                    ds.dataset_path,
                    ds.images_path
                FROM dataset ds
            """

            result = await typed_fetch(self.connection, DatasetDto, query_string)
            
            return result

    async def get_dataset_by_name(self, name: str) -> DatasetDto:
        """Get dataset based on its name"""
        
        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    ds.id,
                    ds.dataset_type_id,
                    ds.dataset_name,
                    ds.dataset_size,
                    ds.dataset_path,
                    ds.images_path,
                    m.id
                FROM dataset ds
                JOIN model_dataset mds on ds.id = mds.dataset_id
                JOIN model m on mds.model_id = m.id
                WHERE dataset_name=$1;
            """

            result = await typed_fetch(self.connection, DatasetDto, query_string, name)
 
            return [] if len(result) == 0 else result[0]

    async def get_dataset_by_id(self, dataset_id: int) -> DatasetDto:
        """Get dataset based on its id"""

        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    ds.id,
                    ds.dataset_type_id,
                    ds.dataset_name,
                    ds.dataset_size,
                    ds.dataset_path,
                    ds.images_path
                FROM dataset ds
                WHERE id=$1;
            """

            result = await typed_fetch(self.connection, DatasetDto, query_string, dataset_id)
            return [] if len(result) == 0 else result[0]

    async def create_dataset(self, dataset_type: str, dataset_name: str, dataset_size: int, dataset_path: str, images_path: str, ) -> None:
        """Create a new dataset"""

        async with self.connection.transaction():
            get_dataset_type_id_string = f"""
                SELECT 
                    dst.id 
                FROM dataset_type dst
                WHERE dst.name=$1;
            """
            
            dataset_type_id = await self.connection.fetchval(
                get_dataset_type_id_string,
                dataset_type,
            )
            
            dataset_insert_query_string = f"""
                INSERT INTO dataset(dataset_type_id, dataset_name, dataset_size, dataset_path, images_path)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id;
            """
           
            result = await self.connection.fetch(
                dataset_insert_query_string,
                dataset_type_id,
                dataset_name,
                dataset_size,
                dataset_path,
                images_path,
            )
