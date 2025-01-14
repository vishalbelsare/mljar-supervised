import json
import os
import shutil
import unittest

import joblib
import numpy as np

from supervised import AutoML
from supervised.exceptions import AutoMLException


class TestJoblibVersion(unittest.TestCase):
    automl_dir = "TestJoblibVersion"

    def tearDown(self):
        shutil.rmtree(self.automl_dir, ignore_errors=True)

    def test_joblib_good_version(self):
        X = np.random.uniform(size=(60, 2))
        y = np.random.randint(0, 2, size=(60,))

        automl = AutoML(
            results_path=self.automl_dir,
            model_time_limit=10,
            algorithms=["Xgboost"],
            mode="Explain",
            explain_level=0,
            start_random_models=1,
            hill_climbing_steps=0,
            top_models_to_improve=0,
            kmeans_features=False,
            golden_features=False,
            features_selection=False,
            boost_on_errors=False,
        )
        automl.fit(X, y)

        # Test if joblib is in json
        json_path = os.path.join(self.automl_dir, "1_Default_Xgboost", "framework.json")

        with open(json_path) as file:
            frame = json.load(file)

        json_version = frame["joblib_version"]
        expected_result = joblib.__version__

        self.assertEqual(expected_result, json_version)

    def test_joblib_wrong_version(self):
        X = np.random.uniform(size=(60, 2))
        y = np.random.randint(0, 2, size=(60,))

        automl = AutoML(
            results_path=self.automl_dir,
            model_time_limit=10,
            algorithms=["Xgboost"],
            mode="Explain",
            explain_level=0,
            start_random_models=1,
            hill_climbing_steps=0,
            top_models_to_improve=0,
            kmeans_features=False,
            golden_features=False,
            features_selection=False,
            boost_on_errors=False,
        )
        automl.fit(X, y)

        json_path = os.path.join(self.automl_dir, "1_Default_Xgboost", "framework.json")

        with open(json_path) as file:
            frame = json.load(file)

        # Injection of wrong joblib version
        frame["joblib_version"] = "0.2.0"

        with open(json_path, "w") as file:
            json.dump(frame, file)

        with self.assertRaises(AutoMLException):
            automl_2 = AutoML(results_path=self.automl_dir)
            automl_2.predict(X)


if __name__ == "__main__":
    unittest.main()
