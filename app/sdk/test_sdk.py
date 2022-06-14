from dataclasses import dataclass
import dataclasses
import json
import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient
from fastapi import status

from .main import TenyksSDK

@dataclass
class DatasetTestRequest:   
    name: str
    dataset_path: str
    images_path: str


@pytest.fixture
def dataset_1():
    return DatasetTestRequest(
        name="human_dataset",
        dataset_path="human_dataset",
        images_path=f"human_dataset/images",
    )
    
@pytest.fixture
def tce():
    return TenyksSDK()

def test_we_can_save_a_dataset_succesfully(tce, dataset_1):
    tc = TenyksSDK()
    result = tc.save_dataset(dataclasses.asdict(**dataset_1))
    print('Hello...')
    assert result == f"xx"
