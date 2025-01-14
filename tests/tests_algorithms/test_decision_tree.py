import os
import tempfile
import unittest

from numpy.testing import assert_almost_equal
from sklearn import datasets

from supervised.algorithms.decision_tree import (
    DecisionTreeRegressorAlgorithm,
)
from supervised.utils.metric import Metric


class DecisionTreeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.X, cls.y = datasets.make_regression(
            n_samples=100,
            n_features=5,
            n_informative=4,
            n_targets=1,
            shuffle=False,
            random_state=0,
        )

    def test_reproduce_fit_regression(self):
        metric = Metric({"name": "rmse"})
        params = {"max_depth": 1, "seed": 1, "ml_task": "regression"}
        prev_loss = None
        for _ in range(3):
            model = DecisionTreeRegressorAlgorithm(params)
            model.fit(self.X, self.y)
            y_predicted = model.predict(self.X)
            loss = metric(self.y, y_predicted)
            if prev_loss is not None:
                assert_almost_equal(prev_loss, loss)
            prev_loss = loss

    def test_save_and_load(self):
        metric = Metric({"name": "rmse"})
        dt = DecisionTreeRegressorAlgorithm({"ml_task": "regression"})
        dt.fit(self.X, self.y)
        y_predicted = dt.predict(self.X)
        loss = metric(self.y, y_predicted)

        filename = os.path.join(tempfile.gettempdir(), os.urandom(12).hex())

        dt.save(filename)
        dt2 = DecisionTreeRegressorAlgorithm({"ml_task": "regression"})
        dt2.load(filename)

        y_predicted = dt2.predict(self.X)
        loss2 = metric(self.y, y_predicted)
        assert_almost_equal(loss, loss2)

        # Finished with temp file, delete it
        os.remove(filename)

    def test_is_fitted(self):
        params = {"max_depth": 1, "seed": 1, "ml_task": "regression"}
        model = DecisionTreeRegressorAlgorithm(params)
        self.assertFalse(model.is_fitted())
        model.fit(self.X, self.y)
        self.assertTrue(model.is_fitted())
