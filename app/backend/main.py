import os, json
from abc import ABC, abstractmethod

@abstractmethod
class DataPreparation(ABC):
    def _load_img_bbox(self, img_path: str, img_dir, annotations_dir: str):
        pass


class JsonDataPreparation(DataPreparation):
    def _load_img_bbox(self, img_path: str, img_dir, annotations_dir: str):
        # Get relative image path
        rel_img_path = os.path.relpath(img_path, img_dir)

        # Compute the path to the annotations directory
        annotations_img_path = os.path.abspath(os.path.join(annotations_dir, rel_img_path))
        annotations_img_path = os.path.splitext(annotations_img_path)[0] + ".json"

        # Load the annotations data
        with open(annotations_img_path, "r") as annotations_file:
            img_data = json.load(annotations_file)

        # Retrieve the bounding box data
        bbox_data = img_data['bbox']

        return bbox_data
