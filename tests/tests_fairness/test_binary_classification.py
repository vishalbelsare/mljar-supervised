import shutil
import unittest

import numpy as np
import pandas as pd

from supervised import AutoML


class FairnessInBinaryClassificationTest(unittest.TestCase):
    automl_dir = "automl_fairness_testing"

    def tearDown(self):
        shutil.rmtree(self.automl_dir, ignore_errors=True)

    def test_init(self):
        X = np.random.uniform(size=(30, 2))
        y = np.random.randint(0, 2, size=(30,))
        S = pd.DataFrame({"sensitive": ["A", "B"] * 15})

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
        self.assertEqual(len(sensitive_features_names), 1)
        self.assertTrue("sensitive" in sensitive_features_names)

        self.assertTrue(automl._models[0].get_fairness_metric("sensitive") is not None)
        self.assertTrue(len(automl._models[0].get_fairness_optimization()) > 1)
        self.assertTrue(automl._models[0].get_worst_fairness() is not None)
        self.assertTrue(automl._models[0].get_best_fairness() is not None)

    def test_arguments(self):
        X = np.random.uniform(size=(30, 2))
        y = np.random.randint(0, 2, size=(30,))
        S = pd.DataFrame({"sensitive": ["A", "B"] * 15})

        automl = AutoML(
            results_path=self.automl_dir,
            model_time_limit=10,
            algorithms=["Xgboost"],
            privileged_groups=[{"sensitive": "A"}],
            underprivileged_groups=[{"sensitive": "B"}],
            fairness_metric="demographic_parity_ratio",
            fairness_threshold=0.2,
            explain_level=0,
            train_ensemble=False,
            stack_models=False,
            validation_strategy={"validation_type": "split"},
            start_random_models=1,
        )

        automl.fit(X, y, sensitive_features=S)

        self.assertGreater(len(automl._models), 0)

    def test_wrong_metric_name(self):
        X = np.random.uniform(size=(30, 2))
        y = np.random.randint(0, 2, size=(30,))
        S = pd.DataFrame({"sensitive": ["A", "B"] * 15})

        with self.assertRaises(ValueError) as context:
            automl = AutoML(
                results_path=self.automl_dir,
                model_time_limit=10,
                algorithms=["Xgboost"],
                privileged_groups=[{"sensitive": "A"}],
                underprivileged_groups=[{"sensitive": "B"}],
                fairness_metric="wrong_metric_name",
                fairness_threshold=0.2,
                explain_level=0,
                train_ensemble=False,
                stack_models=False,
                validation_strategy={"validation_type": "split"},
                start_random_models=1,
            )
            automl.fit(X, y, sensitive_features=S)
        self.assertTrue("is not allowed" in str(context.exception))

    def test_two_sensitive_features(self):
        X = np.random.uniform(size=(30, 2))
        y = np.random.randint(0, 2, size=(30,))
        S = pd.DataFrame(
            {
                "sensitive_1": ["White", "Black"] * 15,
                "sensitive_2": ["Male", "Female"] * 15,
            }
        )

        automl = AutoML(
            results_path=self.automl_dir,
            model_time_limit=10,
            algorithms=["Xgboost"],
            explain_level=0,
            train_ensemble=False,
            stack_models=False,
            start_random_models=1,
        )

        automl.fit(X, y, sensitive_features=S)

        self.assertGreater(len(automl._models), 0)

        sensitive_features_names = automl._models[0].get_sensitive_features_names()
        self.assertEqual(len(sensitive_features_names), 2)
