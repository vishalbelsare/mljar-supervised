import os
import tempfile
import unittest

from numpy.testing import assert_almost_equal
from sklearn import datasets

from supervised.algorithms.baseline import (
    BaselineClassifierAlgorithm,
    BaselineRegressorAlgorithm,
)
from supervised.utils.metric import Metric


class BaselineTest(unittest.TestCase):
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
        prev_loss = None
        for _ in range(3):
            model = BaselineRegressorAlgorithm({"ml_task": "regression"})
            model.fit(self.X, self.y)
            y_predicted = model.predict(self.X)
            loss = metric(self.y, y_predicted)
            if prev_loss is not None:
                assert_almost_equal(prev_loss, loss)
            prev_loss = loss

    def test_reproduce_fit_bin_class(self):
        X, y = datasets.make_classification(
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
        metric = Metric({"name": "logloss"})
        prev_loss = None
        for _ in range(3):
            model = BaselineClassifierAlgorithm({"ml_task": "binary_classification"})
            model.fit(X, y)
            y_predicted = model.predict(X)
            loss = metric(y, y_predicted)
            if prev_loss is not None:
                assert_almost_equal(prev_loss, loss)
            prev_loss = loss

    def test_save_and_load(self):
        metric = Metric({"name": "rmse"})
        dt = BaselineRegressorAlgorithm({"ml_task": "regression"})
        dt.fit(self.X, self.y)
        y_predicted = dt.predict(self.X)
        loss = metric(self.y, y_predicted)

        filename = os.path.join(tempfile.gettempdir(), os.urandom(12).hex())

        dt.save(filename)
        dt2 = BaselineRegressorAlgorithm({"ml_task": "regression"})
        dt2.load(filename)
        # Finished with the file, delete it
        os.remove(filename)

        y_predicted = dt2.predict(self.X)
        loss2 = metric(self.y, y_predicted)
        assert_almost_equal(loss, loss2)

    def test_is_fitted(self):
        model = BaselineRegressorAlgorithm({"ml_task": "regression"})
        self.assertFalse(model.is_fitted())
        model.fit(self.X, self.y)
        self.assertTrue(model.is_fitted())
