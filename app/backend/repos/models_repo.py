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

    async def get_all_models(self) -> ModelDto:
        """Get model based on its name"""
        
        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    mo.id,
                    mo.name,
                    d.dataset_type_id,
                    d.dataset_name,
                    d.dataset_size,
                    d.dataset_path,
                    d.images_path
                FROM tenyks.model mo
                JOIN tenyks.model_dataset md on mo.id = md.model_id
                JOIN tenyks.dataset d on md.dataset_id = d.id
                JOIN tenyks.dataset_type dt on d.dataset_type_id = dt.id
            """
            result = await typed_fetch(self.connection, ModelDto, query_string)
            return result

    async def get_model_by_name(self, name: str) -> ModelDto:
        """Get model based on its name"""
        
        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    mo.id,
                    mo.name,
                    d.dataset_type_id,
                    d.dataset_name,
                    d.dataset_size,
                    d.dataset_path,
                    d.images_path
                FROM tenyks.model mo
                JOIN tenyks.model_dataset md on mo.id = md.model_id
                JOIN tenyks.dataset d on md.dataset_id = d.id
                JOIN tenyks.dataset_type dt on d.dataset_type_id = dt.id
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
                    d.dataset_type_id,
                    d.dataset_name,
                    d.dataset_size,
                    d.dataset_path,
                    d.images_path
                FROM tenyks.model mo
                JOIN tenyks.model_dataset md on mo.id = md.model_id
                JOIN tenyks.dataset d on md.dataset_id = d.id
                JOIN tenyks.dataset_type dt on d.dataset_type_id = dt.id
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

            model_id = await self.connection.fetchval(
                model_insert_query_string,
                name,
            )
            
            print(model_id)
            print(model_id)
            print(model_id)
            print(model_id)
            print(model_id)
            print(model_id)
            get_dataset_id_query_string = f"""
                SELECT 
                    ds.id 
                FROM tenyks.dataset ds
                WHERE ds.dataset_name=$1;
            """
            dataset_ids = [
                await self.connection.fetchval(
                    get_dataset_id_query_string,
                    dataset,
                ) 
                for dataset in datasets
            ]
            
            model_dataset_insert_query_string = f"""
                INSERT INTO tenyks.model_dataset(model_id, dataset_id)
                VALUES ($1, $2);
            """
            
            result = [
                await self.connection.fetch(
                    model_dataset_insert_query_string,
                    model_id, dataset_id,
                )
                for dataset_id in dataset_ids
            ]

