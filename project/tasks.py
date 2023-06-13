import json
import numpy as np
import pandas as pd
import pickle
import re
from sklearn.ensemble import RandomForestClassifier as rfc
from celery import Task
from worker import worker

from data_prep import parse_request, feature_engineering, get_result

class PredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.
    """
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            self.model = pickle.load(open("ml_models/rfc_42.pickle", "rb"))
        
        return self.run(*args, **kwargs)


@worker.task(name="create_task",
             bind=True,
             base=PredictTask,
             ignore_result=False)
def create_task(self, data):
    data = parse_request(data)
    data = feature_engineering(data)
    result = get_result(data, self.model)

    return result

