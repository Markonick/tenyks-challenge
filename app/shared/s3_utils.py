import json
import os
import dataclasses
from typing import Any     
from aiobotocore.session import get_session 
from dataclasses import dataclass
from io import BytesIO

@dataclass
class AwsConfig:
    endpoint_url: str
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str


@dataclass
class DownloadedFile:
    name: str
    content: BytesIO


async def s3_get_file_type(files_path: str, aws_config: AwsConfig) -> str:
    bucket = os.environ.get("AWS_BUCKET")
    session = get_session()
    async with session.create_client("s3", **dataclasses.asdict(aws_config)) as s3:
        paginator = s3.get_paginator("list_objects")
        async for page in paginator.paginate(Bucket=bucket, Prefix=files_path):
            return page.get("Contents", [])[0]["Key"].split(".")[-1]

async def s3_get_file_count(files_path: str, file_type_filter: str, aws_config: AwsConfig) -> str:
    totalCount = 0
  
    bucket = os.environ.get("AWS_BUCKET")
    session = get_session()
    async with session.create_client("s3", **dataclasses.asdict(aws_config)) as s3:
        totalCount = 0 
        paginator = s3.get_paginator("list_objects")
        async for page in paginator.paginate(Bucket=bucket, Prefix=files_path): 
            for c in page.get("Contents", []):
                if c["Key"].split(".")[-1] == file_type_filter:
                    totalCount += 1
        
    return totalCount

async def s3_download_files(files_path: str, file_type_filter: str, aws_config: AwsConfig) -> str: 
    bucket = os.environ.get("AWS_BUCKET")
    # keys = [key async for key in self._s3_reader(files_path=files_path, file_type_filter=file_type_filter)]

    session = get_session()
    async with session.create_client("s3", **dataclasses.asdict(aws_config)) as s3:
        
        paginator = s3.get_paginator("list_objects")
        async for page in paginator.paginate(Bucket=bucket, Prefix=files_path): 
            for c in page.get('Contents', []):
                response = await s3.get_object(Bucket=bucket, Key=c["Key"])
                # this will ensure the connection is correctly re-used/closed
                async with response["Body"] as stream: 
                    content = (await stream.read()).decode("utf-8")
                    content = json.loads(content)  
                    yield DownloadedFile(
                        name=c["Key"].split("/")[-1],
                        content=content
                    )


async def s3_download_file(file_path: str, aws_config: AwsConfig) -> str: 
    bucket = os.environ.get("AWS_BUCKET")
    # keys = [key async for key in self._s3_reader(files_path=files_path, file_type_filter=file_type_filter)]

    session = get_session()
    async with session.create_client("s3", **dataclasses.asdict(aws_config)) as s3:  
        s3_object = await s3.get_object(Bucket=bucket, Key=file_path)
        image_dl = await s3_object['Body'].read()

        return DownloadedFile(
                name=file_path.split("/")[-1],
                content=BytesIO(image_dl)
            )