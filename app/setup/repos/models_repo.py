import json
from typing import List
from asyncpg.connection import Connection
import pydantic
from ...shared.database import typed_fetch
from ..dtos import DatasetDto
from ...shared.database import BaseRepository


class ModelsRepository(BaseRepository):
    """Models repository used to fetch or post ML models"""

    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)

    async def get_model_by_name(self, name: str) -> json:
        """Get model based on its name"""
        
        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    mo.id,
                    mo.name,
                FROM tenyks.model mo
                WHERE name=$1;
            """
            dataset = await typed_fetch(self.connection, DatasetDto, query_string, name)
            return dataset

    async def get_model_by_id(self, modelid: int) -> json:
        """Get model based on its id"""

        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    mo.id,
                    mo.name,
                FROM tenyks.model mo
                WHERE id=$1;
            """
            dataset = await typed_fetch(self.connection, DatasetDto, query_string, modelid)
            return dataset

    async def create_model(self, dataset_type: str, dataset_name: str, dataset_url: str, dataset_size: int, ) -> None:
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