from PIL import Image
import numpy as np
import random

class DummyModel:
    def __init__(self, model_id):
        self.model_id = model_id
        # First model is trained on both datasets
        # Second model is trained only on the terminator dataset
        if model_id == 0:
            self.model_datasets = ['human_dataset', 'terminator_dataset']
            self.model_name = 'Hybrid Model'
            self.layer_sizes = [(100, 200), (64)]
        elif model_id == 1:
            self.model_datasets = ['terminator_dataset']
            self.model_name = 'Terminator Model'
            self.layer_sizes = [(200, 100), (64), (32)]
        else:
            raise ValueError("Unrecognized model ID...")

    def get_img_heatmap(self, img_path):
        # Dummy heatmap generation
        # A heatmap is represented as a numpy array of shape (H * W), where H and W are the image height and width
        # The values represent the heatmap intensities
        print(img_path)
        print(img_path)
        print(img_path)
        print(img_path)
        print(img_path)
        np_img = np.asarray(Image.open(img_path))
        h, w = np_img.shape[0], np_img.shape[1]
        # Values are generated randomly for the dummy models
        heatmap = np.random.uniform(0, 1, size=(h, w))
        return heatmap


    def get_img_activations(self, img_path):
        # Dummy activation generation
        # In this case, we generate activations from all model layers
        layer_activations = []
        for layer_size in self.layer_sizes:
            # In this case, the activation values are generated randomly
            layer_activation = np.random.uniform(0, 1, size=layer_size)
            layer_activations.append(layer_activation)
        return layer_activations


    def get_model_prediction(self, img_path):
        # Dummy bounding box predictions
        # In this case, the model randomly predicts a random number of bounding boxes

        # Randomly determine how many bounding boxes a model predicts (in this case - between 0 and 10)
        n_bboxes =  random.randint(0, 10)
        bboxes = []
        category_ids = []
        for bbox_id in range(n_bboxes):
            # Randomly generate a bbox category ID
            category_id = random.randint(0, 3)
            category_ids.append(category_id)

            # Randomly generate bbox coordinates
            min_x, min_y = random.randint(0, 40), random.randint(0, 40)
            bbox_h, bbox_w = random.randint(5, 40), random.randint(5, 40)
            bbox= [min_x, min_y, min_x+bbox_h, min_y+bbox_w]
            bboxes.append(bbox)

        target = {}
        target['bbox'] = bboxes
        target['category_id'] = category_ids
        return target



def get_models():
    # Generate two sample models for this exercise
    model_ids = [0, 1]
    dummy_models = []
    for model_id in model_ids:
        dummy_model = DummyModel(model_id)
        dummy_models.append(dummy_model)

    return dummy_models
