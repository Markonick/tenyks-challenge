import json
from typing import List
from asyncpg.connection import Connection
import pydantic
from ...shared.database import typed_fetch
from ..dtos import DatasetDto
from ...shared.database import BaseRepository


class DatasetsRepository(BaseRepository):
    """Sites repository used to fetch sites"""

    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)

    async def get_dataset_by_name(self, name: str) -> json:
        """Get dataset based on its name"""
        
        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    ds.id,
                    ds.dataset_type_id,
                    ds.name as dataset_name
                    ds.dataset_url
                FROM tenyks.dataset ds
                WHERE name=$1;
            """
            dataset = await typed_fetch(self.connection, DatasetDto, query_string, name)
            return dataset

    async def get_dataset_by_id(self, dataset_id: int) -> json:
        """Get dataset based on its id"""

        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    ds.id,
                    ds.dataset_type_id,
                    ds.name as dataset_name
                    ds.dataset_url
                FROM tenyks.dataset ds
                FROM site sit
                WHERE id=$1;
            """
            dataset = await typed_fetch(self.connection, DatasetDto, query_string, dataset_id)
            return dataset

    async def create_dataset(self, dataset_type: str, dataset_name: str, dataset_url: str, dataset_size: int, ) -> None:
        """Create a new dataset"""

        async with self.connection.transaction():
            get_dataset_type_id_string = f"""
                SELECT 
                    dataset_type_id 
                FROM tenyks.dataset ds
                JOIN tenyks.dataset_type dst ON ds.dataset_type_id = dst.id
                WHERE name=$1;
            """
            
            dataset_type_id = await self.connection.raw_fetch(
                get_dataset_type_id_string,
                dataset_type,
            )

            dataset_insert_query_string = f"""
                INSERT INTO tenyks.dataset(dataset_type_id, dataset_name, dataset_url, dataset_size)
                VALUES ($1, $2, $3, $4)
                RETURNING id;
            """
                
            result = await self.connection.raw_fetch(
                dataset_insert_query_string,
                dataset_type_id,
                dataset_name,
                dataset_url,
            )