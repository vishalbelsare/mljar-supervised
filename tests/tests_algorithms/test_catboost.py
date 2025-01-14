import os
import tempfile
import unittest

import pandas as pd
from numpy.testing import assert_almost_equal
from sklearn import datasets

from supervised.algorithms.catboost import CatBoostAlgorithm, additional
from supervised.utils.metric import Metric

additional["max_rounds"] = 1


class CatBoostRegressorAlgorithmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.X, cls.y = datasets.make_regression(
            n_samples=100, n_features=5, n_informative=4, shuffle=False, random_state=0
        )
        cls.X = pd.DataFrame(cls.X, columns=[f"f_{i}" for i in range(cls.X.shape[1])])
        cls.params = {
            "learning_rate": 0.1,
            "depth": 4,
            "rsm": 0.5,
            "l2_leaf_reg": 1,
            "seed": 1,
            "ml_task": "regression",
            "loss_function": "RMSE",
            "eval_metric": "RMSE",
        }

    def test_reproduce_fit(self):
        metric = Metric({"name": "mse"})
        prev_loss = None
        for _ in range(2):
            model = CatBoostAlgorithm(self.params)
            model.fit(self.X, self.y)
            y_predicted = model.predict(self.X)
            loss = metric(self.y, y_predicted)
            if prev_loss is not None:
                assert_almost_equal(prev_loss, loss, decimal=3)
            prev_loss = loss

    def test_get_metric_name(self):
        model = CatBoostAlgorithm(self.params)
        self.assertEqual(model.get_metric_name(), "rmse")


class CatBoostAlgorithmTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.X, cls.y = datasets.make_classification(
            n_samples=100,
            n_features=5,
            n_informative=4,
            n_redundant=1,
            n_classes=2,
            n_clusters_per_class=3,
            n_repeated=0,
            shuffle=False,
            random_state=0,
        )
        cls.X = pd.DataFrame(cls.X, columns=[f"f_{i}" for i in range(cls.X.shape[1])])
        cls.params = {
            "learning_rate": 0.1,
            "depth": 4,
            "rsm": 0.5,
            "l2_leaf_reg": 1,
            "seed": 1,
            "ml_task": "binary_classification",
            "loss_function": "Logloss",
            "eval_metric": "Logloss",
        }

    def test_reproduce_fit(self):
        metric = Metric({"name": "logloss"})
        prev_loss = None
        for _ in range(2):
            model = CatBoostAlgorithm(self.params)
            model.fit(self.X, self.y)
            y_predicted = model.predict(self.X)
            loss = metric(self.y, y_predicted)
            if prev_loss is not None:
                assert_almost_equal(prev_loss, loss, decimal=3)
            prev_loss = loss

    def test_fit_predict(self):
        metric = Metric({"name": "logloss"})
        loss_prev = None
        for _ in range(2):
            cat = CatBoostAlgorithm(self.params)
            cat.fit(self.X, self.y)
            y_predicted = cat.predict(self.X)
            loss = metric(self.y, y_predicted)
            if loss_prev is not None:
                assert_almost_equal(loss, loss_prev, decimal=3)
            loss_prev = loss

    def test_copy(self):
        # train model #1
        metric = Metric({"name": "logloss"})
        cat = CatBoostAlgorithm(self.params)
        cat.fit(self.X, self.y)
        y_predicted = cat.predict(self.X)
        loss = metric(self.y, y_predicted)
        # create model #2
        cat2 = CatBoostAlgorithm(self.params)
        # model #2 is initialized in constructor
        self.assertTrue(cat2.model is not None)
        # do a copy and use it for predictions
        cat2 = cat.copy()
        self.assertEqual(type(cat), type(cat2))
        y_predicted = cat2.predict(self.X)
        loss2 = metric(self.y, y_predicted)
        self.assertEqual(loss, loss2)

    def test_save_and_load(self):
        metric = Metric({"name": "logloss"})
        cat = CatBoostAlgorithm(self.params)
        cat.fit(self.X, self.y)
        y_predicted = cat.predict(self.X)
        loss = metric(self.y, y_predicted)

        filename = os.path.join(tempfile.gettempdir(), os.urandom(12).hex())

        cat.save(filename)
        cat2 = CatBoostAlgorithm(self.params)
        self.assertTrue(cat.uid != cat2.uid)
        self.assertTrue(cat2.model is not None)
        cat2.load(filename)
        # Finished with the file, delete it
        os.remove(filename)

        y_predicted = cat2.predict(self.X)
        loss2 = metric(self.y, y_predicted)
        assert_almost_equal(loss, loss2, decimal=3)

    def test_get_metric_name(self):
        model = CatBoostAlgorithm(self.params)
        self.assertEqual(model.get_metric_name(), "logloss")
        params = dict(self.params)
        params["loss_function"] = "MultiClass"
        params["eval_metric"] = "MultiClass"
        model = CatBoostAlgorithm(params)
        self.assertEqual(model.get_metric_name(), "logloss")

    def test_is_fitted(self):
        cat = CatBoostAlgorithm(self.params)
        self.assertFalse(cat.is_fitted())
        cat.fit(self.X, self.y)
        self.assertTrue(cat.is_fitted())
