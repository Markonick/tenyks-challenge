import json
from typing import List, Optional
from asyncpg.connection import Connection
import pydantic
from shared.view_models import Annotations, Category
from shared.database import typed_fetch
from ..dtos import ImageDto
from shared.database import BaseRepository


class ImagesRepository(BaseRepository):
    """Images repository used to fetch sites"""

    def __init__(self, conn: Connection) -> None:
        super().__init__(conn)

    async def get_all_images(self, dataset_name: str) -> List[ImageDto]:
        """Get image based on its id"""
        
        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    im.id,
                    im.name,
                    im.dataset_id,
                    ARRAY_AGG(bbox_json) bboxes,
                    ARRAY_AGG(category) categories,
                    d.images_path,
                    d.dataset_name
                FROM image im
                JOIN dataset d ON im.dataset_id=d.id
                JOIN image_bbox ib ON im.id=ib.image_id
                JOIN image_category ic ON ib.category_id =ic.id 
                WHERE d.dataset_name=$1
                GROUP by
                    im.id,d.images_path,d.dataset_name, im.name;
            """
            image = await typed_fetch(self.connection, ImageDto, query_string, dataset_name)
            return image
            
    async def get_image_by_id(self, image_id: int) -> ImageDto:
        """Get image based on its id"""
        
        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    im.id as image_id,
                    im.dataset_id,
                    ib.bbox_json,
                    ic.category
                FROM image im
                JOIN image_bbox ib on im.id=ib.image_id
                JOIN image_category ic on ib.category_id=ic.id
                WHERE image_id=$1;
            """
            image = await typed_fetch(self.connection, ImageDto, query_string, image_id)
            return image   

    async def get_image_by_name(self, image_name: str) -> ImageDto:
        """Get image based on its id"""
        
        async with self.connection.transaction():
            query_string = f"""              
                SELECT
                    im.id,
                    im.name,
                    im.dataset_id,
                    ARRAY_AGG(bbox_json) bboxes,
                    ARRAY_AGG(category) categories,
                    d.images_path,
                    d.dataset_name
                FROM image im
                JOIN dataset d ON im.dataset_id=d.id
                JOIN image_bbox ib ON im.id=ib.image_id
                JOIN image_category ic ON ib.category_id =ic.id 
                WHERE im.name=$1
                GROUP by
                    im.id,d.images_path,d.dataset_name, im.name;
            """
            image = await typed_fetch(self.connection, ImageDto, query_string, image_name)
            return image[0]

    async def get_model_image_by_image_id_model_id(self, image_id: int, model_id: int) -> ImageDto:
        """Get image based on its model id and image id"""

        async with self.connection.transaction():
            query_string = f"""
                SELECT
                    im.id as image_id,
                    im.dataset_id,
                    im.image_path,
                    ib.bbox_json,
                    ic.category_json
                FROM image im
                JOIN image_bbox ib on im.id=ib.image_id
                JOIN image_category ic on ib.id=ic.bbox_id
                JOIN model_image_bbox mib on im.id=mib.image_id
                JOIN model_image_category mic on mib.id=mic.bbox_id
                JOIN model m on mib.model_id = m.id
                --JOIN model_image_heatmap mih on 
                WHERE image_id=$1 AND model_id=$2;
            """
            image = await typed_fetch(self.connection, ImageDto, query_string, image_id, model_id)
            return image

    async def create_image(
        self,
        name: str,
        dataset_name: str,
        annotations: Annotations,
    ) -> ImageDto:
        """Create a new image"""

        bboxes = [bbox for bbox in annotations.bboxes]
        categories = [cat for cat in annotations.categories]
        
        async with self.connection.transaction():
            get_dataset_id_string = f"""
                SELECT 
                    ds.id 
                FROM dataset ds
                WHERE dataset_name=$1;
            """
            
            dataset_id = await self.connection.fetchval(
                get_dataset_id_string,
                dataset_name,
            )

            image_insert_query_string = f"""
                INSERT INTO image(dataset_id, name)
                VALUES ($1, $2)
                RETURNING id;
            """
                
            image_id = await self.connection.fetchval(
                image_insert_query_string,
                dataset_id,
                name
            )

            category_insert_query_string = f"""
                INSERT INTO image_category(category)
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
                INSERT INTO image_bbox(image_id, category_id, bbox_json)
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
                for i, category_id in enumerate(category_ids)
            ]

    async def create_model_image_annotations(
        self,
        image_id: int,
        model_name: str,
        model_annotations: Annotations,
    ) -> None:
        """Create image model based features"""

        # First need model id
        model_get_query_string = f"""
            SELECT m.id
            FROM model m
            WHERE m.name = $1;
        """

        model_id = await self.connection.fetchval(
            model_get_query_string,
            model_name,
        )
        bboxes = [bbox for bbox in model_annotations.bboxes]
        categories = [cat for cat in model_annotations.categories]

        category_insert_query_string = f"""
            INSERT INTO model_image_category(category)
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
            INSERT INTO model_image_bbox(image_id, model_id, category_id, bbox_json)
            VALUES ($1, $2, $3, $4)
            RETURNING id;
        """
        
        result = [
            await self.connection.fetchval(
                image_bbox_insert_query_string,
                image_id,
                model_id,
                category_id,
                json.dumps(bboxes[i]),
            )
            for i, category_id in enumerate(category_ids)
        ]

    async def create_model_image_heatmap(
        self,
        image_id: int,
        model_name: str,
        result_path: str,
    ) -> None:
        """Create image model based features"""

        # First need model id
        model_get_query_string = f"""
            SELECT m.id
            FROM model m
            WHERE m.name = $1;
        """

        model_id = await self.connection.fetchval(
            model_get_query_string,
            model_name,
        )

        image_bbox_insert_query_string = f"""
            INSERT INTO model_image_heatmap(image_id, model_id, result_path)
            VALUES ($1, $2, $3)
            RETURNING (image_id, model_id);
        """
        
        result = await self.connection.fetchval(
            image_bbox_insert_query_string,
            image_id,
            model_id,
            result_path,
        )

    async def create_model_image_activations(
        self,
        image_id: int,
        model_name: str,
        result_path: str,
    ) -> None:
        """Create image model based features"""

        # First need model id
        model_get_query_string = f"""
            SELECT m.id
            FROM model m
            WHERE m.name = $1;
        """

        model_id = await self.connection.fetchval(
            model_get_query_string,
            model_name,
        )

        image_bbox_insert_query_string = f"""
            INSERT INTO model_image_activations(image_id, model_id, result_path)
            VALUES ($1, $2, $3)
            RETURNING (image_id, model_id);
        """
        
        result = await self.connection.fetchval(
            image_bbox_insert_query_string,
            image_id,
            model_id,
            result_path,
        )
  