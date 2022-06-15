from dataclasses import dataclass
import dataclasses
import json
import pytest
from httpx import AsyncClient
from starlette.testclient import TestClient
from fastapi import status

from sdk.main import TenyksSDK

@dataclass
class DatasetTestRequest:
    name: str
    dataset_path: str
    images_path: str


def base_dataset_input(n):
    return DatasetTestRequest(
        name=f"human_dataset{n}",
        dataset_path=f"human_dataset{n}",
        images_path=f"human_dataset{n}/images",
    )
 
@pytest.fixture
def dataset_input(n):
    return base_dataset_input(n=n)

@pytest.fixture
def tc():
    return TenyksSDK()

@pytest.mark.parametrize('n', [""],)
def test_we_can_save_a_dataset_succesfully(tc, dataset_input):
    result = tc.save_dataset(**dataclasses.asdict(dataset_input))
    assert result.status_code == 200
