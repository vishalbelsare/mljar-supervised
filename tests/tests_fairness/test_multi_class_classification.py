import shutil
import unittest

import numpy as np
import pandas as pd

from supervised import AutoML


class FairnessInMultiClassClassificationTest(unittest.TestCase):
    automl_dir = "automl_fairness_testing"

    def tearDown(self):
        shutil.rmtree(self.automl_dir, ignore_errors=True)

    def test_init(self):
        X = np.random.uniform(size=(30, 2))
        y = np.array(["A", "B", "C"] * 10)
        S = pd.DataFrame({"sensitive": ["D", "E"] * 15})

        automl = AutoML(
            results_path=self.automl_dir,
            model_time_limit=10,
            algorithms=["Xgboost"],
            explain_level=0,
            train_ensemble=False,
            stack_models=False,
            validation_strategy={"validation_type": "split"},
            start_random_models=1,
        )

        automl.fit(X, y, sensitive_features=S)

        self.assertGreater(len(automl._models), 0)

        sensitive_features_names = automl._models[0].get_sensitive_features_names()
        self.assertEqual(len(sensitive_features_names), 3)

        self.assertTrue("sensitive__A" in sensitive_features_names)
        self.assertTrue("sensitive__B" in sensitive_features_names)
        self.assertTrue("sensitive__C" in sensitive_features_names)

        self.assertTrue(
            automl._models[0].get_fairness_metric("sensitive__A") is not None
        )
        self.assertTrue(
            automl._models[0].get_fairness_metric("sensitive__B") is not None
        )
        self.assertTrue(
            automl._models[0].get_fairness_metric("sensitive__C") is not None
        )

        self.assertTrue(len(automl._models[0].get_fairness_optimization()) > 1)
        self.assertTrue(automl._models[0].get_worst_fairness() is not None)
        self.assertTrue(automl._models[0].get_best_fairness() is not None)
