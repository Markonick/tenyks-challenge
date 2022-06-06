import json
from typing import List
from asyncpg.connection import Connection
import pydantic
from shared.database import typed_fetch
from ..dtos import DatasetDto, ModelDto
from shared.database import BaseRepository


class ModelsRepository(BaseRepository):
    """Models repository used to fetch or post ML models"""

    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)

    async def get_model_by_name(self, name: str) -> ModelDto:
        """Get model based on its name"""
        
        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    mo.id,
                    mo.name
                FROM tenyks.model mo
                WHERE name=$1;
            """
            result = await typed_fetch(self.connection, ModelDto, query_string, name)
            return result[0]

    async def get_model_by_id(self, modelid: int) -> ModelDto:
        """Get model based on its id"""

        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    mo.id,
                    mo.name,
                FROM tenyks.model mo
                WHERE id=$1;
            """
            dataset = await typed_fetch(self.connection, ModelDto, query_string, modelid)
            return dataset

    async def create_model(self, name: str, datasets: List[str]) -> None:
        """Create a new model"""

        async with self.connection.transaction():
            model_insert_query_string = f"""
                INSERT INTO tenyks.model(name)
                VALUES ($1)
                RETURNING id;
            """
                
            model_id = await self.connection.fetchrow(
                model_insert_query_string,
                name,
            )
            print(model_id[0])
            get_dataset_id_query_string = f"""
                SELECT 
                    ds.id 
                FROM tenyks.dataset ds
                WHERE ds.dataset_name=$1;
            """

            dataset_ids = [
                await self.connection.fetchval(
                    get_dataset_id_query_string,
                    dataset_name,
                ) 
                for dataset_name in datasets
            ]

            print(dataset_ids)
            model_dataset_insert_query_string = f"""
                INSERT INTO tenyks.model_dataset(model_id, dataset_id)
                VALUES ($1, $2);
            """
            
            result = [
                await self.connection.fetch(
                    model_dataset_insert_query_string,
                    model_id[0], dataset_id,
                )
                for dataset_id in dataset_ids
            ]
