import json
from typing import List
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, list):
            print("COUGHT!!!!!")
            print("COUGHT!!!!!")
            print("COUGHT!!!!!")
            print("COUGHT!!!!!")
            print("COUGHT!!!!!")
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)