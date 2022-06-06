import json
from typing import List
from unicodedata import category
from asyncpg.connection import Connection
import pydantic
from shared.view_models import Annotations
from shared.database import typed_fetch
from ..dtos import ImageDto
from shared.database import BaseRepository


class ImagesRepository(BaseRepository):
    """Images repository used to fetch sites"""

    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)

    async def get_image_by_id(self, image_id: int) -> ImageDto:
        """Get image based on its id"""
        
        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    im.id as image_id,
                    im.dataset_id,
                    im.image_url,
                    ib.bbox_json,
                    ic.category_json
                FROM tenyks.image im
                JOIN tenyks.image_bbox ib on im.id=ib.image_id
                JOIN tenyks.image_category ic on ib.id=ic.bbox_id
                WHERE image_id=$1;
            """
            image = await typed_fetch(self.connection, ImageDto, query_string, image_id)
            return image

    async def get_model_image_by_image_id_model_id(self, image_id: int, model_id: int) -> ImageDto:
        """Get image based on its model id and image id"""

        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    im.id as image_id,
                    im.dataset_id,
                    im.image_url,
                    ib.bbox_json,
                    ic.category_json
                FROM tenyks.image im
                JOIN tenyks.image_bbox ib on im.id=ib.image_id
                JOIN tenyks.image_category ic on ib.id=ic.bbox_id
                JOIN tenyks.model_image_bbox mib on im.id=mib.image_id
                JOIN tenyks.model_image_category mic on mib.id=mic.bbox_id
                JOIN tenyks.model m on mib.model_id = m.id
                --JOIN tenyks.model_image_heatmap mih on 
                WHERE image_id=$1 AND model_id=$2;
            """
            image = await typed_fetch(self.connection, ImageDto, query_string, image_id, model_id)
            return image

    async def create_image(self, name: str, dataset_name: str, annotations: Annotations, url: str ) -> ImageDto:
        """Create a new image"""

        bboxes = [bbox.array for bbox in annotations.bboxes]
        categories = [cat.category_id for cat in annotations.categories]

        async with self.connection.transaction():
            get_dataset_id_string = f"""
                SELECT 
                    ds.id 
                FROM tenyks.dataset ds
                WHERE dataset_name=$1;
            """
            
            dataset_id = await self.connection.fetchval(
                get_dataset_id_string,
                dataset_name,
            )

            image_insert_query_string = f"""
                INSERT INTO tenyks.image(dataset_id, image_url)
                VALUES ($1, $2)
                RETURNING id;
            """
                
            image_id = await self.connection.fetchval(
                image_insert_query_string,
                dataset_id,
                url
            )

            category_insert_query_string = f"""
                INSERT INTO tenyks.image_category(category)
                VALUES ($1)
                RETURNING id;
            """
            category_ids = [ 
                await self.connection.fetchval(
                    category_insert_query_string,
                    category
                )
                for category in categories
            ]

            image_bbox_insert_query_string = f"""
                INSERT INTO tenyks.image_bbox(image_id, category_id, bbox_json)
                VALUES ($1, $2, $3)
                RETURNING id;
            """
            
            result = [
                await self.connection.fetchval(
                    image_bbox_insert_query_string,
                    image_id,
                    category_id,
                    json.dumps(bboxes[i]),
            )
            for i, category_id in enumerate(category_ids)]

    async def create_model_image(self, dataset_type: str, dataset_name: str, dataset_url: str, dataset_size: int, ) -> None:
        """Create a new image"""

        async with self.connection.transaction():
            get_dataset_type_id_string = f"""
                SELECT 
                    dataset_type_id 
                FROM tenyks.dataset ds
                JOIN tenyks.dataset_type dst ON ds.dataset_type_id = dst.id
                WHERE name=$1;
            """
            
            dataset_type_id = await self.connection.fetch(
                get_dataset_type_id_string,
                dataset_type,
            )

            dataset_insert_query_string = f"""
                INSERT INTO tenyks.dataset(dataset_type_id, dataset_name, dataset_url, dataset_size)
                VALUES ($1, $2, $3, $4)
                RETURNING id;
            """
                
            result = await self.connection.fetch(
                dataset_insert_query_string,
                dataset_type_id,
                dataset_name,
                dataset_url,
            )